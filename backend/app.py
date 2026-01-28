from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from io import BytesIO
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from services.extract_text import load_and_clean
from services.extract_fields import extract_fields, infer_jd_skills, infer_jd_title, infer_req_years
from services.vector_store import ResumeIndex
from services.scorer import score_and_rank
from services.mistral_service import extract_fields_with_mistral, analyze_with_prompt
from services.resume_analyzer import analyze_and_suggest_improvements, compare_with_references, analyze_resume_for_job
from services.intelligent_extractor import extract_jd_requirements, extract_resume_qualifications, intelligent_gap_analysis
from services.rag_engine import rag_search_resumes, rag_enhance_suggestions
from services.grounded_rag import grounded_search_insights, grounded_rag_analysis
from services.resume_pdf_generator import generate_professional_resume_pdf, generate_simple_pdf_from_text

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "../data/uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

index = ResumeIndex(persist_dir=os.getenv("CHROMA_PERSIST_DIR", "../data/chroma"))

@app.get("/api/health")
def health():
    return {"ok": True, "vector_db_count": index.col.count()}

@app.post("/api/analyze")
def analyze():
    data = request.get_json(force=True)
    jd_text = (data.get("jd_text") or "").strip()
    use_llm = bool(data.get("use_llm", False))
    paths = data.get("server_resume_paths") or []

    if not jd_text:
        return jsonify({"error":"jd_text is required"}), 400

    candidates = []
    for p in paths:
        text = load_and_clean(p)
        fields = extract_fields(text, use_llm=use_llm)
        rid = index.upsert_resume(resume_path=p, text=text, metadata={
            "filename": p.split("/")[-1],
            "skills": fields.get("skills", []),
            "titles": fields.get("titles", []),
            "years": fields.get("years_exp", 0)
        })
        candidates.append({"id": rid, "path": p, "text": text, "fields": fields})

    if not candidates:
        hits = index.query_similar(jd_text, top_k=50)
        ids = hits.get("ids", [[]])[0]
        docs = hits.get("documents", [[]])[0]
        metas = hits.get("metadatas", [[]])[0]
        for rid, text, meta in zip(ids, docs, metas):
            # Parse comma-separated strings back to lists
            skills_str = meta.get("skills", "")
            titles_str = meta.get("titles", "")
            skills = [s.strip() for s in skills_str.split(",") if s.strip()] if skills_str else []
            titles = [t.strip() for t in titles_str.split(",") if t.strip()] if titles_str else []
            
            candidates.append({
                "id": rid,
                "path": meta.get("filename", rid),
                "text": text,
                "fields": {"skills": skills, "titles": titles, "years_exp": meta.get("years", 0)}
            })

    jd_info = {
        "skills": infer_jd_skills(jd_text),
        "title": infer_jd_title(jd_text),
        "years": infer_req_years(jd_text) or 0
    }

    results = score_and_rank(jd_text, jd_info, candidates)
    return jsonify({"top_k": results[:10]})

@app.post("/api/analyze-resume")
def analyze_user_resume():
    """Analyze user's resume and provide improvement suggestions."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Extract text
            text = load_and_clean(filepath)
            
            # Get AI analysis and suggestions
            analysis = analyze_and_suggest_improvements(text)
            
            # Extract fields for display
            fields = extract_fields(text, use_llm=False)
            
            return jsonify({
                "success": True,
                "filename": filename,
                "resume_text": text[:1000] + "..." if len(text) > 1000 else text,
                "resume_text_full": text,
                "score": analysis["score"],
                "analysis": analysis["analysis"],
                "fields": fields,
                "message": "Resume analyzed successfully",
                "api_usage": analysis.get("api_usage")
            })
        except Exception as e:
            return jsonify({"error": f"Failed to analyze resume: {str(e)}"}), 500
    
    return jsonify({"error": "Invalid file type. Allowed: pdf, docx, txt"}), 400


@app.post("/api/improve-with-jd")
def improve_resume_with_jd():
    """Analyze user's resume against a job description with reference resume insights."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    jd_text = request.form.get('jd_text', '').strip()
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not jd_text:
        return jsonify({"error": "Job description is required"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Extract resume text
            resume_text = load_and_clean(filepath)
            
            # Check if enhanced intelligent extraction is requested
            use_intelligent = request.form.get('use_intelligent', 'true').lower() == 'true'
            
            # Extract fields (basic fallback)
            fields = extract_fields(resume_text, use_llm=False)
            
            # Find top matching reference resumes based on JD
            hits = index.query_similar(jd_text, top_k=5)
            
            # Build reference resumes list
            references = []
            ids = hits.get("ids", [[]])[0]
            docs = hits.get("documents", [[]])[0]
            metas = hits.get("metadatas", [[]])[0]
            distances = hits.get("distances", [[]])[0]
            
            for rid, text, meta, dist in zip(ids, docs, metas, distances):
                # Parse comma-separated strings back to lists
                skills_str = meta.get("skills", "")
                titles_str = meta.get("titles", "")
                skills = [s.strip() for s in skills_str.split(",") if s.strip()] if skills_str else []
                titles = [t.strip() for t in titles_str.split(",") if t.strip()] if titles_str else []
                
                references.append({
                    "id": rid,
                    "text": text,
                    "metadata": {
                        "category": meta.get("category", "N/A"),
                        "skills": skills,
                        "titles": titles,
                        "years": meta.get("years", 0),
                        "filename": meta.get("filename", rid)
                    },
                    "similarity_score": round((1 - dist) * 100, 1)
                })
            
            # Use grounded RAG analysis for evidence-based evaluation
            grounded_analysis = grounded_rag_analysis(jd_text, resume_text, references)
            
            # Calculate match score from evaluation
            match_eval = grounded_analysis.get("match_evaluation", [])
            met_count = sum(1 for e in match_eval if e["status"] == "met")
            total_count = len(match_eval) if match_eval else 1
            score = int((met_count / total_count) * 100)
            
            # Also run old analysis for suggestions (backward compat)
            old_analysis = analyze_resume_for_job(resume_text, jd_text, references)
            
            response_data = {
                "success": True,
                "filename": filename,
                "filepath": filepath,
                "resume_text": resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text,
                "resume_text_full": resume_text,
                "jd_text": jd_text,
                "score": score,
                "analysis": old_analysis["analysis"],
                "suggestions": old_analysis.get("suggestions", []),
                "fields": fields,
                "reference_resumes": references,
                "grounded_analysis": grounded_analysis,
                "message": "Resume analyzed with evidence-grounded RAG",
                "api_usage": None
            }
            
            return jsonify(response_data)
        except Exception as e:
            return jsonify({"error": f"Failed to analyze resume: {str(e)}"}), 500
    
    return jsonify({"error": "Invalid file type. Allowed: pdf, docx, txt"}), 400


@app.post("/api/find-references")
def find_reference_resumes():
    """Find similar reference resumes from database based on user's resume or prompt."""
    data = request.get_json(force=True)
    query_text = (data.get("query") or "").strip()  # Can be resume text or search prompt
    top_k = int(data.get("top_k", 10))
    include_comparison = bool(data.get("include_comparison", False))
    user_resume_text = data.get("user_resume_text", "")  # Optional for comparison
    
    if not query_text:
        return jsonify({"error": "query is required"}), 400
    
    try:
        # Search vector database
        hits = index.query_similar(query_text, top_k=top_k)
        
        # Build reference resumes list
        references = []
        ids = hits.get("ids", [[]])[0]
        docs = hits.get("documents", [[]])[0]
        metas = hits.get("metadatas", [[]])[0]
        distances = hits.get("distances", [[]])[0]
        
        for rid, text, meta, dist in zip(ids, docs, metas, distances):
            # Parse comma-separated strings back to lists
            skills_str = meta.get("skills", "")
            titles_str = meta.get("titles", "")
            skills = [s.strip() for s in skills_str.split(",") if s.strip()] if skills_str else []
            titles = [t.strip() for t in titles_str.split(",") if t.strip()] if titles_str else []
            
            references.append({
                "id": rid,
                "text": text,
                "metadata": {
                    "category": meta.get("category", "N/A"),
                    "skills": skills,
                    "titles": titles,
                    "years": meta.get("years", 0),
                    "filename": meta.get("filename", rid)
                },
                "similarity_score": round((1 - dist) * 100, 1)  # Convert to percentage
            })
        
        result = {
            "query": query_text[:100] + "..." if len(query_text) > 100 else query_text,
            "references": references
        }
        
        # Add comparison analysis if requested and user resume provided
        if include_comparison and user_resume_text and references:
            comparison = compare_with_references(user_resume_text, references)
            result["comparison_analysis"] = comparison.get("comparison")
            result["api_usage"] = comparison.get("api_usage")
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Search failed: {str(e)}"}), 500


@app.post("/api/upload")
def upload_resume():
    """Upload a resume file and add it to the vector database."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Extract text
            text = load_and_clean(filepath)
            
            # Extract fields
            fields = extract_fields(text, use_llm=False)
            
            # Add to vector store (ChromaDB only accepts str, int, float, bool)
            skills_list = fields.get("skills", [])
            titles_list = fields.get("titles", [])
            metadata = {
                "filename": filename,
                "category": "uploaded",
                "skills": ",".join(skills_list) if isinstance(skills_list, list) else str(skills_list),
                "titles": ",".join(titles_list) if isinstance(titles_list, list) else str(titles_list),
                "years": int(fields.get("years_exp", 0)),
                "name": str(fields.get("name", ""))
            }
            
            rid = index.upsert_resume(filepath, text, metadata)
            
            return jsonify({
                "success": True,
                "resume_id": rid,
                "filename": filename,
                "fields": fields,
                "message": "Resume uploaded and indexed successfully"
            })
        except Exception as e:
            return jsonify({"error": f"Failed to process file: {str(e)}"}), 500
    
    return jsonify({"error": "Invalid file type. Allowed: pdf, docx, txt"}), 400


@app.post("/api/search-resumes")
def search_resumes_with_rag():
    """Evidence-grounded resume search: Find top resumes with strict citation."""
    data = request.get_json(force=True)
    jd_text = (data.get("jd_text") or "").strip()
    top_k = int(data.get("top_k", 10))
    
    if not jd_text:
        return jsonify({"error": "jd_text is required"}), 400
    
    try:
        # Step 1: Retrieve top resumes from vector DB
        hits = index.query_similar(jd_text, top_k=top_k)
        
        # Build resumes list
        resumes = []
        ids = hits.get("ids", [[]])[0]
        docs = hits.get("documents", [[]])[0]
        metas = hits.get("metadatas", [[]])[0]
        distances = hits.get("distances", [[]])[0]
        
        for rid, text, meta, dist in zip(ids, docs, metas, distances):
            skills_str = meta.get("skills", "")
            titles_str = meta.get("titles", "")
            skills = [s.strip() for s in skills_str.split(",") if s.strip()] if skills_str else []
            titles = [t.strip() for t in titles_str.split(",") if t.strip()] if titles_str else []
            
            resumes.append({
                "id": rid,
                "text": text,
                "metadata": {
                    "category": meta.get("category", "N/A"),
                    "skills": skills,
                    "titles": titles,
                    "years": meta.get("years", 0),
                    "filename": meta.get("filename", rid)
                },
                "similarity_score": round((1 - dist) * 100, 1)
            })
        
        # Step 2: Generate grounded insights (no hallucination)
        insights = grounded_search_insights(jd_text, resumes)
        
        return jsonify({
            "resumes": resumes,
            "grounded_insights": insights,
            "query_jd": jd_text[:200] + "..." if len(jd_text) > 200 else jd_text
        })
    except Exception as e:
        return jsonify({"error": f"Search failed: {str(e)}"}), 500


@app.post("/api/query")
def query_with_prompt():
    """Query the resume database with a natural language prompt."""
    data = request.get_json(force=True)
    prompt = (data.get("prompt") or "").strip()
    top_k = int(data.get("top_k", 20))
    use_mistral = bool(data.get("use_mistral", True))
    
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400
    
    try:
        # Search vector database
        hits = index.query_similar(prompt, top_k=top_k)
        
        # Build contexts
        contexts = []
        ids = hits.get("ids", [[]])[0]
        docs = hits.get("documents", [[]])[0]
        metas = hits.get("metadatas", [[]])[0]
        distances = hits.get("distances", [[]])[0]
        
        for rid, text, meta, dist in zip(ids, docs, metas, distances):
            # Parse comma-separated strings back to lists
            skills_str = meta.get("skills", "")
            titles_str = meta.get("titles", "")
            meta["skills"] = [s.strip() for s in skills_str.split(",") if s.strip()] if skills_str else []
            meta["titles"] = [t.strip() for t in titles_str.split(",") if t.strip()] if titles_str else []
            
            contexts.append({
                "id": rid,
                "text": text,
                "metadata": meta,
                "score": 1 - dist  # Convert distance to similarity
            })
        
        # Use Mistral to analyze if requested
        if use_mistral and contexts:
            analysis = analyze_with_prompt(prompt, contexts)
            
            return jsonify({
                "prompt": prompt,
                "analysis": analysis["answer"],
                "model": analysis["model"],
                "api_usage": analysis.get("api_usage"),
                "top_matches": [
                    {
                        "resume_id": c["metadata"].get("filename", c["id"]),
                        "category": c["metadata"].get("category", "N/A"),
                        "skills": c["metadata"].get("skills", []),
                        "years": c["metadata"].get("years", 0),
                        "match_score": round(c["score"], 3),
                        "preview": c["text"][:200]
                    }
                    for c in contexts[:10]
                ]
            })
        else:
            # Return raw matches without AI analysis
            return jsonify({
                "prompt": prompt,
                "matches": [
                    {
                        "resume_id": c["metadata"].get("filename", c["id"]),
                        "category": c["metadata"].get("category", "N/A"),
                        "skills": c["metadata"].get("skills", []),
                        "match_score": round(c["score"], 3)
                    }
                    for c in contexts[:10]
                ]
            })
    except Exception as e:
        return jsonify({"error": f"Query failed: {str(e)}"}), 500


@app.post("/api/generate-resume-pdf")
def generate_resume_pdf():
    """Generate a professionally formatted resume PDF from structured data."""
    data = request.get_json(force=True)
    resume_data = data.get("resume_data")
    filename = data.get("filename", "resume").strip()
    
    if not resume_data:
        return jsonify({"error": "resume_data is required"}), 400
    
    try:
        # Generate professional PDF
        buffer = generate_professional_resume_pdf(resume_data)
        
        # Return PDF as download
        return app.response_class(
            buffer.getvalue(),
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}.pdf"'
            }
        )
    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500


@app.post("/api/render-pdf")
def render_pdf():
    """Render plain text to a simple PDF and return it as a download (legacy)."""
    data = request.get_json(force=True)
    title = (data.get("title") or "Reference Resume").strip()
    content = (data.get("content") or "").replace("\r\n", "\n")
    
    try:
        # Use new generator for better formatting
        buffer = generate_simple_pdf_from_text(title, content)
        
        return app.response_class(
            buffer.getvalue(),
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{title.replace(" ", "_")}.pdf"'
            }
        )
    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

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
from services.openai_service import extract_fields_with_openai, analyze_with_prompt, enhance_candidate_summary
from services.resume_analyzer import analyze_and_suggest_improvements, compare_with_references

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
    use_openai = request.form.get('use_openai', 'false').lower() == 'true'
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Extract text
            text = load_and_clean(filepath)
            
            # Extract fields (with optional OpenAI)
            if use_openai:
                fields = extract_fields_with_openai(text)
            else:
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


@app.post("/api/query")
def query_with_prompt():
    """Query the resume database with a natural language prompt."""
    data = request.get_json(force=True)
    prompt = (data.get("prompt") or "").strip()
    top_k = int(data.get("top_k", 20))
    use_openai = bool(data.get("use_openai", True))
    
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
        
        # Use OpenAI to analyze if requested
        if use_openai and contexts:
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
            # Return raw matches without OpenAI
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


@app.post("/api/render-pdf")
def render_pdf():
    """Render plain text to a simple PDF and return it as a download."""
    data = request.get_json(force=True)
    title = (data.get("title") or "Reference Resume").strip()
    content = (data.get("content") or "").replace("\r\n", "\n")

    # Create PDF in memory
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, height - 72, title[:90])

    # Body text with simple wrapping
    c.setFont("Helvetica", 10)
    x = 72
    y = height - 100
    max_width = width - 2*72

    for paragraph in content.split("\n\n"):
        for line in paragraph.split("\n"):
            words = line.split(" ")
            current = ""
            for w in words:
                test = (current + " " + w).strip()
                if c.stringWidth(test, "Helvetica", 10) > max_width:
                    c.drawString(x, y, current)
                    y -= 14
                    current = w
                    if y < 72:
                        c.showPage()
                        c.setFont("Helvetica", 10)
                        y = height - 72
                else:
                    current = test
            if current:
                c.drawString(x, y, current)
                y -= 14
                if y < 72:
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y = height - 72
        y -= 10
    c.showPage()
    c.save()
    buffer.seek(0)

    return app.response_class(buffer.getvalue(), mimetype='application/pdf', headers={
        'Content-Disposition': f'attachment; filename="{title.replace(" ", "_")}.pdf"'
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

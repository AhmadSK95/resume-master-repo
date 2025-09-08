from flask import Flask, request, jsonify
from services.extract_text import load_and_clean
from services.extract_fields import extract_fields, infer_jd_skills, infer_jd_title, infer_req_years
from services.vector_store import ResumeIndex
from services.scorer import score_and_rank

app = Flask(__name__)
index = ResumeIndex(persist_dir="../data/chroma")

@app.get("/api/health")
def health():
    return {"ok": True}

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
            candidates.append({
                "id": rid,
                "path": meta.get("filename", rid),
                "text": text,
                "fields": {"skills": meta.get("skills", []), "titles": meta.get("titles", []), "years_exp": meta.get("years", 0)}
            })

    jd_info = {
        "skills": infer_jd_skills(jd_text),
        "title": infer_jd_title(jd_text),
        "years": infer_req_years(jd_text) or 0
    }

    results = score_and_rank(jd_text, jd_info, candidates)
    return jsonify({"top_k": results[:10]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer

MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDER = SentenceTransformer(MODEL)
WEIGHTS = {"vec":0.55, "kw":0.25, "title":0.15, "yrs":0.05}

def embed_one(text:str):
    return EMBEDDER.encode([text], normalize_embeddings=True)[0]

def cos(a,b):
    return float(cosine_similarity([a],[b])[0][0])

def score_and_rank(jd_text:str, jd_info:dict, candidates:list[dict]):
    jd_vec = embed_one(jd_text)
    jd_skills = set(jd_info.get("skills", []))
    jd_title = jd_info.get("title", "software engineer")
    jd_years = jd_info.get("years", 0)

    results = []
    for c in candidates:
        text = c["text"]
        fields = c["fields"]
        skills = set(fields.get("skills", []))
        titles = fields.get("titles", [])
        years = fields.get("years_exp", 0)

        r_vec = embed_one(text)
        S_vec = cos(jd_vec, r_vec)
        S_kw = (len(jd_skills & skills) / max(1, len(jd_skills))) if jd_skills else 0.0
        S_title = max((fuzz.token_set_ratio(jd_title, t) for t in titles), default=0)/100.0
        S_yrs = (min(years, jd_years)/jd_years) if jd_years else 0.0

        final = (WEIGHTS["vec"]*S_vec + WEIGHTS["kw"]*S_kw + WEIGHTS["title"]*S_title + WEIGHTS["yrs"]*S_yrs)

        why = []
        if S_vec>0.7: why.append("High semantic match")
        if jd_skills & skills: why.append("Skills overlap: "+", ".join(sorted(list(jd_skills & skills))[:5]))
        if S_title>0.6: why.append("Title closely matches JD")
        if S_yrs>0: why.append(f"Experience aligns ({years} yrs)")

        results.append({
            "resume_id": c.get("path") or c.get("id"),
            "candidate_name": None,
            "score": round(final, 3),
            "why": why[:3],
            "highlights": {"skills_found": sorted(list(jd_skills & skills))[:10], "years_experience_est": years}
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results

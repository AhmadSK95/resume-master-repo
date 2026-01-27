"""RAG (Retrieval-Augmented Generation) engine for resume search and analysis."""
from services.vector_store import ResumeIndex
from services.mistral_service import call_mistral
from services.extract_fields import infer_jd_skills, infer_jd_title


def rag_search_resumes(jd_text: str, top_k: int = 10, index: ResumeIndex = None) -> dict:
    """
    RAG-powered resume search: Retrieve top resumes and generate intelligent insights.
    
    Args:
        jd_text: Job description text
        top_k: Number of top resumes to return
        index: ResumeIndex instance
        
    Returns:
        dict with resumes and RAG-generated insights
    """
    if index is None:
        raise ValueError("ResumeIndex required")
    
    # STEP 1: RETRIEVE - Semantic search over vector DB
    hits = index.query_similar(jd_text, top_k=top_k)
    
    # Parse results
    resumes = []
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
    
    # STEP 2: AUGMENT - Extract key requirements from JD
    jd_skills = infer_jd_skills(jd_text)
    jd_title = infer_jd_title(jd_text)
    
    # STEP 3: GENERATE - LLM analyzes search results and provides insights
    rag_insights = generate_search_insights(jd_text, jd_skills, jd_title, resumes[:5])
    
    return {
        "resumes": resumes,
        "rag_insights": rag_insights,
        "query_jd": jd_text[:200] + "..." if len(jd_text) > 200 else jd_text
    }


def generate_search_insights(jd_text: str, jd_skills: list, jd_title: str, top_resumes: list) -> dict:
    """
    Use LLM to generate intelligent insights about the search results.
    
    Args:
        jd_text: Job description
        jd_skills: Extracted skills from JD
        jd_title: Extracted title from JD
        top_resumes: Top 5 matching resumes
        
    Returns:
        dict with key_requirements, match_summary, and patterns
    """
    # Build context from top resumes
    resume_context = "\n\n".join([
        f"Resume {i+1} (Match: {r['similarity_score']}%):\n"
        f"Skills: {', '.join(r['metadata'].get('skills', [])[:10])}\n"
        f"Title: {', '.join(r['metadata'].get('titles', ['N/A']))}\n"
        f"Experience: {r['metadata'].get('years', 0)} years"
        for i, r in enumerate(top_resumes)
    ])
    
    prompt = f"""Analyze this job description and the top matching resumes found:

JOB DESCRIPTION:
{jd_text[:1500]}

TOP MATCHING RESUMES:
{resume_context}

Provide brief insights:
1. KEY_REQUIREMENTS: List 5-8 most important skills/qualifications from the JD
2. MATCH_SUMMARY: One sentence explaining why these resumes match well
3. COMMON_PATTERNS: What do the top resumes have in common?

Be concise and specific."""

    system_prompt = "You are a recruiting analyst providing insights on resume search results."
    
    try:
        response = call_mistral(prompt, system_prompt, temperature=0.5, max_tokens=500)
        
        # Parse response
        insights = parse_insights_response(response, jd_skills, jd_title)
        return insights
    except Exception as e:
        print(f"Error generating RAG insights: {e}")
        # Fallback to basic insights
        return {
            "key_requirements": jd_skills[:8] if jd_skills else ["Skills not detected"],
            "match_summary": f"Found {len(top_resumes)} resumes matching the {jd_title} role.",
            "common_patterns": []
        }


def parse_insights_response(text: str, fallback_skills: list, fallback_title: str) -> dict:
    """Parse LLM insights response into structured dict."""
    import re
    
    insights = {
        "key_requirements": [],
        "match_summary": "",
        "common_patterns": []
    }
    
    # Extract KEY_REQUIREMENTS section
    key_req_match = re.search(r'KEY_REQUIREMENTS[:\s]+(.*?)(?=MATCH_SUMMARY|COMMON_PATTERNS|$)', text, re.DOTALL | re.IGNORECASE)
    if key_req_match:
        content = key_req_match.group(1)
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line)):
                item = re.sub(r'^[-•\d\.\s]+', '', line).strip()
                if item and len(item) > 2:
                    insights["key_requirements"].append(item)
    
    # Fallback to extracted skills if empty
    if not insights["key_requirements"]:
        insights["key_requirements"] = fallback_skills[:8] if fallback_skills else []
    
    # Extract MATCH_SUMMARY
    match_sum = re.search(r'MATCH_SUMMARY[:\s]+(.*?)(?=COMMON_PATTERNS|KEY_REQUIREMENTS|$)', text, re.DOTALL | re.IGNORECASE)
    if match_sum:
        summary = match_sum.group(1).strip()
        # Take first sentence
        first_sent = re.split(r'[.!?]', summary)[0]
        insights["match_summary"] = first_sent.strip() if first_sent else summary[:150]
    else:
        insights["match_summary"] = f"Top resumes match the {fallback_title} requirements."
    
    # Extract COMMON_PATTERNS
    patterns_match = re.search(r'COMMON_PATTERNS[:\s]+(.*?)(?=KEY_REQUIREMENTS|MATCH_SUMMARY|$)', text, re.DOTALL | re.IGNORECASE)
    if patterns_match:
        content = patterns_match.group(1)
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line)):
                item = re.sub(r'^[-•\d\.\s]+', '', line).strip()
                if item and len(item) > 2:
                    insights["common_patterns"].append(item)
    
    return insights


def rag_enhance_suggestions(resume_text: str, jd_text: str, reference_resumes: list) -> list:
    """
    RAG-enhanced resume suggestions: Use similar resumes as examples for improvements.
    
    Args:
        resume_text: User's resume
        jd_text: Job description
        reference_resumes: Top matching reference resumes
        
    Returns:
        list of suggestions with citations to reference resumes
    """
    # Extract relevant sections from reference resumes
    ref_examples = extract_relevant_bullet_examples(reference_resumes, jd_text)
    
    # Build augmented context
    context = "\n\n".join([
        f"EXAMPLE {i+1} (from top {ex['source_rank']}% matching resume):\n{ex['text']}"
        for i, ex in enumerate(ref_examples[:10])
    ])
    
    prompt = f"""You are a resume coach. Use these examples from successful resumes to suggest improvements.

REFERENCE EXAMPLES FROM SIMILAR RESUMES:
{context}

USER'S RESUME (excerpt):
{resume_text[:2000]}

JOB DESCRIPTION:
{jd_text[:1500]}

Provide 5-7 specific bullet improvements inspired by the reference examples:

For each suggestion:
BEFORE: [Original or generic bullet]
AFTER: [Improved bullet inspired by examples]
INSPIRED_BY: [Which example number]
IMPACT: [Why this helps for this JD]

Make bullets achievement-oriented with metrics like the examples."""

    system_prompt = "You are an expert resume writer helping improve bullets using proven examples."
    
    try:
        response = call_mistral(prompt, system_prompt, temperature=0.7, max_tokens=2000)
        
        # Parse suggestions with citations
        suggestions = parse_rag_suggestions(response)
        return suggestions
    except Exception as e:
        print(f"Error in RAG suggestions: {e}")
        return []


def extract_relevant_bullet_examples(resumes: list, jd_text: str, max_examples: int = 10) -> list:
    """Extract relevant bullet points from reference resumes."""
    examples = []
    
    for idx, resume in enumerate(resumes[:5]):
        text = resume.get("text", "")
        lines = text.split('\n')
        
        # Extract lines that look like bullet points and are substantial
        for line in lines:
            line = line.strip()
            if (line.startswith('-') or line.startswith('•') or line.startswith('*')) and len(line) > 40:
                # Check if line has numbers (metrics)
                if any(char.isdigit() for char in line):
                    examples.append({
                        "text": line,
                        "source_rank": idx + 1,
                        "source_score": resume.get("similarity_score", 0)
                    })
        
        if len(examples) >= max_examples:
            break
    
    return examples[:max_examples]


def parse_rag_suggestions(text: str) -> list:
    """Parse RAG-enhanced suggestions with citations."""
    import re
    
    suggestions = []
    
    # Look for BEFORE/AFTER/INSPIRED_BY/IMPACT patterns
    pattern = r'BEFORE:\s*(.+?)\s*AFTER:\s*(.+?)\s*(?:INSPIRED_BY:\s*(.+?))?\s*IMPACT:\s*(.+?)(?=\n\nBEFORE:|$)'
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    
    for before, after, inspired, impact in matches:
        suggestions.append({
            "type": "bullet",
            "before": before.strip(),
            "after": after.strip(),
            "reason": impact.strip(),
            "source": inspired.strip() if inspired else "Reference examples"
        })
    
    return suggestions[:10]

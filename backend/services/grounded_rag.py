"""Evidence-grounded RAG pipeline with strict citation requirements."""
import json
from typing import Dict, List
from services.mistral_service import call_mistral
from services.evidence_segmenter import (
    segment_jd, segment_resume, segment_reference_resumes,
    extract_resume_facts, find_candidate_segments
)


SYSTEM_PROMPT = """You are an evidence-grounded resume/JD analyst. 
Use ONLY the provided JD# / R# / REF# snippets as evidence.
Do NOT infer requirements that aren't explicitly stated.
Do NOT invent skills, tools, or requirements.
Return valid JSON only matching the schema provided.
Keep quotes short (<= 25 words)."""


def stage1_extract_jd_requirements(jd_text: str, jd_segments: List[Dict]) -> Dict:
    """
    Stage 1: Extract requirements ONLY from JD text.
    
    Returns:
        {
            "jd_requirements": [...],
            "warnings": [...]
        }
    """
    # Check if JD is too short
    warnings = []
    if len(jd_text) < 400:
        warnings.append("JD text seems short (< 400 chars). Paste full responsibilities + requirements for better analysis.")
    
    bullet_count = jd_text.count('\n-') + jd_text.count('\n•') + jd_text.count('\n*')
    if bullet_count < 5:
        warnings.append("JD has few bullet points (< 5). More detailed JDs produce better matches.")
    
    # Build segments context
    segments_text = "\n".join([
        f"{seg['id']}: {seg['text']}"
        for seg in jd_segments
    ])
    
    prompt = f"""Extract job requirements from this JD. Use ONLY explicit statements from the JD segments below.

JD SEGMENTS:
{segments_text}

Extract requirements in this EXACT JSON format:
{{
  "jd_requirements": [
    {{
      "requirement": "short requirement text",
      "type": "must" | "preferred" | "nice",
      "category": "skills" | "experience" | "education" | "tools" | "responsibilities",
      "jd_evidence": [{{"id": "JD#N", "quote": "exact quote <= 25 words"}}]
    }}
  ]
}}

RULES:
- type="must": Look for "required", "must have", "essential"
- type="preferred": Look for "preferred", "nice to have", "plus"  
- type="nice": Everything else
- Quote EXACTLY from JD segments (no paraphrasing)
- If JD says "Python experience", write requirement="Python programming"
- If JD says "5+ years", write requirement="5+ years experience" with that evidence
- Do NOT add requirements not explicitly in the JD
- Return JSON only, no markdown"""

    try:
        response = call_mistral(prompt, SYSTEM_PROMPT, temperature=0.2, max_tokens=2000)
        
        # Parse JSON
        # Remove markdown code fences if present
        response = response.strip()
        if response.startswith('```'):
            response = response.split('\n', 1)[1]
            response = response.rsplit('```', 1)[0]
        
        result = json.loads(response)
        result["warnings"] = warnings
        
        return result
    except json.JSONDecodeError as e:
        print(f"JSON decode error in stage1: {e}")
        print(f"Response was: {response[:500]}")
        return {
            "jd_requirements": [],
            "warnings": warnings + [f"Failed to parse JD requirements: {str(e)}"]
        }
    except Exception as e:
        print(f"Error in stage1: {e}")
        return {
            "jd_requirements": [],
            "warnings": warnings + [f"Error extracting requirements: {str(e)}"]
        }


def stage2_evaluate_match(
    jd_requirements: List[Dict],
    resume_segments: List[Dict],
    resume_facts: Dict
) -> Dict:
    """
    Stage 2: Evaluate each requirement against resume with evidence.
    
    Returns:
        {
            "match_evaluation": [...]
        }
    """
    match_evaluation = []
    
    # Provide resume facts context
    facts_context = f"""
RESUME FACTS (extracted deterministically):
- Education: {', '.join([f"{e['degree']} {e['field']}" for e in resume_facts['education']]) if resume_facts['education'] else 'None detected'}
- Total Experience: ~{resume_facts['total_years_experience']:.1f} years
- Experience Ranges: {', '.join([f"{r['start']}-{r['end']}" for r in resume_facts['experience_ranges']]) if resume_facts['experience_ranges'] else 'None detected'}
"""
    
    for req in jd_requirements[:15]:  # Limit to avoid token overflow
        requirement_text = req['requirement']
        
        # Find candidate resume segments
        candidates = find_candidate_segments(requirement_text, resume_segments, top_k=5)
        
        if not candidates:
            # No candidates found
            match_evaluation.append({
                "requirement": requirement_text,
                "status": "missing",
                "confidence": 0.3,
                "jd_evidence": req.get('jd_evidence', []),
                "resume_evidence": [],
                "notes": "No relevant resume segments found for this requirement"
            })
            continue
        
        # Build candidates context
        candidates_text = "\n".join([
            f"{c['id']}: {c['text']}"
            for c in candidates
        ])
        
        prompt = f"""Evaluate if this requirement is met in the resume.

REQUIREMENT: {requirement_text}
JD EVIDENCE: {json.dumps(req.get('jd_evidence', []))}

{facts_context}

CANDIDATE RESUME SEGMENTS:
{candidates_text}

Return JSON in this EXACT format:
{{
  "status": "met" | "partial" | "missing",
  "confidence": 0.0,
  "resume_evidence": [{{"id": "R#N", "quote": "exact quote <= 25 words"}}],
  "notes": "why you marked it this way (1 sentence)"
}}

RULES:
- status="met": Clear evidence in resume segments or facts
- status="partial": Some evidence but incomplete
- status="missing": No evidence found
- confidence: 0.8-1.0 for met, 0.4-0.7 for partial, 0.0-0.4 for missing
- Quote EXACTLY from R# segments
- Check resume_facts first (education, years)
- If requirement is "Bachelor's degree" and facts show "B.Tech", status="met"
- If requirement is "5 years" and facts show "~6 years", status="met"
- Do NOT claim missing if evidence exists
- Return JSON only"""

        try:
            response = call_mistral(prompt, SYSTEM_PROMPT, temperature=0.2, max_tokens=500)
            
            # Parse JSON
            response = response.strip()
            if response.startswith('```'):
                response = response.split('\n', 1)[1]
                response = response.rsplit('```', 1)[0]
            
            eval_result = json.loads(response)
            
            match_evaluation.append({
                "requirement": requirement_text,
                "status": eval_result.get("status", "missing"),
                "confidence": float(eval_result.get("confidence", 0.5)),
                "jd_evidence": req.get('jd_evidence', []),
                "resume_evidence": eval_result.get("resume_evidence", []),
                "notes": eval_result.get("notes", "")
            })
            
        except Exception as e:
            print(f"Error evaluating requirement '{requirement_text}': {e}")
            match_evaluation.append({
                "requirement": requirement_text,
                "status": "missing",
                "confidence": 0.3,
                "jd_evidence": req.get('jd_evidence', []),
                "resume_evidence": [],
                "notes": f"Evaluation error: {str(e)}"
            })
    
    return {"match_evaluation": match_evaluation}


def stage3_common_patterns(reference_segments: List[Dict]) -> Dict:
    """
    Stage 3: Analyze common patterns in top matching resumes.
    
    Returns:
        {
            "common_patterns_in_top_matches": [...]
        }
    """
    if not reference_segments:
        return {"common_patterns_in_top_matches": []}
    
    # Build reference context
    ref_context = "\n".join([
        f"{seg['id']}: {seg['text'][:100]}..."
        for seg in reference_segments[:15]
    ])
    
    prompt = f"""Analyze these snippets from top matching resumes and identify 3-5 common patterns.

REFERENCE SNIPPETS:
{ref_context}

Return JSON in this EXACT format:
{{
  "common_patterns_in_top_matches": [
    {{
      "pattern": "description (e.g., 'Many top resumes mention cloud platforms')",
      "reference_evidence": [{{"id": "REF#N", "quote": "exact quote <= 25 words"}}]
    }}
  ]
}}

RULES:
- Identify what's COMMON across multiple references
- Do NOT list every skill - focus on patterns
- Quote from REF# segments only
- Limit to 5 patterns max
- Return JSON only"""

    try:
        response = call_mistral(prompt, SYSTEM_PROMPT, temperature=0.3, max_tokens=800)
        
        response = response.strip()
        if response.startswith('```'):
            response = response.split('\n', 1)[1]
            response = response.rsplit('```', 1)[0]
        
        result = json.loads(response)
        return result
        
    except Exception as e:
        print(f"Error in stage3: {e}")
        return {"common_patterns_in_top_matches": []}


def grounded_rag_analysis(
    jd_text: str,
    resume_text: str,
    reference_resumes: List[dict] = None
) -> Dict:
    """
    Full evidence-grounded RAG pipeline with strict citation.
    
    Args:
        jd_text: Job description
        resume_text: Candidate's resume
        reference_resumes: Optional top matching resumes
        
    Returns:
        {
            "jd_requirements": [...],
            "match_evaluation": [...],
            "common_patterns_in_top_matches": [...],
            "warnings": [...],
            "resume_facts": {...}
        }
    """
    # Step 0: Segment everything
    jd_segments = segment_jd(jd_text)
    resume_segments = segment_resume(resume_text)
    resume_facts = extract_resume_facts(resume_text)
    
    reference_segments = []
    if reference_resumes:
        reference_segments = segment_reference_resumes(reference_resumes, top_n=3)
    
    # Stage 1: Extract JD requirements
    stage1_result = stage1_extract_jd_requirements(jd_text, jd_segments)
    jd_requirements = stage1_result.get("jd_requirements", [])
    warnings = stage1_result.get("warnings", [])
    
    # Stage 2: Evaluate match
    stage2_result = stage2_evaluate_match(jd_requirements, resume_segments, resume_facts)
    match_evaluation = stage2_result.get("match_evaluation", [])
    
    # Stage 3: Common patterns (optional)
    stage3_result = {}
    if reference_segments:
        stage3_result = stage3_common_patterns(reference_segments)
    
    # Combine results
    return {
        "jd_requirements": jd_requirements,
        "match_evaluation": match_evaluation,
        "common_patterns_in_top_matches": stage3_result.get("common_patterns_in_top_matches", []),
        "warnings": warnings,
        "resume_facts": resume_facts,
        "meta": {
            "jd_segments_count": len(jd_segments),
            "resume_segments_count": len(resume_segments),
            "reference_segments_count": len(reference_segments)
        }
    }


def grounded_search_insights(jd_text: str, top_resumes: List[dict]) -> Dict:
    """
    Generate search insights for "Find Top Resumes" tab.
    Focus ONLY on JD requirements + patterns in retrieved resumes.
    
    Args:
        jd_text: Job description
        top_resumes: Top retrieved resumes
        
    Returns:
        {
            "jd_requirements": [...],
            "common_patterns_in_top_matches": [...],
            "warnings": [...]
        }
    """
    # Segment JD
    jd_segments = segment_jd(jd_text)
    reference_segments = segment_reference_resumes(top_resumes, top_n=5)
    
    # Stage 1: Extract JD requirements
    stage1_result = stage1_extract_jd_requirements(jd_text, jd_segments)
    
    # Stage 3: Common patterns in top matches
    stage3_result = {}
    if reference_segments:
        stage3_result = stage3_common_patterns(reference_segments)
    
    return {
        "jd_requirements": stage1_result.get("jd_requirements", []),
        "common_patterns_in_top_matches": stage3_result.get("common_patterns_in_top_matches", []),
        "warnings": stage1_result.get("warnings", []),
        "match_summary": f"Found {len(top_resumes)} matching resumes based on semantic similarity.",
        "meta": {
            "jd_segments_count": len(jd_segments),
            "reference_segments_count": len(reference_segments)
        }
    }

"""Resume analysis and improvement suggestions using Mistral."""
from services.openai_service import call_mistral

def analyze_and_suggest_improvements(resume_text: str) -> dict:
    """
    Analyze a user's resume and provide detailed improvement suggestions.
    
    Args:
        resume_text: The full text of the user's resume
    
    Returns:
        dict with analysis, suggestions, and scores
    """
    prompt = f"""You are an expert resume coach and career consultant. Analyze this resume and provide comprehensive feedback.

Resume:
{resume_text[:4000]}

Provide a detailed analysis in the following format:

1. OVERALL SCORE (0-100): Rate the resume quality
2. STRENGTHS: List 3-5 strong points
3. WEAKNESSES: List 3-5 areas needing improvement
4. SPECIFIC SUGGESTIONS: Provide 5-7 actionable improvements with examples
5. MISSING ELEMENTS: What's missing that should be added
6. FORMAT & STRUCTURE: Comments on layout and organization
7. KEYWORDS: Important industry keywords that should be included

Be specific, constructive, and actionable."""

    system_prompt = "You are an expert resume coach with 20 years of experience in career development and recruiting."
    
    try:
        analysis = call_mistral(prompt, system_prompt, temperature=0.7, max_tokens=1500)
        
        # Try to extract score
        score = 75  # Default
        if "OVERALL SCORE" in analysis:
            import re
            score_match = re.search(r'(\d+)', analysis.split("OVERALL SCORE")[1].split("\n")[0])
            if score_match:
                score = int(score_match.group(1))
        
        return {
            "score": score,
            "analysis": analysis,
            "model": "mistral",
            "api_usage": None
        }
    except Exception as e:
        return {
            "score": 0,
            "analysis": f"Error analyzing resume: {str(e)}",
            "model": "mistral",
            "api_usage": None
        }


def compare_with_references(user_resume_text: str, reference_resumes: list[dict]) -> dict:
    """
    Compare user's resume with reference resumes and explain differences.
    
    Args:
        user_resume_text: User's resume text
        reference_resumes: List of reference resume dicts with text and metadata
    
    Returns:
        dict with comparison analysis
    """
    # Build context from top references
    ref_context = "\n\n---\n\n".join([
        f"Reference Resume {i+1} (Category: {r.get('metadata', {}).get('category', 'N/A')}):\n"
        f"Skills: {r.get('metadata', {}).get('skills', '')}\n"
        f"Experience: {r.get('metadata', {}).get('years', 0)} years\n"
        f"Content: {r['text'][:300]}..."
        for i, r in enumerate(reference_resumes[:3])
    ])
    
    prompt = f"""Compare this user's resume with these high-quality reference resumes and explain what they can learn:

USER'S RESUME:
{user_resume_text[:1500]}

REFERENCE RESUMES:
{ref_context}

Provide:
1. KEY DIFFERENCES: What do reference resumes have that user's doesn't?
2. WHAT TO ADOPT: Specific elements to incorporate from references
3. FORMATTING INSIGHTS: How reference resumes structure information
4. SKILL PRESENTATION: How references showcase their skills better"""

    system_prompt = "You are a resume expert helping job seekers improve their resumes."
    
    try:
        comparison = call_mistral(prompt, system_prompt, temperature=0.7, max_tokens=1000)
        
        return {
            "comparison": comparison,
            "model": "mistral",
            "api_usage": None
        }
    except Exception as e:
        return {
            "comparison": f"Error comparing resumes: {str(e)}",
            "model": "mistral",
            "api_usage": None
        }


def analyze_resume_for_job(resume_text: str, jd_text: str, reference_resumes: list[dict] = None) -> dict:
    """
    Analyze user's resume against a specific job description with reference resume insights.
    
    Args:
        resume_text: The full text of the user's resume
        jd_text: Job description text
        reference_resumes: Optional list of top matching reference resumes
    
    Returns:
        dict with comprehensive analysis, score, and suggestions
    """
    # Build reference context if provided
    ref_context = ""
    if reference_resumes and len(reference_resumes) > 0:
        ref_context = "\n\nTOP MATCHING REFERENCE RESUMES:\n" + "\n\n".join([
            f"Reference {i+1} (Match: {r.get('similarity_score', 0):.0f}%):\n"
            f"Skills: {', '.join(r.get('metadata', {}).get('skills', [])[:8])}\n"
            f"Experience: {r.get('metadata', {}).get('years', 0)} years\n"
            f"Preview: {r['text'][:250]}..."
            for i, r in enumerate(reference_resumes[:3])
        ])
    
    prompt = f"""You are an expert resume coach. Analyze this resume against the job description and provide actionable insights.

JOB DESCRIPTION:
{jd_text[:2000]}

USER'S RESUME:
{resume_text[:3000]}{ref_context}

Provide a comprehensive analysis in this format:

1. OVERALL MATCH SCORE (0-100): Rate how well the resume matches the JD

2. JD REQUIREMENTS ANALYSIS:
   - List key requirements from the JD
   - Mark which ones are clearly addressed in the resume
   - Mark which ones are missing or weak

3. GAP ANALYSIS:
   - Critical gaps between resume and JD requirements
   - Missing keywords and skills the JD emphasizes
   - Experience level alignment issues

4. STRENGTHS FOR THIS ROLE:
   - What in the resume aligns well with this JD
   - Relevant accomplishments to highlight

5. SPECIFIC IMPROVEMENTS:
   - 5-7 actionable changes to better match this JD
   - Suggested keywords to add
   - Content to emphasize or de-emphasize
   - Formatting suggestions

6. LEARNING FROM REFERENCES:
   - What successful candidates include (based on reference resumes)
   - How they structure relevant experience
   - Keywords and phrases they use effectively

7. PRIORITY ACTIONS:
   - Top 3 most important changes ranked by impact

Be specific, constructive, and actionable. Focus on this particular job opportunity."""

    system_prompt = "You are an expert resume coach and ATS optimization specialist with deep knowledge of matching resumes to job descriptions."
    
    try:
        analysis = call_mistral(prompt, system_prompt, temperature=0.7, max_tokens=2000)
        
        # Extract score
        score = 65  # Default
        if "MATCH SCORE" in analysis:
            import re
            score_match = re.search(r'(\d+)', analysis.split("MATCH SCORE")[1].split("\n")[0])
            if score_match:
                score = int(score_match.group(1))
        
        return {
            "score": score,
            "analysis": analysis,
            "model": "mistral",
            "api_usage": None
        }
    except Exception as e:
        return {
            "score": 0,
            "analysis": f"Error analyzing resume for job: {str(e)}",
            "model": "mistral",
            "api_usage": None
        }

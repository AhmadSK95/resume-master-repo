"""Resume analysis and improvement suggestions using Mistral."""
from services.mistral_service import call_mistral
import re

def extract_bullet_suggestions(analysis_text: str) -> list:
    """Extract BEFORE/AFTER/IMPACT bullet suggestions from analysis text."""
    suggestions = []
    
    # Look for BEFORE/AFTER/IMPACT patterns
    pattern = r'BEFORE:\s*(.+?)\s*AFTER:\s*(.+?)\s*IMPACT:\s*(.+?)(?=\n\nBEFORE:|\n\n\*\*|$)'
    matches = re.findall(pattern, analysis_text, re.DOTALL | re.IGNORECASE)
    
    for before, after, impact in matches:
        suggestions.append({
            "type": "bullet",
            "before": before.strip(),
            "after": after.strip(),
            "reason": impact.strip()
        })
    
    return suggestions[:10]  # Limit to 10 suggestions


def extract_section(analysis_text: str, section_name: str) -> list:
    """Extract bullet points or content from a named section."""
    items = []
    
    # Find the section
    pattern = rf'\*?\*?{section_name}\*?\*?:?\s*(.+?)(?=\n\n\*\*|$)'
    match = re.search(pattern, analysis_text, re.DOTALL | re.IGNORECASE)
    
    if match:
        content = match.group(1).strip()
        # Extract bullet points or numbered items
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line)):
                # Clean up bullet/number markers
                cleaned = re.sub(r'^[-•\d\.\s]+', '', line).strip()
                if cleaned:
                    items.append(cleaned)
            elif line and not line.startswith('**'):  # Not a new section header
                items.append(line)
    
    return items[:15]  # Limit items


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
    Returns structured suggestions for bullet point improvements.
    
    Args:
        resume_text: The full text of the user's resume
        jd_text: Job description text
        reference_resumes: Optional list of top matching reference resumes
    
    Returns:
        dict with comprehensive analysis, score, suggestions array, and detailed breakdown
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
    
    prompt = f"""You are an expert resume coach. Analyze this resume against the job description and provide specific, actionable insights.

JOB DESCRIPTION:
{jd_text[:2000]}

USER'S RESUME:
{resume_text[:3000]}{ref_context}

Provide analysis in this EXACT format:

**MATCH SCORE**: [0-100 number]

**KEY REQUIREMENTS FROM JD**:
- [Requirement 1]: [Present/Missing/Weak] in resume
- [Requirement 2]: [Present/Missing/Weak] in resume
- [List 5-7 key requirements]

**CRITICAL GAPS**:
1. [Specific gap with what's missing]
2. [Another gap]
3. [List 3-5 gaps]

**MISSING KEYWORDS**: [List 10-15 important keywords from JD not in resume]

**STRENGTHS FOR THIS ROLE**:
- [Specific strength 1]
- [Specific strength 2]
- [List 3-5 strengths]

**RECOMMENDED BULLET IMPROVEMENTS**:
For each improvement, use this format:
BEFORE: [Original bullet from resume or generic version]
AFTER: [Improved bullet with JD keywords and metrics]
IMPACT: [Why this change matters for this JD]

[Provide 5-7 bullet improvements]

**TOP 3 PRIORITY ACTIONS**:
1. [Most important change with immediate impact]
2. [Second priority]
3. [Third priority]

Be specific to THIS job description. Use actual JD keywords. Make bullets achievement-oriented with metrics."""

    system_prompt = "You are an expert resume coach and ATS optimization specialist with deep knowledge of matching resumes to job descriptions."
    
    try:
        analysis = call_mistral(prompt, system_prompt, temperature=0.7, max_tokens=2500)
        
        # Extract score
        score = 65  # Default
        if "MATCH SCORE" in analysis or "**MATCH SCORE**" in analysis:
            import re
            score_match = re.search(r'\*?\*?MATCH SCORE\*?\*?:?\s*(\d+)', analysis)
            if score_match:
                score = int(score_match.group(1))
        
        # Extract structured suggestions for bullets
        suggestions = extract_bullet_suggestions(analysis)
        
        # Extract key gaps and keywords
        gaps = extract_section(analysis, "CRITICAL GAPS")
        missing_keywords = extract_section(analysis, "MISSING KEYWORDS")
        strengths = extract_section(analysis, "STRENGTHS")
        priorities = extract_section(analysis, "TOP 3 PRIORITY")
        
        return {
            "score": score,
            "analysis": analysis,
            "suggestions": suggestions,
            "gaps": gaps,
            "missing_keywords": missing_keywords,
            "strengths": strengths,
            "priorities": priorities,
            "model": "mistral",
            "api_usage": None
        }
    except Exception as e:
        return {
            "score": 0,
            "analysis": f"Error analyzing resume for job: {str(e)}",
            "suggestions": [],
            "gaps": [],
            "missing_keywords": "",
            "strengths": [],
            "priorities": [],
            "model": "mistral",
            "api_usage": None
        }

"""Intelligent field extraction using NLP and LLM - dynamically extracts what matters for each JD."""
import re
from services.mistral_service import call_mistral


def extract_jd_requirements(jd_text: str) -> dict:
    """
    Use LLM to intelligently extract ALL requirements from a job description.
    Returns structured requirements specific to THIS job.
    
    Args:
        jd_text: Job description text
        
    Returns:
        dict with dynamic requirements: skills, qualifications, certifications, 
        soft_skills, tools, education, experience_details, etc.
    """
    prompt = f"""Analyze this job description and extract ALL requirements in structured format.

JOB DESCRIPTION:
{jd_text[:3000]}

Extract and categorize requirements into:

1. REQUIRED_SKILLS: Technical/hard skills that are must-haves
2. PREFERRED_SKILLS: Nice-to-have technical skills
3. SOFT_SKILLS: Communication, leadership, teamwork, etc.
4. TOOLS_TECHNOLOGIES: Specific tools, platforms, frameworks, languages
5. CERTIFICATIONS: Any certifications mentioned (AWS, CPA, PMP, etc.)
6. EDUCATION: Degree requirements (BS, MS, PhD, specific majors)
7. EXPERIENCE_REQUIREMENTS: Years, specific roles, industries, domain experience
8. RESPONSIBILITIES: Key job responsibilities
9. DOMAIN_KNOWLEDGE: Industry-specific knowledge (healthcare, fintech, etc.)
10. KEYWORDS: Important keywords for ATS matching

Return as structured sections with bullet points. Be comprehensive."""

    system_prompt = "You are an expert recruiter and ATS specialist. Extract comprehensive, specific requirements."
    
    try:
        response = call_mistral(prompt, system_prompt, temperature=0.3, max_tokens=1500)
        
        # Parse response into structured dict
        parsed = parse_requirements_response(response)
        return parsed
    except Exception as e:
        print(f"Error extracting JD requirements: {e}")
        return get_empty_requirements()


def extract_resume_qualifications(resume_text: str, jd_requirements: dict = None) -> dict:
    """
    Use LLM to extract qualifications from resume, focusing on what matches JD if provided.
    
    Args:
        resume_text: Resume text
        jd_requirements: Optional dict of JD requirements to focus extraction
        
    Returns:
        dict with candidate's qualifications in same structure as JD requirements
    """
    context = ""
    if jd_requirements:
        context = f"""
Focus on finding evidence of these requirement categories:
- Technical Skills: {len(jd_requirements.get('required_skills', []) + jd_requirements.get('preferred_skills', []))} skills needed
- Tools: {', '.join(jd_requirements.get('tools_technologies', [])[:10])}
- Certifications: {', '.join(jd_requirements.get('certifications', []))}
- Domain: {', '.join(jd_requirements.get('domain_knowledge', []))}
"""
    
    prompt = f"""Analyze this resume and extract ALL qualifications in structured format.
{context}

RESUME:
{resume_text[:4000]}

Extract and categorize:

1. TECHNICAL_SKILLS: All technical/hard skills mentioned
2. SOFT_SKILLS: Leadership, communication, collaboration, etc.
3. TOOLS_TECHNOLOGIES: Specific tools, platforms, frameworks, languages used
4. CERTIFICATIONS: Any certifications held
5. EDUCATION: Degrees, majors, institutions, GPA if impressive
6. EXPERIENCE_DETAILS: Years total, industries worked, company types (startup/enterprise)
7. ACHIEVEMENTS: Quantified accomplishments with metrics
8. PROJECTS: Notable projects with technologies used
9. DOMAIN_KNOWLEDGE: Industry/domain expertise demonstrated
10. KEYWORDS: Important keywords present in resume

Be specific and comprehensive. Include metrics where available."""

    system_prompt = "You are an expert resume parser. Extract detailed, structured information."
    
    try:
        response = call_mistral(prompt, system_prompt, temperature=0.3, max_tokens=1500)
        parsed = parse_qualifications_response(response)
        return parsed
    except Exception as e:
        print(f"Error extracting resume qualifications: {e}")
        return get_empty_qualifications()


def intelligent_gap_analysis(jd_requirements: dict, resume_qualifications: dict) -> dict:
    """
    Use LLM to perform intelligent gap analysis between JD requirements and resume.
    
    Args:
        jd_requirements: Requirements extracted from JD
        resume_qualifications: Qualifications extracted from resume
        
    Returns:
        dict with: strengths, gaps, partial_matches, missing_critical, recommendations
    """
    prompt = f"""Perform detailed gap analysis between job requirements and candidate qualifications.

JOB REQUIREMENTS:
Required Skills: {', '.join(jd_requirements.get('required_skills', []))}
Preferred Skills: {', '.join(jd_requirements.get('preferred_skills', []))}
Tools: {', '.join(jd_requirements.get('tools_technologies', []))}
Certifications: {', '.join(jd_requirements.get('certifications', []))}
Education: {', '.join(jd_requirements.get('education', []))}
Domain Knowledge: {', '.join(jd_requirements.get('domain_knowledge', []))}

CANDIDATE QUALIFICATIONS:
Technical Skills: {', '.join(resume_qualifications.get('technical_skills', []))}
Tools: {', '.join(resume_qualifications.get('tools_technologies', []))}
Certifications: {', '.join(resume_qualifications.get('certifications', []))}
Education: {', '.join(resume_qualifications.get('education', []))}
Domain: {', '.join(resume_qualifications.get('domain_knowledge', []))}
Experience: {', '.join(resume_qualifications.get('experience_details', []))}

Provide:
1. STRONG_MATCHES: Requirements candidate fully meets (be specific)
2. PARTIAL_MATCHES: Requirements candidate partially meets (explain how)
3. CRITICAL_GAPS: Must-have requirements candidate lacks
4. NICE_TO_HAVE_GAPS: Preferred requirements candidate lacks
5. TRANSFERABLE_SKILLS: Skills candidate has that could transfer
6. MATCH_SCORE: Overall match 0-100
7. TOP_3_ACTIONS: Most important things to add/improve on resume

Be specific with examples."""

    system_prompt = "You are an expert ATS analyst and recruiter performing detailed match analysis."
    
    try:
        response = call_mistral(prompt, system_prompt, temperature=0.5, max_tokens=1500)
        analysis = parse_gap_analysis_response(response)
        return analysis
    except Exception as e:
        print(f"Error in gap analysis: {e}")
        return {
            'strong_matches': [],
            'partial_matches': [],
            'critical_gaps': [],
            'nice_to_have_gaps': [],
            'transferable_skills': [],
            'match_score': 0,
            'top_3_actions': []
        }


def parse_requirements_response(text: str) -> dict:
    """Parse LLM response into structured requirements dict."""
    result = {
        'required_skills': [],
        'preferred_skills': [],
        'soft_skills': [],
        'tools_technologies': [],
        'certifications': [],
        'education': [],
        'experience_requirements': [],
        'responsibilities': [],
        'domain_knowledge': [],
        'keywords': []
    }
    
    # Map section headers to dict keys
    section_map = {
        'REQUIRED_SKILLS': 'required_skills',
        'REQUIRED SKILLS': 'required_skills',
        'PREFERRED_SKILLS': 'preferred_skills',
        'PREFERRED SKILLS': 'preferred_skills',
        'SOFT_SKILLS': 'soft_skills',
        'SOFT SKILLS': 'soft_skills',
        'TOOLS_TECHNOLOGIES': 'tools_technologies',
        'TOOLS': 'tools_technologies',
        'CERTIFICATIONS': 'certifications',
        'EDUCATION': 'education',
        'EXPERIENCE_REQUIREMENTS': 'experience_requirements',
        'EXPERIENCE': 'experience_requirements',
        'RESPONSIBILITIES': 'responsibilities',
        'DOMAIN_KNOWLEDGE': 'domain_knowledge',
        'DOMAIN': 'domain_knowledge',
        'KEYWORDS': 'keywords'
    }
    
    current_section = None
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line is a section header
        line_upper = line.upper().rstrip(':').strip()
        if line_upper in section_map:
            current_section = section_map[line_upper]
            continue
        
        # Extract bullet point or numbered item
        if current_section and (line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line)):
            item = re.sub(r'^[-•\d\.\s]+', '', line).strip()
            if item and len(item) > 3:
                result[current_section].append(item)
    
    return result


def parse_qualifications_response(text: str) -> dict:
    """Parse LLM response into structured qualifications dict."""
    result = {
        'technical_skills': [],
        'soft_skills': [],
        'tools_technologies': [],
        'certifications': [],
        'education': [],
        'experience_details': [],
        'achievements': [],
        'projects': [],
        'domain_knowledge': [],
        'keywords': []
    }
    
    section_map = {
        'TECHNICAL_SKILLS': 'technical_skills',
        'TECHNICAL SKILLS': 'technical_skills',
        'SOFT_SKILLS': 'soft_skills',
        'SOFT SKILLS': 'soft_skills',
        'TOOLS_TECHNOLOGIES': 'tools_technologies',
        'TOOLS': 'tools_technologies',
        'CERTIFICATIONS': 'certifications',
        'EDUCATION': 'education',
        'EXPERIENCE_DETAILS': 'experience_details',
        'EXPERIENCE': 'experience_details',
        'ACHIEVEMENTS': 'achievements',
        'PROJECTS': 'projects',
        'DOMAIN_KNOWLEDGE': 'domain_knowledge',
        'DOMAIN': 'domain_knowledge',
        'KEYWORDS': 'keywords'
    }
    
    current_section = None
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        line_upper = line.upper().rstrip(':').strip()
        if line_upper in section_map:
            current_section = section_map[line_upper]
            continue
        
        if current_section and (line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line)):
            item = re.sub(r'^[-•\d\.\s]+', '', line).strip()
            if item and len(item) > 3:
                result[current_section].append(item)
    
    return result


def parse_gap_analysis_response(text: str) -> dict:
    """Parse gap analysis response."""
    result = {
        'strong_matches': [],
        'partial_matches': [],
        'critical_gaps': [],
        'nice_to_have_gaps': [],
        'transferable_skills': [],
        'match_score': 65,
        'top_3_actions': []
    }
    
    section_map = {
        'STRONG_MATCHES': 'strong_matches',
        'STRONG MATCHES': 'strong_matches',
        'PARTIAL_MATCHES': 'partial_matches',
        'PARTIAL MATCHES': 'partial_matches',
        'CRITICAL_GAPS': 'critical_gaps',
        'CRITICAL GAPS': 'critical_gaps',
        'NICE_TO_HAVE_GAPS': 'nice_to_have_gaps',
        'NICE TO HAVE GAPS': 'nice_to_have_gaps',
        'TRANSFERABLE_SKILLS': 'transferable_skills',
        'TRANSFERABLE SKILLS': 'transferable_skills',
        'TOP_3_ACTIONS': 'top_3_actions',
        'TOP 3 ACTIONS': 'top_3_actions'
    }
    
    current_section = None
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Extract match score
        if 'MATCH_SCORE' in line.upper() or 'MATCH SCORE' in line.upper():
            score_match = re.search(r'(\d+)', line)
            if score_match:
                result['match_score'] = int(score_match.group(1))
            continue
        
        line_upper = line.upper().rstrip(':').strip()
        if line_upper in section_map:
            current_section = section_map[line_upper]
            continue
        
        if current_section and (line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line)):
            item = re.sub(r'^[-•\d\.\s]+', '', line).strip()
            if item and len(item) > 3:
                result[current_section].append(item)
    
    return result


def get_empty_requirements():
    """Return empty requirements structure."""
    return {
        'required_skills': [],
        'preferred_skills': [],
        'soft_skills': [],
        'tools_technologies': [],
        'certifications': [],
        'education': [],
        'experience_requirements': [],
        'responsibilities': [],
        'domain_knowledge': [],
        'keywords': []
    }


def get_empty_qualifications():
    """Return empty qualifications structure."""
    return {
        'technical_skills': [],
        'soft_skills': [],
        'tools_technologies': [],
        'certifications': [],
        'education': [],
        'experience_details': [],
        'achievements': [],
        'projects': [],
        'domain_knowledge': [],
        'keywords': []
    }

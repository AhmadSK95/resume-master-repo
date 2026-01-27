"""Mistral integration for resume analysis and prompt-based querying via Ollama."""
import requests
import json

# Ollama API endpoint for local Mistral
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MISTRAL_MODEL = "mistral"

def call_mistral(prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = 500) -> str:
    """
    Call local Mistral model via Ollama.
    
    Args:
        prompt: User prompt
        system_prompt: System message for context
        temperature: Response creativity (0-1)
        max_tokens: Max response length
        
    Returns:
        Generated text response
    """
    full_prompt = prompt
    if system_prompt:
        full_prompt = f"{system_prompt}\n\n{prompt}"
    
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": MISTRAL_MODEL,
                "prompt": full_prompt,
                "temperature": temperature,
                "num_predict": max_tokens,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        print(f"Mistral API error: {e}")
        return ""


def extract_fields_with_mistral(resume_text: str) -> dict:
    """Extract structured fields from resume using Mistral."""
    prompt = f"""Extract the following information from this resume and return as JSON:
- skills: list of technical skills
- titles: list of job titles mentioned
- years_exp: total years of experience (number)
- name: candidate name if available

Resume:
{resume_text[:3000]}

Return only valid JSON without markdown formatting."""

    system_prompt = "You are a resume parser. Return only JSON."
    
    try:
        response_text = call_mistral(prompt, system_prompt, temperature=0.3, max_tokens=500)
        
        # Try to parse JSON from response
        result = json.loads(response_text)
        
        return {
            "skills": result.get("skills", [])[:20],
            "titles": result.get("titles", [])[:5],
            "years_exp": result.get("years_exp", 0),
            "name": result.get("name"),
            "api_usage": None  # No cost tracking for local model
        }
    except Exception as e:
        print(f"Mistral extraction error: {e}")
        return {"skills": [], "titles": ["unknown"], "years_exp": 0, "name": None, "api_usage": None}


def analyze_with_prompt(prompt: str, resume_contexts: list[dict]) -> dict:
    """
    Analyze resumes based on user's natural language prompt using Mistral.
    
    Args:
        prompt: User's query/prompt
        resume_contexts: List of dicts with keys: text, metadata, score
    
    Returns:
        dict with answer and context information
    """
    # Build context from top resumes
    context_text = "\n\n---\n\n".join([
        f"Resume {i+1} (Match Score: {r['score']:.2f}):\n"
        f"Category: {r.get('metadata', {}).get('category', 'N/A')}\n"
        f"Skills: {', '.join(r.get('metadata', {}).get('skills', [])[:10])}\n"
        f"Experience: {r.get('metadata', {}).get('years', 0)} years\n"
        f"Content Preview: {r['text'][:500]}..."
        for i, r in enumerate(resume_contexts[:5])
    ])
    
    system_msg = """You are an expert technical recruiter and resume analyst. 
Analyze resumes and answer questions about candidates based on the provided resume data.
Be specific, cite evidence from resumes, and provide actionable insights."""

    user_msg = f"""User Question: {prompt}

Based on these candidate resumes from our database:

{context_text}

Provide a comprehensive answer that:
1. Directly answers the question
2. Cites specific examples from the resumes
3. Ranks or recommends candidates if applicable
4. Explains your reasoning"""

    try:
        answer = call_mistral(user_msg, system_msg, temperature=0.7, max_tokens=1000)
        
        return {
            "answer": answer,
            "context_used": len(resume_contexts),
            "model": "mistral",
            "api_usage": None
        }
    except Exception as e:
        return {
            "answer": f"Error analyzing resumes: {str(e)}",
            "context_used": 0,
            "model": "mistral",
            "api_usage": None
        }


def enhance_candidate_summary(resume_text: str, jd_text: str = None) -> dict:
    """Generate a summary of how a candidate fits a role using Mistral."""
    prompt = f"""Summarize this candidate's qualifications in 2-3 sentences:

Resume: {resume_text[:1500]}"""
    
    if jd_text:
        prompt += f"\n\nJob Requirements: {jd_text[:800]}\n\nFocus on relevant fit for this role."
    
    system_prompt = "You are a recruiter writing candidate summaries."
    
    try:
        summary = call_mistral(prompt, system_prompt, temperature=0.7, max_tokens=150)
        return {
            "summary": summary,
            "api_usage": None
        }
    except Exception as e:
        return {"summary": "AI summary unavailable", "api_usage": None}

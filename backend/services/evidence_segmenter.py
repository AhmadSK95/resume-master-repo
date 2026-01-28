"""Evidence segmentation for citation-grounded analysis."""
import re
from typing import List, Dict


def segment_jd(jd_text: str) -> List[Dict[str, str]]:
    """
    Segment job description into numbered segments for citation.
    
    Returns:
        List of {"id": "JD#1", "text": "..."}
    """
    segments = []
    
    # Split by bullet points, numbered lists, or double newlines
    lines = jd_text.split('\n')
    
    segment_id = 1
    current_segment = []
    
    for line in lines:
        line = line.strip()
        
        if not line:
            if current_segment:
                text = ' '.join(current_segment)
                if len(text) > 20:  # Minimum segment length
                    segments.append({
                        "id": f"JD#{segment_id}",
                        "text": text
                    })
                    segment_id += 1
                current_segment = []
            continue
        
        # Check if line starts a new segment (bullet, number, or section header)
        is_new_segment = (
            line.startswith('-') or 
            line.startswith('•') or 
            line.startswith('*') or
            re.match(r'^\d+[\.\)]', line) or
            line.isupper() or
            (len(line) < 60 and line.endswith(':'))
        )
        
        if is_new_segment and current_segment:
            # Save previous segment
            text = ' '.join(current_segment)
            if len(text) > 20:
                segments.append({
                    "id": f"JD#{segment_id}",
                    "text": text
                })
                segment_id += 1
            current_segment = []
        
        # Clean bullet markers
        clean_line = re.sub(r'^[-•\*\d\.\)]+\s*', '', line)
        if clean_line:
            current_segment.append(clean_line)
    
    # Add final segment
    if current_segment:
        text = ' '.join(current_segment)
        if len(text) > 20:
            segments.append({
                "id": f"JD#{segment_id}",
                "text": text
            })
    
    return segments


def segment_resume(resume_text: str) -> List[Dict[str, str]]:
    """
    Segment resume into numbered segments for citation.
    
    Returns:
        List of {"id": "R#1", "text": "..."}
    """
    segments = []
    
    lines = resume_text.split('\n')
    segment_id = 1
    current_segment = []
    
    for line in lines:
        line = line.strip()
        
        if not line:
            if current_segment:
                text = ' '.join(current_segment)
                if len(text) > 15:
                    segments.append({
                        "id": f"R#{segment_id}",
                        "text": text
                    })
                    segment_id += 1
                current_segment = []
            continue
        
        # Check for section headers or bullet points
        is_new_segment = (
            line.startswith('-') or 
            line.startswith('•') or 
            line.startswith('*') or
            re.match(r'^\d+[\.\)]', line) or
            (line.isupper() and len(line) < 40) or
            re.match(r'^[A-Z][^.!?]+:$', line)
        )
        
        if is_new_segment and current_segment:
            text = ' '.join(current_segment)
            if len(text) > 15:
                segments.append({
                    "id": f"R#{segment_id}",
                    "text": text
                })
                segment_id += 1
            current_segment = []
        
        clean_line = re.sub(r'^[-•\*\d\.\)]+\s*', '', line)
        if clean_line:
            current_segment.append(clean_line)
    
    if current_segment:
        text = ' '.join(current_segment)
        if len(text) > 15:
            segments.append({
                "id": f"R#{segment_id}",
                "text": text
            })
    
    return segments


def segment_reference_resumes(reference_resumes: List[dict], top_n: int = 3) -> List[Dict[str, str]]:
    """
    Extract key segments from reference resumes for pattern analysis.
    
    Returns:
        List of {"id": "REF#1", "text": "...", "source_idx": 0}
    """
    segments = []
    segment_id = 1
    
    for idx, resume in enumerate(reference_resumes[:top_n]):
        text = resume.get('text', '')
        lines = text.split('\n')
        
        # Extract achievement bullets (lines with metrics)
        for line in lines:
            line = line.strip()
            if (line.startswith('-') or line.startswith('•') or line.startswith('*')) and len(line) > 40:
                # Check for metrics
                if any(char.isdigit() for char in line):
                    clean_line = re.sub(r'^[-•\*]+\s*', '', line)
                    segments.append({
                        "id": f"REF#{segment_id}",
                        "text": clean_line,
                        "source_idx": idx,
                        "source_score": resume.get('similarity_score', 0)
                    })
                    segment_id += 1
                    
                    if segment_id > 20:  # Limit total reference segments
                        return segments
    
    return segments


def extract_resume_facts(resume_text: str) -> Dict[str, any]:
    """
    Deterministically extract key facts from resume before LLM analysis.
    This prevents LLM from missing or hallucinating basic facts.
    
    Returns:
        {
            "education": [{"degree": "...", "field": "...", "institution": "..."}],
            "total_years_experience": float,
            "experience_ranges": [{"start": "...", "end": "...", "duration_years": float}]
        }
    """
    facts = {
        "education": [],
        "total_years_experience": 0.0,
        "experience_ranges": []
    }
    
    # Extract education
    education_patterns = [
        r'\b(B\.?Tech|Bachelor|B\.?S\.?|B\.?E\.?|M\.?S\.?|Master|M\.?Tech|MBA|Ph\.?D\.?|Doctorate)\b',
        r'\b(Computer Science|CS|Information Technology|IT|Engineering|Mathematics|Statistics|Data Science)\b',
        r'\b(University|Institute|College|IIT|MIT|Stanford|Berkeley)\b'
    ]
    
    lines = resume_text.split('\n')
    for i, line in enumerate(lines):
        # Look for lines with degree keywords
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in education_patterns[:1]):
            # Try to extract full education entry
            degree_match = re.search(r'(B\.?Tech|Bachelor|B\.?S\.?|B\.?E\.?|M\.?S\.?|Master|M\.?Tech|MBA|Ph\.?D\.?)', line, re.IGNORECASE)
            field_match = re.search(r'(Computer Science|CS|Information Technology|IT|Engineering|Mathematics|Statistics|Data Science|Software|Electrical|Mechanical)', line, re.IGNORECASE)
            institution_match = re.search(r'([A-Z][a-z]+ (?:University|Institute|College|Tech))', line)
            
            if degree_match:
                facts["education"].append({
                    "degree": degree_match.group(1),
                    "field": field_match.group(1) if field_match else "",
                    "institution": institution_match.group(1) if institution_match else "",
                    "raw_text": line.strip()[:100]
                })
    
    # Extract experience duration from date ranges
    # Patterns: "Jan 2022 - Present", "2020-2023", "Jun 2021 – Dec 2022"
    date_range_patterns = [
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})\s*[-–—to]\s*(Present|Current|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4}))',
        r'(\d{4})\s*[-–—to]\s*(Present|Current|\d{4})',
    ]
    
    import datetime
    current_year = datetime.datetime.now().year
    
    for line in lines:
        for pattern in date_range_patterns:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                try:
                    full_match = match.group(0)
                    
                    # Extract start year
                    start_year_match = re.search(r'(\d{4})', full_match)
                    if start_year_match:
                        start_year = int(start_year_match.group(1))
                        
                        # Extract end year
                        if 'present' in full_match.lower() or 'current' in full_match.lower():
                            end_year = current_year
                        else:
                            end_year_matches = re.findall(r'(\d{4})', full_match)
                            end_year = int(end_year_matches[-1]) if len(end_year_matches) > 1 else current_year
                        
                        duration = max(0, end_year - start_year)
                        
                        facts["experience_ranges"].append({
                            "start": str(start_year),
                            "end": "Present" if end_year == current_year else str(end_year),
                            "duration_years": duration,
                            "raw_text": full_match
                        })
                except:
                    continue
    
    # Calculate total years (sum of ranges, rough estimate)
    if facts["experience_ranges"]:
        facts["total_years_experience"] = sum(r["duration_years"] for r in facts["experience_ranges"])
    
    return facts


def find_candidate_segments(requirement: str, segments: List[Dict[str, str]], top_k: int = 3) -> List[Dict[str, str]]:
    """
    Find the most relevant segments for a given requirement using keyword matching.
    
    Args:
        requirement: The requirement text to search for
        segments: List of {"id": "R#1", "text": "..."}
        top_k: Number of top candidates to return
        
    Returns:
        Top k most relevant segments
    """
    # Extract keywords from requirement (simple approach)
    req_lower = requirement.lower()
    req_keywords = set(re.findall(r'\b[a-z]{3,}\b', req_lower))
    
    # Score each segment
    scored_segments = []
    for seg in segments:
        text_lower = seg["text"].lower()
        
        # Count keyword matches
        matches = sum(1 for kw in req_keywords if kw in text_lower)
        
        # Bonus for exact phrase match
        if requirement[:20].lower() in text_lower:
            matches += 5
        
        if matches > 0:
            scored_segments.append({
                **seg,
                "match_score": matches
            })
    
    # Sort by score and return top k
    scored_segments.sort(key=lambda x: x["match_score"], reverse=True)
    return scored_segments[:top_k]

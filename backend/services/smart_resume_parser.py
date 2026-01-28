"""
Smart Resume Parser
Parses raw resume text and extracts structured data for PDF generation.
"""

import re


def parse_resume_text(text):
    """
    Parse raw resume text into structured data for professional PDF generation.
    
    Args:
        text: Raw resume text string
        
    Returns:
        dict with header and sections
    """
    lines = text.split('\n')
    
    # Extract header information (usually first few lines)
    header = extract_header(lines)
    
    # Parse into sections
    sections = extract_sections(lines)
    
    return {
        "header": header,
        "sections": sections
    }


def extract_header(lines):
    """Extract name, email, phone, location from top of resume."""
    header = {
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "links": []
    }
    
    # Look at first 10 lines for header info
    header_text = '\n'.join(lines[:10])
    
    # Extract email
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', header_text)
    if email_match:
        header["email"] = email_match.group(0)
    
    # Extract phone (various formats)
    phone_patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    ]
    for pattern in phone_patterns:
        phone_match = re.search(pattern, header_text)
        if phone_match:
            header["phone"] = phone_match.group(0)
            break
    
    # Extract LinkedIn/GitHub/Portfolio links
    link_patterns = [
        r'linkedin\.com/in/[\w-]+',
        r'github\.com/[\w-]+',
        r'(?:https?://)?(?:www\.)?[\w-]+\.(?:com|io|dev|net)/[\w-]+'
    ]
    for pattern in link_patterns:
        links = re.findall(pattern, header_text, re.IGNORECASE)
        header["links"].extend(links)
    
    # Extract name (usually first non-empty line)
    for line in lines[:5]:
        line = line.strip()
        if line and not any(x in line.lower() for x in ['email', '@', 'phone', 'http', '.com']):
            # Skip if it looks like a title or section header
            if len(line) < 50 and not line.isupper() or (line[0].isupper() and len(line.split()) <= 4):
                header["name"] = line
                break
    
    return header


def extract_sections(lines):
    """Extract resume sections (experience, education, skills, etc.)."""
    sections = []
    current_section = None
    current_content = []
    
    # Common section headers
    section_keywords = {
        'experience': ['experience', 'work history', 'employment', 'professional experience'],
        'education': ['education', 'academic', 'qualifications'],
        'skills': ['skills', 'technical skills', 'core competencies', 'expertise'],
        'projects': ['projects', 'key projects'],
        'summary': ['summary', 'profile', 'objective', 'about'],
        'certifications': ['certifications', 'certificates', 'licenses']
    }
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        if not line_stripped:
            continue
        
        # Check if this is a section header
        is_section_header = False
        section_type = None
        
        # All caps or title case with colons often indicates section
        if line_stripped.isupper() or line_stripped.endswith(':'):
            line_lower = line_stripped.lower().rstrip(':')
            for stype, keywords in section_keywords.items():
                if any(kw in line_lower for kw in keywords):
                    is_section_header = True
                    section_type = stype
                    break
        
        if is_section_header:
            # Save previous section
            if current_section:
                sections.append({
                    "type": current_section,
                    "content": '\n'.join(current_content).strip()
                })
            
            # Start new section
            current_section = section_type
            current_content = []
        else:
            # Add to current section content
            if current_section:
                current_content.append(line)
            elif i > 10:  # After header, create generic section
                if not current_section:
                    current_section = 'summary'
                current_content.append(line)
    
    # Add last section
    if current_section and current_content:
        sections.append({
            "type": current_section,
            "content": '\n'.join(current_content).strip()
        })
    
    # Parse structured content within sections
    for section in sections:
        if section["type"] == "experience":
            section["items"] = parse_experience_section(section["content"])
        elif section["type"] == "education":
            section["items"] = parse_education_section(section["content"])
        elif section["type"] == "skills":
            section["groups"] = parse_skills_section(section["content"])
        elif section["type"] == "projects":
            section["items"] = parse_projects_section(section["content"])
    
    return sections


def parse_experience_section(content):
    """Parse experience section into structured items."""
    items = []
    lines = content.split('\n')
    
    current_item = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect job title/company lines (often have | or dates)
        if '|' in line or re.search(r'\d{4}', line):
            # Save previous item
            if current_item:
                items.append(current_item)
            
            # Parse new item
            parts = [p.strip() for p in line.split('|')]
            current_item = {
                "title": parts[0] if parts else "",
                "company": parts[1] if len(parts) > 1 else "",
                "dates": parts[2] if len(parts) > 2 else extract_dates(line),
                "location": "",
                "bullets": []
            }
        elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
            # Bullet point
            if current_item:
                current_item["bullets"].append(line.lstrip('-•* '))
        elif current_item and not current_item["title"]:
            # First line after section header
            current_item["title"] = line
    
    if current_item:
        items.append(current_item)
    
    return items if items else None


def parse_education_section(content):
    """Parse education section into structured items."""
    items = []
    lines = content.split('\n')
    
    current_item = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Look for degree indicators
        if any(degree in line for degree in ['B.S.', 'M.S.', 'B.A.', 'M.A.', 'Ph.D.', 'Bachelor', 'Master', 'MBA']):
            if current_item:
                items.append(current_item)
            
            current_item = {
                "school": "",
                "degree": line,
                "dates": extract_dates(line)
            }
        elif '|' in line or 'University' in line or 'College' in line or 'Institute' in line:
            if current_item:
                items.append(current_item)
            
            parts = [p.strip() for p in line.split('|')]
            current_item = {
                "school": parts[0],
                "degree": parts[1] if len(parts) > 1 else "",
                "dates": parts[2] if len(parts) > 2 else extract_dates(line)
            }
        elif current_item and not current_item["school"]:
            current_item["school"] = line
    
    if current_item:
        items.append(current_item)
    
    return items if items else None


def parse_skills_section(content):
    """Parse skills section into groups."""
    groups = []
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line has a category (e.g., "Languages: Python, Java")
        if ':' in line:
            parts = line.split(':', 1)
            groups.append({
                "name": parts[0].strip(),
                "skills": [s.strip() for s in parts[1].split(',')]
            })
        else:
            # Just a list of skills
            skills = [s.strip() for s in re.split(r'[,;|]', line)]
            groups.append({
                "name": "Skills",
                "skills": skills
            })
    
    return groups if groups else None


def parse_projects_section(content):
    """Parse projects section into structured items."""
    items = []
    lines = content.split('\n')
    
    current_item = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Project name (often bold or first line)
        if line.startswith('-') or line.startswith('•') or line.startswith('*'):
            if current_item:
                current_item["bullets"].append(line.lstrip('-•* '))
        else:
            # New project
            if current_item:
                items.append(current_item)
            current_item = {
                "name": line,
                "bullets": []
            }
    
    if current_item:
        items.append(current_item)
    
    return items if items else None


def extract_dates(text):
    """Extract date range from text."""
    # Look for patterns like "2020-2023", "Jan 2020 - Present", etc.
    date_patterns = [
        r'\b\d{4}\s*-\s*(?:\d{4}|Present|Current)\b',
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*-\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|Present|Current)\b'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return ""

# Intelligent NLP-Based Extraction

## Overview
The application now uses **dynamic, JD-driven extraction** powered by Mistral LLM instead of static regex patterns. This extracts **whatever matters for EACH specific job**, not just pre-defined skills.

## What Changed

### Before (Rigid Extraction)
```python
# Fixed lists - missed anything not in these lists
SKILL_BANK = {'python', 'java', 'react', ...}  # Only 100 skills
TITLE_HINTS = ['software engineer', ...]        # Only 30 titles
```

**Problems:**
- ❌ Missed domain-specific skills (HIPAA, GDPR, SOX, etc.)
- ❌ Missed soft skills (stakeholder management, cross-functional)
- ❌ Missed company-specific tools (Salesforce, SAP, Workday)
- ❌ Missed certifications (AWS, CPA, PMP)
- ❌ Missed education requirements

### After (Intelligent Extraction)
```python
# LLM analyzes JD and extracts EVERYTHING relevant
jd_requirements = extract_jd_requirements(jd_text)
# Returns: required_skills, preferred_skills, soft_skills, tools, 
#          certifications, education, domain_knowledge, responsibilities, etc.

# LLM extracts qualifications from resume, focused on JD needs
resume_qualifications = extract_resume_qualifications(resume_text, jd_requirements)

# Intelligent gap analysis with specific matches
gap_analysis = intelligent_gap_analysis(jd_requirements, resume_qualifications)
```

## Features

### 1. Dynamic JD Analysis
Extracts 10 categories from **each job description**:
- **Required Skills**: Must-have technical skills
- **Preferred Skills**: Nice-to-have skills
- **Soft Skills**: Communication, leadership, teamwork
- **Tools & Technologies**: Specific platforms, frameworks, languages
- **Certifications**: AWS, CPA, PMP, etc.
- **Education**: Degree requirements
- **Experience Requirements**: Years, industries, roles
- **Responsibilities**: Key job duties
- **Domain Knowledge**: Healthcare, fintech, etc.
- **Keywords**: ATS optimization keywords

### 2. Focused Resume Extraction
Extracts qualifications from resume, **focusing on what the JD asked for**:
- Technical skills with context
- Achievements with metrics
- Projects with technologies
- Domain expertise demonstrated
- Certifications held
- Education background

### 3. Intelligent Gap Analysis
Returns structured analysis:
- **Strong Matches**: Requirements fully met (with evidence)
- **Partial Matches**: Requirements partially met (with explanation)
- **Critical Gaps**: Must-haves missing
- **Nice-to-Have Gaps**: Preferred requirements missing
- **Transferable Skills**: Skills that could apply
- **Match Score**: 0-100
- **Top 3 Actions**: Priority improvements

## API Usage

### Endpoint: `/api/improve-with-jd`
**Request:**
```bash
curl -X POST http://localhost:5002/api/improve-with-jd \
  -F "file=@resume.pdf" \
  -F "jd_text=Job description here..." \
  -F "use_intelligent=true"
```

**Response:**
```json
{
  "success": true,
  "score": 72,
  "analysis": "Full text analysis...",
  "suggestions": [...],
  "intelligent_extraction": {
    "jd_requirements": {
      "required_skills": ["Python", "SQL", "Data visualization"],
      "preferred_skills": ["Airflow", "Tableau"],
      "soft_skills": ["Stakeholder communication"],
      "tools_technologies": ["Snowflake", "dbt", "Looker"],
      "certifications": [],
      "education": ["BS in Computer Science or related field"],
      "experience_requirements": ["3+ years in data analysis"],
      "domain_knowledge": ["Healthcare domain experience preferred"],
      "keywords": ["Data-driven decision making", "ETL", "Data pipelines"]
    },
    "resume_qualifications": {
      "technical_skills": ["Python", "SQL", "pandas", "NumPy"],
      "tools_technologies": ["Jupyter", "Git", "PostgreSQL"],
      "certifications": [],
      "education": ["BS Computer Science, MIT"],
      "experience_details": ["2 years at tech startup"],
      "achievements": ["Reduced query time by 40%"],
      "domain_knowledge": ["E-commerce analytics"]
    },
    "gap_analysis": {
      "strong_matches": [
        "Python: Candidate has 2 years Python experience with data libraries",
        "SQL: Strong SQL skills demonstrated with performance optimization"
      ],
      "partial_matches": [
        "Data visualization: Has basic Matplotlib, but lacks Tableau"
      ],
      "critical_gaps": [
        "Healthcare domain: Candidate has e-commerce, not healthcare",
        "Snowflake: No cloud data warehouse experience"
      ],
      "nice_to_have_gaps": [
        "Airflow: No workflow orchestration tool experience",
        "Tableau: Uses Matplotlib instead"
      ],
      "transferable_skills": [
        "E-commerce analytics → Healthcare: Data analysis skills transfer"
      ],
      "match_score": 68,
      "top_3_actions": [
        "Add healthcare domain keywords throughout resume",
        "Highlight any healthcare projects or interest",
        "Add cloud data tools (Snowflake, Redshift) to skills if any exposure"
      ]
    }
  }
}
```

## UI Display

The frontend **Match Overview** tab now shows:

### With Intelligent Data:
```
✓ Strong Matches (3)
- Python: 2 years experience with data libraries
- SQL: Strong skills with performance optimization  
- Bachelor's degree: BS in Computer Science from MIT

⚠️ Critical Gaps (2)
- Healthcare domain experience required
- Snowflake experience missing

◐ Partial Matches (2)
- Data visualization: Has Matplotlib but lacks Tableau
- Experience level: 2 years vs 3+ preferred

🎯 Top Priority Actions
1. Add healthcare domain keywords throughout resume
2. Highlight any healthcare projects or interest
3. Add cloud data tools to skills section
```

### Without Intelligent Data (Fallback):
Falls back to basic analysis with simple strengths/gaps extraction from text.

## Performance

**Latency:** ~20-30 seconds total per analysis
- JD requirements extraction: ~5-8 seconds
- Resume qualifications extraction: ~5-8 seconds  
- Gap analysis: ~5-8 seconds
- Bullet suggestions: ~5-8 seconds

**Token Usage:** ~4,000-6,000 tokens per complete analysis (local, $0 cost)

## Benefits

1. **Job-Specific**: Extracts what matters for THIS role, not generic skills
2. **Comprehensive**: Finds soft skills, domain knowledge, certifications
3. **Actionable**: Tells you exactly what's strong vs. what's missing
4. **ATS-Aware**: Identifies keywords that matter for this specific JD
5. **Intelligent Matching**: Understands partial matches and transferable skills
6. **Zero Cost**: Runs locally on Mistral via Ollama

## Configuration

Enable/disable intelligent extraction:
```bash
# Enable (default)
use_intelligent=true

# Disable (use basic regex extraction)
use_intelligent=false
```

## Files

**Backend:**
- `backend/services/intelligent_extractor.py` - Core extraction logic
- `backend/app.py` - Integration in `/api/improve-with-jd`

**Frontend:**
- `frontend/src/components/InsightsPanel.jsx` - Display logic

## Future Enhancements

- [ ] Cache JD requirements for same job (avoid re-extraction)
- [ ] Add visual comparison charts (radar charts for skills)
- [ ] Export gap analysis as PDF report
- [ ] Benchmark matching accuracy
- [ ] Add more extraction categories (languages, industries, company size)

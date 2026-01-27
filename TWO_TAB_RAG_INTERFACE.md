# Two-Tab RAG Interface

## Overview
Complete UI redesign with two distinct tabs powered by RAG (Retrieval-Augmented Generation):

1. **Find Top Resumes** - RAG search over 10,730 indexed resumes
2. **Improve My Resume** - AI-powered resume improvement with intelligent extraction

## Tab 1: Find Top Resumes 🔍

### Purpose
Search the entire resume database to find the best matches for a job description using semantic search + LLM insights.

### How It Works (RAG Pipeline)

#### Step 1: RETRIEVE
```python
# Semantic search using sentence-transformers
hits = index.query_similar(jd_text, top_k=10)
# Returns top N resumes by cosine similarity
```

#### Step 2: AUGMENT
```python
# Extract JD requirements
jd_skills = infer_jd_skills(jd_text)
jd_title = infer_jd_title(jd_text)

# Build context from top resumes
resume_context = """
Resume 1 (Match: 87%):
Skills: Python, SQL, Airflow, Spark
Title: Data Engineer
Experience: 5 years
...
"""
```

#### Step 3: GENERATE
```python
# LLM analyzes results and generates insights
prompt = f"""
JOB DESCRIPTION: {jd_text}
TOP MATCHING RESUMES: {resume_context}

Provide:
1. KEY_REQUIREMENTS: 5-8 most important qualifications
2. MATCH_SUMMARY: Why these resumes match well
3. COMMON_PATTERNS: What top resumes have in common
"""

rag_insights = call_mistral(prompt, ...)
```

### Features

**User Input:**
- Job description textarea
- Adjustable result count (5-50 resumes)
- Search button

**Results Display:**
- **RAG Insights Card**:
  - Key Requirements (tags)
  - Match Summary (one sentence)
  - Common Patterns
- **Resume Cards** (enhanced):
  - Similarity score
  - Skills, titles, years
  - Highlights extracted from text
  - Download button

### API Endpoint

**POST** `/api/search-resumes`

**Request:**
```json
{
  "jd_text": "Looking for Senior Data Engineer with Python, SQL, Spark...",
  "top_k": 10
}
```

**Response:**
```json
{
  "resumes": [
    {
      "id": "abc123",
      "text": "Full resume text...",
      "metadata": {
        "skills": ["Python", "SQL", "Spark"],
        "titles": ["Data Engineer"],
        "years": 5
      },
      "similarity_score": 87.3
    }
  ],
  "rag_insights": {
    "key_requirements": [
      "Python programming",
      "SQL and data modeling",
      "Spark/distributed computing",
      "Cloud platforms (AWS/GCP)",
      "5+ years experience"
    ],
    "match_summary": "Top resumes demonstrate strong data engineering backgrounds with Python/SQL and distributed systems experience",
    "common_patterns": [
      "All have 4+ years Python experience",
      "Experience with both SQL and NoSQL",
      "Cloud platform expertise (AWS or GCP)"
    ]
  },
  "query_jd": "Looking for Senior Data Engineer..."
}
```

---

## Tab 2: Improve My Resume ✨

### Purpose
Upload your resume + job description to get AI-powered improvement suggestions.

### How It Works

#### Standard Analysis (No RAG)
Uses intelligent extraction (from previous implementation):
- Extracts JD requirements dynamically
- Extracts resume qualifications
- Performs gap analysis
- Generates improvement suggestions

#### With RAG Enhancement (Optional)
```python
# 1. Find similar resumes
hits = index.query_similar(jd_text, top_k=5)

# 2. Extract good bullet examples
ref_examples = extract_relevant_bullet_examples(hits)
# Example: "- Increased pipeline efficiency by 40% using Spark optimization"

# 3. Use examples to inspire improvements
prompt = f"""
EXAMPLES FROM SUCCESSFUL RESUMES:
{ref_examples}

USER'S RESUME:
{resume_text}

Provide improvements inspired by these examples:
BEFORE: Worked on data pipelines
AFTER: Architected ETL pipelines processing 2TB daily, reducing latency 40%
INSPIRED_BY: Example 3
IMPACT: Shows scale and impact with metrics
"""
```

### Features

**User Input:**
- Resume file upload (PDF, DOCX, TXT)
- Job description textarea (optional)
- Analyze button

**Results Display:**
- **Split View** (when JD provided):
  - Left: JD with detected fields
  - Right: Resume preview (A4 template)
- **Match Overview Tab**:
  - Match score
  - Strong matches (✓)
  - Critical gaps (⚠️)
  - Partial matches (◐)
  - Top priority actions (🎯)
- **Suggestions Tab**:
  - BEFORE/AFTER comparisons
  - Word-level diffs
  - Apply/Copy buttons
- **References Tab**:
  - Top matching reference resumes
  - Inspiration for improvements

### API Endpoint

**POST** `/api/improve-with-jd`

**Request:** (FormData)
```
file: resume.pdf
jd_text: "Job description..."
use_intelligent: true
```

**Response:**
```json
{
  "success": true,
  "score": 72,
  "analysis": "Full text analysis...",
  "suggestions": [
    {
      "before": "Managed data projects",
      "after": "Led 3 data migration projects reducing costs 30%",
      "reason": "Adds specifics and metrics",
      "source": "Reference Resume 2"
    }
  ],
  "intelligent_extraction": {
    "gap_analysis": {
      "strong_matches": [...],
      "critical_gaps": [...],
      "match_score": 72
    }
  },
  "reference_resumes": [...]
}
```

---

## Architecture

### Frontend Structure
```
App.jsx (Main container with tabs)
├── FindTopResumes.jsx (Tab 1)
│   └── ReferenceResumeCard.jsx
└── ImproveResume.jsx (Tab 2)
    ├── JDPanel.jsx
    ├── ResumePreview.jsx
    └── InsightsPanel.jsx
        ├── Match Overview
        ├── Suggestions
        └── References
```

### Backend Structure
```
backend/
├── app.py (Flask endpoints)
└── services/
    ├── rag_engine.py (NEW) - RAG implementation
    │   ├── rag_search_resumes()
    │   ├── generate_search_insights()
    │   ├── rag_enhance_suggestions()
    │   └── extract_relevant_bullet_examples()
    ├── intelligent_extractor.py - Dynamic field extraction
    ├── vector_store.py - ChromaDB interface
    └── mistral_service.py - LLM calls via Ollama
```

---

## RAG Benefits

### Tab 1: Find Top Resumes
1. **Smarter Search**: Not just keyword matching, but semantic understanding
2. **Context-Aware**: LLM explains WHY resumes match
3. **Pattern Discovery**: Finds common traits in top candidates
4. **Requirement Extraction**: Auto-detects what matters for the role

### Tab 2: Improve My Resume
1. **Example-Driven**: Shows real bullets from successful resumes
2. **Proven Patterns**: Suggests improvements based on what worked
3. **Citation**: Traces suggestions back to reference resumes
4. **Metrics-Focused**: Examples include quantified achievements

---

## Performance

### Tab 1: Find Top Resumes
- **Retrieval**: ~0.5 seconds (vector search)
- **LLM Insights**: ~5-8 seconds (Mistral analysis)
- **Total**: ~6-8 seconds

### Tab 2: Improve My Resume
- **With JD**: ~30-40 seconds (multiple LLM calls)
- **Without JD**: ~10-15 seconds (basic analysis)

---

## Usage

### Access the App
```bash
# Frontend
http://localhost:3003

# Backend API
http://localhost:5002
```

### Tab 1: Find Top Resumes
1. Click "Find Top Resumes" tab
2. Paste job description
3. Adjust number of results (5-50)
4. Click "Search Resumes"
5. View RAG insights and matching resumes

### Tab 2: Improve My Resume
1. Click "Improve My Resume" tab
2. Upload resume file
3. (Optional) Paste job description
4. Click "Analyze"
5. View match score, gaps, and suggestions

---

## Future Enhancements

### Tab 1
- [ ] Filter by years of experience
- [ ] Filter by skills/certifications
- [ ] Export search results to CSV
- [ ] Save searches for later
- [ ] Compare multiple resumes side-by-side

### Tab 2
- [ ] Real-time resume editing
- [ ] Apply suggestions with one click
- [ ] Track improvements over time
- [ ] Export improved resume as PDF
- [ ] A/B test different versions

### RAG Improvements
- [ ] Cache LLM insights for same JDs
- [ ] Add reranking with cross-encoder
- [ ] Chunk resumes by section for better retrieval
- [ ] Build JD vector store for JD-to-JD search
- [ ] Add multi-query retrieval

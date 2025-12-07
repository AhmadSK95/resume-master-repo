# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a Resume Matcher application that analyzes resumes against job descriptions using semantic search and scoring algorithms. The system consists of a Flask backend API and a React frontend, with capabilities for resume text extraction, field parsing, vector embedding, and intelligent ranking.

## Architecture

### Backend (`backend/`)
- **Flask API** (`app.py`): Main server with `/api/health` and `/api/analyze` endpoints
- **Text Extraction** (`services/extract_text.py`): Handles PDF, DOCX, and text file parsing using pypdf and docx libraries
- **Field Extraction** (`services/extract_fields.py`): Rule-based extraction of skills, job titles, and experience years from resume text
- **Vector Store** (`services/vector_store.py`): ChromaDB-based semantic search using sentence-transformers for resume indexing and similarity matching
- **Scorer** (`services/scorer.py`): Multi-factor scoring algorithm combining semantic similarity (55%), keyword overlap (25%), title matching (15%), and experience alignment (5%)

### Frontend (`frontend/`)
- **React SPA**: Single-page application with minimal UI for job description input and results display
- **Components**: `PostBox.jsx` (main interface), `SettingsPanel.jsx` 
- **API Layer** (`api.js`): Handles backend communication

### Data Processing (`one_shot/`)
- **Dataset**: `UpdatedResumeDataSet.csv` with 962 resume samples across 25 job categories
- **Preprocessing**: Jupyter notebook for data exploration and LLM-based resume information extraction using Ollama

## Common Development Commands

### Backend Development
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies (inferred from imports)
pip install flask pypdf python-docx chromadb sentence-transformers scikit-learn rapidfuzz

# Run development server
python app.py
# Server runs on http://localhost:5000
```

### Frontend Development
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (React project structure suggests)
npm install

# Start development server
npm run dev
# Typically runs on http://localhost:3000
```

### Data Processing
```bash
# Navigate to one_shot directory for data experiments
cd one_shot

# Run Jupyter notebook for data preprocessing
jupyter notebook preprocess_csv.ipynb
```

## Key Technical Details

### Dependencies
**Backend**: Flask, pypdf, python-docx, chromadb, sentence-transformers, scikit-learn, rapidfuzz
**Frontend**: React, likely Vite-based build setup
**ML Model**: sentence-transformers/all-MiniLM-L6-v2 for embeddings

### Data Flow
1. Resume files are processed through text extraction pipeline
2. Fields (skills, titles, years) extracted using regex and keyword matching
3. Text embedded using sentence-transformers and stored in ChromaDB
4. Job descriptions analyzed similarly for semantic matching
5. Multi-factor scoring ranks candidates with explanations

### Scoring Algorithm
The scorer uses weighted combination of:
- **Vector similarity (55%)**: Semantic matching between JD and resume text
- **Keyword overlap (25%)**: Skills intersection between JD and resume
- **Title matching (15%)**: Job title similarity using fuzzy matching
- **Years experience (5%)**: Experience level alignment

### File Processing
- Supports PDF (pypdf), DOCX (python-docx), and plain text files
- Vector store persists to `../data/chroma` directory
- Resume indexing uses SHA256 hash of file path as unique identifier

## Development Notes

- ChromaDB vector store requires `../data/chroma` directory for persistence
- Frontend expects API at `VITE_API_URL` or defaults to `http://localhost:5000`
- Skills bank in `extract_fields.py` contains predefined technology keywords
- System designed for batch processing and real-time single resume analysis
- LLM integration available via Ollama for enhanced field extraction (experimental feature in notebook)
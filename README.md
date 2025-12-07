# 🤖 AI Resume Matcher

An intelligent resume matching system powered by OpenAI GPT-4 and vector embeddings. Upload resumes, query with natural language, and get AI-powered candidate recommendations.

## Features

- **📤 Resume Upload**: Upload PDF, DOCX, or TXT resumes with automatic indexing
- **🔍 Natural Language Queries**: Ask questions like "Find me Python developers with 5+ years experience"
- **🤖 GPT-4 Analysis**: Get detailed AI-powered insights on candidate matches
- **📊 Vector Search**: Semantic similarity matching using sentence-transformers
- **💾 Persistent Storage**: ChromaDB vector database with 962+ pre-indexed resumes

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone and setup:**
```bash
git clone <your-repo>
cd resume-master-repo-fresh
chmod +x setup.sh
./setup.sh
```

2. **Add your OpenAI API key:**
Edit `.env` and add:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

3. **Start the backend:**
```bash
cd backend
source venv/bin/activate
python app.py
```

4. **Start the frontend** (in a new terminal):
```bash
cd frontend
npm run dev
```

5. **Open your browser:**
```
http://localhost:3001
```

## Manual Setup

If the setup script doesn't work:

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Import the dataset
python import_resumes.py

# Start server
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Usage

### Query Mode
1. Click "🔍 Query Database" tab
2. Enter a natural language prompt:
   - "Find senior Python developers with machine learning experience"
   - "Who has experience with React and Node.js?"
   - "Show me data scientists with 5+ years experience"
3. Check "Use OpenAI GPT-4 Analysis" for detailed AI insights
4. Click "🚀 Search"

### Upload Mode
1. Click "📤 Upload Resume" tab
2. Select a PDF, DOCX, or TXT file
3. Optionally enable "Extract fields with OpenAI" for better accuracy
4. Click "📤 Upload & Index"

## API Endpoints

### `POST /api/query`
Query resumes with natural language.

**Request:**
```json
{
  "prompt": "Find Python developers",
  "top_k": 20,
  "use_openai": true
}
```

**Response:**
```json
{
  "prompt": "Find Python developers",
  "analysis": "Based on the candidates...",
  "model": "gpt-4",
  "top_matches": [...]
}
```

### `POST /api/upload`
Upload and index a resume.

**Request:**
- `multipart/form-data`
- `file`: Resume file (PDF/DOCX/TXT)
- `use_openai`: "true" or "false"

**Response:**
```json
{
  "success": true,
  "resume_id": "abc123...",
  "filename": "resume.pdf",
  "fields": {
    "skills": [...],
    "years_exp": 5
  }
}
```

### `GET /api/health`
Check system status.

**Response:**
```json
{
  "ok": true,
  "vector_db_count": 962
}
```

## Architecture

```
backend/
  ├── app.py                    # Flask API server
  ├── services/
  │   ├── extract_text.py       # PDF/DOCX parsing
  │   ├── extract_fields.py     # Regex-based field extraction
  │   ├── vector_store.py       # ChromaDB wrapper
  │   ├── scorer.py             # Multi-factor scoring
  │   └── openai_service.py     # OpenAI integration
  └── import_resumes.py         # Bulk import script

frontend/
  ├── src/
  │   ├── components/PostBox.jsx  # Main UI
  │   └── api.js                  # API client
  └── vite.config.js

data/
  ├── chroma/                   # Vector database
  └── uploads/                  # Uploaded resumes

one_shot/
  └── UpdatedResumeDataSet.csv  # 962 resume dataset
```

## Tech Stack

**Backend:**
- Flask + Flask-CORS
- OpenAI GPT-4 & GPT-3.5-turbo
- ChromaDB (vector database)
- sentence-transformers (embeddings)
- pypdf, python-docx (parsing)

**Frontend:**
- React 18
- Vite
- Vanilla CSS (inline styles)

## Configuration

Environment variables (`.env`):
```bash
OPENAI_API_KEY=sk-...           # Required
CHROMA_PERSIST_DIR=../data/chroma
UPLOAD_FOLDER=../data/uploads
FLASK_ENV=development
```

## Dataset

The included dataset (`one_shot/UpdatedResumeDataSet.csv`) contains 962 resumes across 25 job categories:
- Java Developer, Testing, DevOps, Python, Data Science
- Web Design, HR, Hadoop, Blockchain, ETL
- And more...

## Troubleshooting

**"No module named 'chromadb'"**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**"Vector DB: 0 resumes indexed"**
```bash
cd backend
source venv/bin/activate
python import_resumes.py
```

**"OpenAI API error"**
- Check your API key in `.env`
- Verify you have credits: https://platform.openai.com/usage

**CORS errors**
- Backend must run on port 5001
- Frontend must run on port 3001

## License

MIT

## Contributing

Pull requests welcome! Please ensure all tests pass and follow the existing code style.

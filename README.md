# Resume Master Repository

A full-stack resume matching application with Flask backend and React frontend.

## Features

- **Resume Analysis**: Extract and analyze resume content from PDF and DOCX files
- **Job Description Matching**: Match job descriptions with candidate resumes using semantic similarity
- **Skill Extraction**: Automatically identify technical skills from resumes and job descriptions
- **Scoring & Ranking**: Rank candidates based on multiple factors including skills, experience, and semantic match

## Architecture

- **Backend**: Flask API server (`/backend`)
  - Text extraction from PDF/DOCX files
  - Vector-based semantic search using ChromaDB
  - Skills and experience extraction
  - Candidate scoring and ranking

- **Frontend**: React application (`/frontend`)
  - Job description input interface
  - Resume path specification
  - Results display with match percentages and explanations

## Repository Access

Repository collaborators are documented in [`COLLABORATORS.yml`](./COLLABORATORS.yml). To add collaborators:

1. **GitHub Web Interface**: 
   - Go to Repository Settings > Manage access > Invite a collaborator
   - Enter the username and select appropriate role

2. **GitHub CLI**:
   ```bash
   gh api repos/AhmadSK95/resume-master-repo/collaborators/USERNAME -X PUT -f permission=ROLE
   ```

3. **GitHub API**:
   ```bash
   curl -X PUT \
     -H "Authorization: token YOUR_TOKEN" \
     -H "Accept: application/vnd.github.v3+json" \
     https://api.github.com/repos/AhmadSK95/resume-master-repo/collaborators/USERNAME \
     -d '{"permission":"ROLE"}'
   ```

See [`COLLABORATORS.yml`](./COLLABORATORS.yml) for current collaborator configuration.

## Development

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend Setup  
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/analyze` - Analyze job description and match with resumes
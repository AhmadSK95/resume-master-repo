# 🚀 Quick Start Guide

Get the AI Resume Matcher running in 5 minutes!

## Step 1: Setup Environment

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup (installs everything)
./setup.sh
```

The setup script will:
- Check for Python 3 and Node.js
- Create virtual environment for Python
- Install all dependencies
- Create `.env` file
- Offer to import the 962 resume dataset

## Step 2: Add Your OpenAI API Key

Edit the `.env` file:
```bash
nano .env
# or
open .env
```

Replace `your_openai_api_key_here` with your actual OpenAI API key.

Get a key here: https://platform.openai.com/api-keys

## Step 3: Start Backend

```bash
cd backend
source venv/bin/activate
python app.py
```

You should see:
```
* Running on http://0.0.0.0:5001
```

## Step 4: Start Frontend

Open a NEW terminal:

```bash
cd frontend
npm run dev
```

You should see:
```
Local: http://localhost:3001
```

## Step 5: Use the App

Open your browser to: **http://localhost:3001**

### Try These Examples:

**Query Mode:**
- "Find me Python developers with machine learning experience"
- "Who has experience with React and AWS?"
- "Show me senior engineers with 8+ years"
- "Find data scientists who know Spark and Hadoop"

**Upload Mode:**
- Upload a sample resume (PDF, DOCX, or TXT)
- Check "Extract fields with OpenAI" for better results
- The resume will be indexed and searchable immediately

## Troubleshooting

### "Vector DB: 0 resumes"
Run the import script:
```bash
cd backend
source venv/bin/activate
python import_resumes.py
```

### "OpenAI API error"
- Check your API key in `.env`
- Make sure you have credits: https://platform.openai.com/usage
- Try with a simpler model by editing `openai_service.py` (change gpt-4 to gpt-3.5-turbo)

### "Module not found"
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## What's Next?

- **Check the database**: The health endpoint shows how many resumes are indexed
- **Upload your own resumes**: Use the Upload tab to add more candidates
- **Customize prompts**: Try different questions to find the perfect candidate
- **Review the code**: Check `backend/services/openai_service.py` to customize AI behavior

## Example Prompts

**For Technical Roles:**
- "Find full-stack developers with React and Node.js experience"
- "Who has DevOps experience with Docker and Kubernetes?"
- "Show me backend engineers who know Python and SQL"

**For Specific Skills:**
- "Find candidates with blockchain experience"
- "Who knows machine learning and has worked with TensorFlow?"
- "Show me people with cloud experience (AWS, GCP, or Azure)"

**For Experience Level:**
- "Find senior engineers with 10+ years experience"
- "Who are junior developers with React skills?"
- "Show me mid-level Python developers"

**For Categories:**
- "Find data scientists"
- "Who are the Java developers in the database?"
- "Show me all testing/QA candidates"

## Architecture Overview

```
User Browser (localhost:3001)
    ↓
React Frontend (Vite)
    ↓ HTTP API calls
Flask Backend (localhost:5001)
    ↓
ChromaDB Vector Store ← sentence-transformers embeddings
    ↓
OpenAI GPT-4 ← Prompt + Retrieved Resumes
    ↓
AI-Powered Analysis → User
```

## Cost Estimate

With OpenAI:
- GPT-4: ~$0.01-0.05 per query (depending on prompt length)
- GPT-3.5-turbo: ~$0.001-0.005 per query

Without OpenAI (disable checkbox):
- Free! Uses only local vector search

## Need Help?

Check the full README.md for:
- API documentation
- Architecture details
- Configuration options
- Advanced usage

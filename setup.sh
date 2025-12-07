#!/bin/bash
# Setup script for AI Resume Matcher

set -e

echo "=== AI Resume Matcher Setup ==="
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check for Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Setup environment file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY"
    echo "   Open .env in a text editor and replace 'your_openai_api_key_here'"
    echo ""
    read -p "Press Enter after you've added your OpenAI API key..."
fi

# Backend setup
echo "🐍 Setting up Python backend..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
cd ..
echo "✅ Backend dependencies installed"

# Frontend setup
echo "📦 Setting up React frontend..."
cd frontend
npm install
cd ..
echo "✅ Frontend dependencies installed"

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/chroma
mkdir -p data/uploads
echo "✅ Data directories created"

# Import resumes
echo ""
echo "📊 Ready to import resume dataset?"
echo "   This will load 962 resumes into the vector database."
read -p "Import now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Importing resumes (this may take a few minutes)..."
    cd backend
    source venv/bin/activate
    python import_resumes.py
    cd ..
    echo "✅ Import complete!"
else
    echo "⏭️  Skipped. Run 'python backend/import_resumes.py' later to import."
fi

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "To start the application:"
echo "  1. Backend:  cd backend && source venv/bin/activate && python app.py"
echo "  2. Frontend: cd frontend && npm run dev"
echo ""
echo "Then open: http://localhost:3001"

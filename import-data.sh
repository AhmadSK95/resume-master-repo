#!/bin/bash
cd "$(dirname "$0")/backend"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run setup.sh first!"
    exit 1
fi

# Load environment variables
cd ..
export $(cat .env | grep -v '^#' | xargs)

# Import data
cd backend
echo "📊 Importing 962 resumes into vector database..."
python import_resumes.py

echo ""
echo "✅ Done! Vector database is ready."
echo "   Restart your backend if it's running."

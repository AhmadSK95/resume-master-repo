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

# Start backend
cd backend
echo "🚀 Starting Flask backend on port 5001..."
python app.py

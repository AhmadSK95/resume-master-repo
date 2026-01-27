#!/bin/bash
#
# Resume Indexing Script for Docker
# Indexes resumes from the dataResumes directory into ChromaDB running in Docker container
#

set -e

echo "════════════════════════════════════════════════════════════════════════════════"
echo "                    Resume Matcher - Indexing Script                            "
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if backend container is running
if ! docker ps | grep -q resume-matcher-backend; then
    echo "❌ Error: Backend container (resume-matcher-backend) is not running."
    echo "   Please start the application first with: docker-compose up -d"
    exit 1
fi

echo "✓ Docker is running"
echo "✓ Backend container is running"
echo ""

# Check if dataResumes directory exists
if [ ! -d "dataResumes" ]; then
    echo "❌ Error: dataResumes directory not found in current directory"
    echo "   Please make sure you're running this script from the project root"
    exit 1
fi

echo "✓ dataResumes directory found"
echo ""

# Show current database count
echo "📊 Current database status:"
CURRENT_COUNT=$(curl -s http://localhost:5002/api/health | jq -r '.vector_db_count' 2>/dev/null || echo "unknown")
echo "   Current resume count: $CURRENT_COUNT"
echo ""

# Copy indexing script to container
echo "📤 Copying indexing script to container..."
docker cp index_resumes.py resume-matcher-backend:/app/ >/dev/null
echo "   ✓ Script copied"

# Copy dataResumes directory to container if not already there
echo "📤 Copying dataResumes directory to container (this may take a moment)..."
docker cp dataResumes resume-matcher-backend:/app/ >/dev/null
echo "   ✓ Data copied"
echo ""

# Run the indexing script
echo "🚀 Starting indexing process..."
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

docker exec -it resume-matcher-backend python index_resumes.py

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "                         Indexing Process Complete                               "
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Show final database count
echo "📊 Final database status:"
FINAL_COUNT=$(curl -s http://localhost:5002/api/health | jq -r '.vector_db_count' 2>/dev/null || echo "unknown")
echo "   Final resume count: $FINAL_COUNT"
echo ""

if [ "$CURRENT_COUNT" != "unknown" ] && [ "$FINAL_COUNT" != "unknown" ]; then
    NEW_RESUMES=$((FINAL_COUNT - CURRENT_COUNT))
    echo "   ✅ Added $NEW_RESUMES new resumes to the database"
fi

echo ""
echo "✓ All done! Your resumes are now indexed and searchable."
echo "✓ Access the application at: http://localhost:3003"
echo ""

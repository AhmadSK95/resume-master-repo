#!/usr/bin/env python3
"""
Test script to verify ChromaDB persistence for resume data.
Tests adding resumes, querying, and verifying data persists after restart.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.vector_store import ResumeIndex

def test_persistence():
    print("=== ChromaDB Persistence Test ===\n")
    
    # Test 1: Add sample resumes
    print("Step 1: Initializing vector store and adding test data...")
    index = ResumeIndex(persist_dir="./data/chroma")
    
    test_resumes = [
        {
            "path": "/fake/path/resume1.pdf",
            "text": "Senior Python Developer with 5 years experience in Django, Flask, and machine learning. Expertise in building scalable APIs and data pipelines.",
            "metadata": {"name": "John Doe", "title": "Python Developer", "years": 5}
        },
        {
            "path": "/fake/path/resume2.pdf",
            "text": "Frontend Engineer specializing in React, TypeScript, and modern web development. 3 years building responsive user interfaces.",
            "metadata": {"name": "Jane Smith", "title": "Frontend Engineer", "years": 3}
        },
        {
            "path": "/fake/path/resume3.pdf",
            "text": "Full Stack Developer with Java, Spring Boot, and Angular experience. 7 years in enterprise software development.",
            "metadata": {"name": "Bob Wilson", "title": "Full Stack Developer", "years": 7}
        }
    ]
    
    for resume in test_resumes:
        rid = index.upsert_resume(resume["path"], resume["text"], resume["metadata"])
        print(f"  ✓ Added: {resume['metadata']['name']} (ID: {rid[:8]}...)")
    
    print(f"\nTotal resumes in collection: {index.col.count()}")
    
    # Test 2: Query the data
    print("\n" + "="*50)
    print("Step 2: Testing query functionality...")
    query = "Python backend developer with Flask experience"
    print(f"Query: '{query}'")
    
    results = index.query_similar(query, top_k=3)
    print(f"\nTop {len(results['ids'][0])} matches:")
    for i, (doc_id, distance, metadata) in enumerate(zip(
        results['ids'][0], 
        results['distances'][0],
        results['metadatas'][0]
    )):
        similarity_score = 1 - distance  # cosine distance to similarity
        print(f"  {i+1}. {metadata['name']} - {metadata['title']}")
        print(f"     Similarity: {similarity_score:.3f}")
    
    # Test 3: Verify persistence by creating new instance
    print("\n" + "="*50)
    print("Step 3: Testing persistence (creating new instance)...")
    
    # Create a new instance (simulates app restart)
    index2 = ResumeIndex(persist_dir="./data/chroma")
    count = index2.col.count()
    print(f"Resumes found after restart: {count}")
    
    if count == len(test_resumes):
        print("✓ SUCCESS: Data persisted correctly!")
    else:
        print(f"✗ WARNING: Expected {len(test_resumes)} resumes, found {count}")
    
    # Query again with new instance
    results2 = index2.query_similar(query, top_k=1)
    top_match = results2['metadatas'][0][0]
    print(f"Top match after restart: {top_match['name']} - {top_match['title']}")
    
    print("\n" + "="*50)
    print("Test completed! Check ./data/chroma/ directory for persisted files.")
    
    # Show what's in the data directory
    print("\nPersisted files:")
    for root, dirs, files in os.walk("./data/chroma"):
        for file in files:
            filepath = os.path.join(root, file)
            size = os.path.getsize(filepath)
            print(f"  {filepath} ({size} bytes)")

if __name__ == "__main__":
    test_persistence()

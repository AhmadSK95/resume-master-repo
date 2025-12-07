#!/usr/bin/env python3
"""
Bulk import script to load resumes from CSV into ChromaDB vector store.
Usage: python import_resumes.py
"""
import sys
import os
import pandas as pd
from services.vector_store import ResumeIndex
from services.extract_fields import extract_fields

def import_from_csv(csv_path, persist_dir="../data/chroma"):
    """Load resumes from CSV and index them in ChromaDB."""
    print(f"=== Resume Import Script ===\n")
    print(f"Loading resumes from: {csv_path}")
    
    # Load CSV
    df = pd.read_csv(csv_path)
    print(f"Found {len(df)} resumes in dataset")
    print(f"Categories: {df['Category'].nunique()}")
    
    # Initialize vector store
    print(f"\nInitializing vector store at: {persist_dir}")
    index = ResumeIndex(persist_dir=persist_dir)
    
    # Check existing count
    existing_count = index.col.count()
    print(f"Existing resumes in vector store: {existing_count}")
    
    # Import resumes
    print("\nImporting resumes...")
    imported = 0
    errors = 0
    
    for idx, row in df.iterrows():
        try:
            category = row['Category']
            resume_text = row['Resume']
            
            # Generate a unique path identifier
            resume_path = f"dataset/{category}/{idx}.txt"
            
            # Extract fields
            fields = extract_fields(resume_text, use_llm=False)
            
            # Prepare metadata (ChromaDB only accepts str, int, float, bool)
            metadata = {
                "filename": resume_path,
                "category": category,
                "skills": ",".join(fields.get("skills", [])),  # Convert list to comma-separated string
                "titles": ",".join(fields.get("titles", [])),  # Convert list to comma-separated string
                "years": fields.get("years_exp", 0),
                "dataset_index": int(idx)
            }
            
            # Upsert into vector store
            rid = index.upsert_resume(resume_path, resume_text, metadata)
            imported += 1
            
            if (imported % 100) == 0:
                print(f"  Processed {imported}/{len(df)} resumes...")
                
        except Exception as e:
            errors += 1
            if errors < 5:  # Only show first few errors
                print(f"  Error on row {idx}: {str(e)}")
    
    print(f"\n=== Import Complete ===")
    print(f"Successfully imported: {imported}")
    print(f"Errors: {errors}")
    print(f"Total resumes in vector store: {index.col.count()}")

if __name__ == "__main__":
    # Resolve absolute paths so persistence is consistent regardless of CWD
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_file = os.path.join(base_dir, "one_shot", "UpdatedResumeDataSet.csv")
    persist_dir = os.path.join(base_dir, "data", "chroma")

    # Allow override via env
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", persist_dir)

    if not os.path.exists(csv_file):
        print(f"ERROR: CSV file not found at {csv_file}")
        sys.exit(1)

    print(f"Using persist directory: {persist_dir}")
    import_from_csv(csv_file, persist_dir=persist_dir)

    try:
        # Verify the import worked
        from services.vector_store import ResumeIndex
        ri = ResumeIndex(persist_dir=persist_dir)
        print(f"Collection count after import: {ri.col.count()}")
    except Exception as e:
        print(f"Warning: couldn't verify: {e}")

    print("\n✓ Vector database is ready for querying!")

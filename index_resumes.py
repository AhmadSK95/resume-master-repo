#!/usr/bin/env python3
"""
Resume Indexing Script
Indexes all resumes from dataResumes directory into the ChromaDB vector store.
Handles both individual resume files (.pdf, .docx, .txt) and CSV files containing resume text.
"""

import os
import sys
import pandas as pd
import hashlib
from pathlib import Path
from datetime import datetime

# Add backend to path to import services
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.vector_store import ResumeIndex
from services.extract_text import load_and_clean
from services.extract_fields import extract_fields

def clean_csv_text(text):
    """Clean text from CSV that may have special formatting"""
    if not isinstance(text, str):
        return ""
    
    # Replace newlines with spaces
    text = text.replace('\\n', ' ').replace('\n', ' ')
    
    # Remove multiple spaces
    text = ' '.join(text.split())
    
    return text.strip()

def parse_csv_skills(skills_str):
    """Parse skills from CSV string format like "['Python', 'Java']" """
    if not isinstance(skills_str, str):
        return []
    
    # Remove brackets and quotes, split by comma
    skills_str = skills_str.strip("[]'\"")
    if not skills_str:
        return []
    
    skills = [s.strip().strip("'\"") for s in skills_str.split(',')]
    return [s for s in skills if s]

def index_individual_resumes(index: ResumeIndex, resumes_dir: Path):
    """Index individual resume files from directory"""
    print(f"\n[1/2] Indexing individual resume files from: {resumes_dir}")
    
    if not resumes_dir.exists():
        print(f"  ⚠ Directory not found: {resumes_dir}")
        return 0
    
    supported_extensions = {'.pdf', '.docx', '.txt', '.doc'}
    resume_files = [f for f in resumes_dir.iterdir() 
                   if f.is_file() and f.suffix.lower() in supported_extensions]
    
    print(f"  Found {len(resume_files)} resume files")
    
    indexed_count = 0
    failed_count = 0
    
    for i, resume_file in enumerate(resume_files, 1):
        try:
            # Extract text from file
            text = load_and_clean(str(resume_file))
            
            if not text or len(text.strip()) < 50:
                print(f"  ⚠ [{i}/{len(resume_files)}] Skipping {resume_file.name} - insufficient content")
                failed_count += 1
                continue
            
            # Extract fields
            fields = extract_fields(text)
            
            # Create metadata
            metadata = {
                "filename": resume_file.name,
                "source": "individual_file",
                "skills": ",".join(fields.get("skills", [])),
                "titles": ",".join(fields.get("titles", [])),
                "years_exp": fields.get("years_exp", 0),
                "indexed_at": datetime.now().isoformat()
            }
            
            # Index the resume
            resume_id = index.upsert_resume(str(resume_file), text, metadata)
            indexed_count += 1
            
            if indexed_count % 10 == 0:
                print(f"    ✓ Indexed {indexed_count}/{len(resume_files)} files...")
                
        except Exception as e:
            print(f"  ✗ [{i}/{len(resume_files)}] Failed to index {resume_file.name}: {str(e)}")
            failed_count += 1
    
    print(f"  ✓ Successfully indexed {indexed_count} individual resumes")
    if failed_count > 0:
        print(f"  ⚠ Failed to index {failed_count} files")
    
    return indexed_count

def index_csv_resumes(index: ResumeIndex, csv_path: Path):
    """Index resumes from CSV file"""
    print(f"\n[2/2] Indexing resumes from CSV: {csv_path.name}")
    
    if not csv_path.exists():
        print(f"  ⚠ CSV file not found: {csv_path}")
        return 0
    
    try:
        # Read CSV
        df = pd.read_csv(csv_path, encoding='utf-8', low_memory=False)
        print(f"  Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
        
        # Identify resume text column
        text_columns = [col for col in df.columns 
                       if 'resume' in col.lower() or 'text' in col.lower() or 'description' in col.lower()]
        
        # If no direct text column, build resume from structured fields
        if not text_columns:
            print(f"  ℹ No direct resume text column found. Building resume from structured fields...")
            
            # Define columns to combine for resume text
            resume_fields = [
                'career_objective',
                'skills',
                'educational_institution_name',
                'degree_names',
                'major_field_of_studies',
                'professional_company_names',
                'positions',
                'responsibilities',
                'certification_providers',
                'certification_skills'
            ]
            
            # Build combined text column
            def build_resume_text(row):
                parts = []
                for field in resume_fields:
                    if field in df.columns and pd.notna(row[field]):
                        val = str(row[field])
                        if val and val != 'N/A' and len(val) > 2:
                            parts.append(val)
                return ' '.join(parts)
            
            df['combined_text'] = df.apply(build_resume_text, axis=1)
            text_col = 'combined_text'
            print(f"  ✓ Created combined resume text from {len(resume_fields)} fields")
        else:
            text_col = text_columns[0]
            print(f"  Using column '{text_col}' for resume text")
        
        # Identify optional columns
        skills_col = next((col for col in df.columns if 'skill' in col.lower()), None)
        category_col = next((col for col in df.columns if 'category' in col.lower() or 'position' in col.lower()), None)
        
        indexed_count = 0
        failed_count = 0
        
        for idx, row in df.iterrows():
            try:
                # Get resume text
                resume_text = str(row[text_col]) if pd.notna(row[text_col]) else ""
                resume_text = clean_csv_text(resume_text)
                
                if not resume_text or len(resume_text) < 50:
                    failed_count += 1
                    continue
                
                # Extract fields from text
                fields = extract_fields(resume_text)
                
                # Parse skills from CSV if available
                csv_skills = []
                if skills_col and pd.notna(row[skills_col]):
                    csv_skills = parse_csv_skills(str(row[skills_col]))
                
                # Combine skills
                all_skills = list(set(fields.get("skills", []) + csv_skills))
                
                # Create unique ID based on content
                content_hash = hashlib.md5(resume_text.encode()).hexdigest()
                resume_id = f"csv_resume_{idx}_{content_hash[:8]}"
                
                # Create metadata
                metadata = {
                    "filename": f"csv_row_{idx}",
                    "source": "csv_file",
                    "csv_file": csv_path.name,
                    "row_index": int(idx),
                    "skills": ",".join(all_skills[:50]),  # Limit to 50 skills
                    "titles": ",".join(fields.get("titles", [])),
                    "years_exp": fields.get("years_exp", 0),
                    "indexed_at": datetime.now().isoformat()
                }
                
                # Add category if available
                if category_col and pd.notna(row[category_col]):
                    metadata["category"] = str(row[category_col])
                
                # Index the resume
                index.upsert_resume(resume_id, resume_text, metadata)
                indexed_count += 1
                
                if indexed_count % 100 == 0:
                    print(f"    ✓ Indexed {indexed_count}/{len(df)} CSV rows...")
                    
            except Exception as e:
                failed_count += 1
                if failed_count <= 5:  # Only show first 5 errors
                    print(f"  ✗ Row {idx}: {str(e)}")
        
        print(f"  ✓ Successfully indexed {indexed_count} resumes from CSV")
        if failed_count > 0:
            print(f"  ⚠ Skipped {failed_count} rows (insufficient content or errors)")
        
        return indexed_count
        
    except Exception as e:
        print(f"  ✗ Failed to process CSV: {str(e)}")
        return 0

def main():
    print("=" * 80)
    print("RESUME INDEXING SCRIPT")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize vector store
    print("\nInitializing ChromaDB vector store...")
    data_dir = os.path.join(os.path.dirname(__file__), 'data', 'chroma')
    index = ResumeIndex(persist_dir=data_dir)
    
    # Get current count
    current_count = index.col.count()
    print(f"  ✓ Vector store initialized")
    print(f"  ✓ Current resume count: {current_count}")
    
    # Define paths
    base_dir = Path(__file__).parent / 'dataResumes'
    resumes_dir = base_dir / 'Resumes'
    csv_file = base_dir / 'resume_data.csv'
    
    # Index individual files
    individual_count = index_individual_resumes(index, resumes_dir)
    
    # Index CSV files
    csv_count = index_csv_resumes(index, csv_file)
    
    # Final count
    final_count = index.col.count()
    new_resumes = final_count - current_count
    
    # Summary
    print("\n" + "=" * 80)
    print("INDEXING COMPLETE!")
    print("=" * 80)
    print(f"Individual files indexed: {individual_count}")
    print(f"CSV resumes indexed:      {csv_count}")
    print(f"Total new resumes:        {new_resumes}")
    print(f"Previous resume count:    {current_count}")
    print(f"New total resume count:   {final_count}")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == '__main__':
    main()

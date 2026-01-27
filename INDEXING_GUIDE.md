# Resume Indexing Guide

This guide explains how to index resumes from the `dataResumes` directory into the ChromaDB vector database running in Docker.

## Overview

The indexing system handles two types of resume sources:
1. **Individual Files** - PDF, DOCX, TXT, and DOC files in `dataResumes/Resumes/`
2. **CSV Data** - Structured resume data in `dataResumes/resume_data.csv`

All resumes are processed and indexed into a ChromaDB vector store using the `all-MiniLM-L6-v2` sentence-transformer model for semantic search capabilities.

## Quick Start

### Prerequisites
- Docker Desktop running
- Application containers running (`docker-compose up -d`)
- Resume files in `dataResumes/` directory

### Run Indexing

Simply execute the shell script:

```bash
./index_resumes.sh
```

This will:
1. ✅ Check Docker and container status
2. 📤 Copy the indexing script and data to the container
3. 🚀 Process all resumes from files and CSV
4. 📊 Show before/after resume counts
5. ✅ Confirm successful indexing

## Current Database Status

After indexing, your database contains:
- **Original resumes**: 962 (from UpdatedResumeDataSet.csv)
- **Individual files**: 224 resumes
- **CSV data**: 9,544 resumes
- **Total**: **10,730 resumes** indexed and searchable

## Directory Structure

```
dataResumes/
├── Resumes/                    # Individual resume files
│   ├── Abiral_Pandey_Fullstack_Java.docx
│   ├── Achyuth Resume_8.docx
│   └── ... (228 files total, 224 successfully indexed)
│
├── resume_data.csv            # 9,544 structured resume records
│                              # with fields: skills, career_objective,
│                              # education, positions, etc.
│
└── archive/                   # Archived data (not indexed)
```

## How It Works

### 1. Individual File Processing

For each file in `dataResumes/Resumes/`:
- **Text Extraction**: PDF/DOCX/TXT files are parsed using pypdf and python-docx
- **Field Extraction**: Skills, job titles, and years of experience are extracted
- **Embedding**: Text is converted to 384-dimensional vectors using sentence-transformers
- **Storage**: Stored in ChromaDB with metadata (filename, skills, titles, years_exp)

### 2. CSV Processing

For `dataResumes/resume_data.csv`:
- **Field Combination**: Multiple columns are combined into resume text:
  - career_objective
  - skills
  - educational_institution_name
  - degree_names
  - major_field_of_studies
  - professional_company_names
  - positions
  - responsibilities
  - certification_providers
  - certification_skills
- **Metadata Enrichment**: Skills from CSV are parsed and combined with extracted skills
- **Embedding & Storage**: Same process as individual files

### 3. Metadata Schema

Each indexed resume includes:
```python
{
    "filename": str,           # Original filename or "csv_row_N"
    "source": str,             # "individual_file" or "csv_file"
    "skills": str,             # Comma-separated skills list
    "titles": str,             # Comma-separated job titles
    "years_exp": int,          # Extracted years of experience
    "indexed_at": str,         # ISO timestamp
    "category": str,           # (CSV only) Job category
    "csv_file": str,           # (CSV only) Source CSV name
    "row_index": int           # (CSV only) Row number in CSV
}
```

## Advanced Usage

### Manual Indexing (Python)

If you need more control, run the Python script directly:

```bash
# Copy script and data to container
docker cp index_resumes.py resume-matcher-backend:/app/
docker cp dataResumes resume-matcher-backend:/app/

# Run indexing
docker exec -it resume-matcher-backend python index_resumes.py
```

### Re-indexing

The script uses `upsert` operations, so:
- **Same file/content**: Updates existing entry (no duplicates)
- **New file/content**: Creates new entry
- **Modified file**: Updates the existing entry

To re-index everything, simply run the script again. ChromaDB will update existing entries.

### Monitoring Progress

The script provides detailed progress updates:
```
[1/2] Indexing individual resume files from: /app/dataResumes/Resumes
  Found 228 resume files
    ✓ Indexed 10/228 files...
    ✓ Indexed 20/228 files...
    ...

[2/2] Indexing resumes from CSV: resume_data.csv
  Loaded CSV with 9544 rows and 35 columns
  ℹ No direct resume text column found. Building resume from structured fields...
  ✓ Created combined resume text from 10 fields
    ✓ Indexed 100/9544 CSV rows...
    ✓ Indexed 200/9544 CSV rows...
    ...
```

## Verification

### Check Database Count

```bash
curl http://localhost:5002/api/health | jq .
```

Expected output:
```json
{
  "ok": true,
  "vector_db_count": 10730
}
```

### Test Search

Use the frontend at http://localhost:3003 to:
1. Enter a job description
2. See ranked resume matches
3. Verify resumes from both sources appear in results

## Troubleshooting

### Container Not Running
```
Error: Backend container (resume-matcher-backend) is not running.
```
**Solution**: Start containers first
```bash
docker-compose up -d
```

### Docker Not Running
```
Error: Docker is not running.
```
**Solution**: Start Docker Desktop

### Insufficient Content Warning
```
⚠ Skipping employer_mounika details.docx - insufficient content
```
**Reason**: File has less than 50 characters of text after extraction
**Action**: No action needed - file is skipped automatically

### No Resume Text Column in CSV
```
ℹ No direct resume text column found. Building resume from structured fields...
```
**Reason**: CSV uses structured fields instead of a single text column
**Action**: Script automatically combines fields - no action needed

### Failed Indexing
If files fail to index:
1. Check file format (PDF, DOCX, TXT, DOC only)
2. Verify file is not corrupted
3. Check Docker logs: `docker logs resume-matcher-backend`

## Performance

- **Individual Files** (228 files): ~14 seconds
- **CSV Data** (9,544 rows): ~6-8 minutes
- **Total Time**: ~8-9 minutes for complete indexing

## Data Persistence

- Vector database is stored in `./data/chroma/` (mounted volume)
- Data persists across container restarts
- To reset database: `rm -rf data/chroma/` and restart containers

## Adding New Resumes

To add more resumes:

1. Place new files in `dataResumes/Resumes/`
2. Or add rows to `dataResumes/resume_data.csv`
3. Run `./index_resumes.sh`
4. New resumes will be automatically indexed

## Scripts Reference

### `index_resumes.py`
Main Python script that performs the indexing. Uses:
- `services/vector_store.py` - ChromaDB interface
- `services/extract_text.py` - PDF/DOCX text extraction
- `services/extract_fields.py` - Skills/titles/years extraction

### `index_resumes.sh`
Convenient bash wrapper that:
- Validates prerequisites
- Copies files to container
- Runs indexing
- Shows before/after statistics

## Integration with Application

The indexed resumes are immediately available for:
- Semantic search via `/api/analyze` endpoint
- Job description matching
- Skills-based filtering
- Experience-level ranking

All searches use cosine similarity on the 384-dimensional embeddings for fast, relevant results.

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Original dataset | 962 resumes |
| Individual files | 224 resumes |
| CSV records | 9,544 resumes |
| **Total indexed** | **10,730 resumes** |
| Failed/skipped | 4 files |
| Embedding model | all-MiniLM-L6-v2 |
| Embedding dimension | 384 |
| Search method | Cosine similarity |

Your resume database is now ready for production use! 🚀

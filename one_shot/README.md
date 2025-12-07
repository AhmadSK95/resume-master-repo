# Resume Data Processing with Sentence Transformers

This directory contains scripts and data for processing resume datasets using BERT-based sentence transformers.

## Overview

The resume data from `UpdatedResumeDataSet.csv` has been processed using **sentence-transformers** (specifically the `all-MiniLM-L6-v2` model) to generate semantic embeddings. This approach provides better semantic understanding compared to traditional keyword-based methods.

## Files

### Input Data
- **`UpdatedResumeDataSet.csv`** (3.0 MB) - Original dataset with 962 resumes across 25 job categories

### Processing Scripts
- **`process_resumes_with_bert.py`** - Python script to process resumes and generate embeddings
- **`preprocess_with_sentence_transformers.ipynb`** - Jupyter notebook version (interactive)
- **`preprocess_csv.ipynb`** - Legacy notebook (uses Ollama LLM for field extraction)

### Output Files (Generated)
1. **`processed_resumes_with_embeddings.csv`** (7.2 MB)
   - Complete dataset with all 384 embedding dimensions as columns
   - Columns: `resume_id`, `category`, `resume_text`, `embedding_0` to `embedding_383`
   
2. **`resume_embeddings.npy`** (1.4 MB)
   - NumPy array of embeddings only (962 x 384)
   - Fast loading for ML applications
   
3. **`resume_metadata.csv`** (2.9 MB)
   - Metadata without embeddings
   - Columns: `resume_id`, `category`, `resume_text`
   
4. **`processed_resumes_complete.pkl`** (4.3 MB)
   - Python pickle containing:
     - `metadata`: DataFrame with resume info
     - `embeddings`: NumPy array (962 x 384)
     - `embedding_dim`: 384
     - `model_name`: 'sentence-transformers/all-MiniLM-L6-v2'
     - `processed_date`: Timestamp of processing

## Technical Details

### Model Specifications
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Architecture**: BERT-based transformer
- **Embedding Dimension**: 384
- **Context Length**: Up to 512 tokens

### Data Statistics
- **Total Resumes**: 962
- **Categories**: 25 unique job categories
- **Text Length**: 
  - Mean: 3,090 characters
  - Median: 2,268 characters
  - Range: 124 to 14,552 characters
- **Embedding Statistics**:
  - Mean: -0.0006
  - Std: 0.051

### Category Distribution (Top 10)
1. Java Developer: 84
2. Testing: 70
3. DevOps Engineer: 55
4. Python Developer: 48
5. Web Designing: 45
6. HR: 44
7. Hadoop: 42
8. Blockchain: 40
9. ETL Developer: 40
10. Operations Manager: 40

## Usage

### Reprocess Data
To regenerate the embeddings:

```bash
cd one_shot
python3 process_resumes_with_bert.py
```

### Load Processed Data in Python

#### Option 1: Load complete pickle (recommended for analysis)
```python
import pickle

with open('processed_resumes_complete.pkl', 'rb') as f:
    data = pickle.load(f)

metadata = data['metadata']      # DataFrame with resume info
embeddings = data['embeddings']  # NumPy array (962, 384)
```

#### Option 2: Load CSV with embeddings
```python
import pandas as pd

df = pd.read_csv('processed_resumes_with_embeddings.csv')

# Separate metadata and embeddings
metadata = df[['resume_id', 'category', 'resume_text']]
embedding_cols = [col for col in df.columns if col.startswith('embedding_')]
embeddings = df[embedding_cols].values
```

#### Option 3: Load separately (faster for large datasets)
```python
import pandas as pd
import numpy as np

metadata = pd.read_csv('resume_metadata.csv')
embeddings = np.load('resume_embeddings.npy')
```

### Use in Backend Application

The backend already uses the same model (`sentence-transformers/all-MiniLM-L6-v2`), so these embeddings can be directly loaded into ChromaDB or used for similarity search:

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Load model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Load pre-computed embeddings
embeddings = np.load('resume_embeddings.npy')

# For a new job description
job_desc = "Looking for Python developer with ML experience"
job_embedding = model.encode([job_desc])[0]

# Compute similarity with all resumes
from sklearn.metrics.pairwise import cosine_similarity
similarities = cosine_similarity([job_embedding], embeddings)[0]

# Get top matches
top_indices = similarities.argsort()[-10:][::-1]
```

## Advantages of This Approach

1. **Semantic Understanding**: Captures meaning beyond keywords
2. **Consistent Dimensions**: Fixed 384-dimensional vectors for all resumes
3. **Pre-computed**: Embeddings generated once, reused multiple times
4. **Efficient Storage**: Multiple formats for different use cases
5. **Compatible**: Same model as backend for consistency
6. **Scalable**: Batch processing with progress tracking

## Notes

- The embedding generation takes approximately 3-5 minutes for 962 resumes
- Processing is done in batches of 32 for memory efficiency
- All text is cleaned (newlines removed, whitespace normalized) before embedding
- The model automatically handles text truncation for resumes longer than 512 tokens

## Dependencies

```bash
pip install pandas numpy sentence-transformers scikit-learn
```

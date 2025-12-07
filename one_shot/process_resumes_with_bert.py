#!/usr/bin/env python3
"""
Resume Processing with Sentence Transformers (BERT)
This script processes resume data from UpdatedResumeDataSet.csv using sentence-transformers.
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import datetime
import pickle
import os

def clean_text(text):
    """Clean resume text for better embedding quality"""
    if not isinstance(text, str):
        return ""
    
    # Replace newlines with spaces
    text = text.replace('\n', ' ').replace('\\n', ' ')
    
    # Remove multiple spaces
    text = ' '.join(text.split())
    
    return text.strip()

def main():
    print("=" * 80)
    print("RESUME PROCESSING WITH SENTENCE TRANSFORMERS")
    print("=" * 80)
    
    # Load raw data
    print("\n[1/6] Loading raw resume dataset...")
    raw_data = pd.read_csv('UpdatedResumeDataSet.csv')
    print(f"  ✓ Loaded {len(raw_data)} resumes")
    print(f"  ✓ Columns: {raw_data.columns.tolist()}")
    print(f"\n  Category distribution:")
    for category, count in raw_data['Category'].value_counts().head(10).items():
        print(f"    - {category}: {count}")
    
    # Initialize model
    print("\n[2/6] Loading sentence transformer model...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embedding_dim = model.get_sentence_embedding_dimension()
    print(f"  ✓ Model loaded: all-MiniLM-L6-v2")
    print(f"  ✓ Embedding dimension: {embedding_dim}")
    
    # Clean text
    print("\n[3/6] Cleaning resume text...")
    raw_data['Resume_Cleaned'] = raw_data['Resume'].apply(clean_text)
    empty_resumes = raw_data[raw_data['Resume_Cleaned'] == '']
    print(f"  ✓ Text cleaned for all resumes")
    print(f"  ✓ Empty resumes after cleaning: {len(empty_resumes)}")
    
    text_lengths = raw_data['Resume_Cleaned'].str.len()
    print(f"  ✓ Text length stats: mean={text_lengths.mean():.0f}, "
          f"median={text_lengths.median():.0f}, "
          f"min={text_lengths.min()}, max={text_lengths.max()}")
    
    # Generate embeddings
    print("\n[4/6] Generating embeddings...")
    print(f"  Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    batch_size = 32
    embeddings_list = []
    
    for i in range(0, len(raw_data), batch_size):
        batch_texts = raw_data['Resume_Cleaned'][i:i+batch_size].tolist()
        batch_embeddings = model.encode(batch_texts, show_progress_bar=False)
        embeddings_list.append(batch_embeddings)
        
        if (i // batch_size + 1) % 10 == 0:
            print(f"    Processed {i + len(batch_texts)}/{len(raw_data)} resumes")
    
    embeddings = np.vstack(embeddings_list)
    
    print(f"  ✓ Completed at: {datetime.now().strftime('%H:%M:%S')}")
    print(f"  ✓ Embeddings shape: {embeddings.shape}")
    print(f"  ✓ Statistics: mean={embeddings.mean():.4f}, std={embeddings.std():.4f}")
    
    # Create processed dataframe
    print("\n[5/6] Creating processed dataframe...")
    
    # Create column names for embeddings
    embedding_columns = [f'embedding_{i}' for i in range(embedding_dim)]
    
    # Create dataframe with metadata
    processed_data = pd.DataFrame({
        'resume_id': range(len(raw_data)),
        'category': raw_data['Category'],
        'resume_text': raw_data['Resume_Cleaned']
    })
    
    # Add embedding columns
    embedding_df = pd.DataFrame(embeddings, columns=embedding_columns)
    processed_data = pd.concat([processed_data, embedding_df], axis=1)
    
    print(f"  ✓ Processed data shape: {processed_data.shape}")
    print(f"  ✓ Total columns: {len(processed_data.columns)}")
    print(f"    - Metadata columns: 3")
    print(f"    - Embedding columns: {embedding_dim}")
    
    # Save files
    print("\n[6/6] Saving processed data...")
    
    # 1. Full CSV with embeddings
    output_csv = 'processed_resumes_with_embeddings.csv'
    processed_data.to_csv(output_csv, index=False)
    size_mb = os.path.getsize(output_csv) / (1024*1024)
    print(f"  ✓ Saved: {output_csv} ({size_mb:.2f} MB)")
    
    # 2. NumPy embeddings only
    output_npy = 'resume_embeddings.npy'
    np.save(output_npy, embeddings)
    size_mb = os.path.getsize(output_npy) / (1024*1024)
    print(f"  ✓ Saved: {output_npy} ({size_mb:.2f} MB)")
    
    # 3. Metadata only
    metadata_df = processed_data[['resume_id', 'category', 'resume_text']].copy()
    output_metadata = 'resume_metadata.csv'
    metadata_df.to_csv(output_metadata, index=False)
    size_mb = os.path.getsize(output_metadata) / (1024*1024)
    print(f"  ✓ Saved: {output_metadata} ({size_mb:.2f} MB)")
    
    # 4. Complete pickle
    output_pickle = 'processed_resumes_complete.pkl'
    with open(output_pickle, 'wb') as f:
        pickle.dump({
            'metadata': metadata_df,
            'embeddings': embeddings,
            'embedding_dim': embedding_dim,
            'model_name': 'sentence-transformers/all-MiniLM-L6-v2',
            'processed_date': datetime.now().isoformat()
        }, f)
    size_mb = os.path.getsize(output_pickle) / (1024*1024)
    print(f"  ✓ Saved: {output_pickle} ({size_mb:.2f} MB)")
    
    # Verification
    print("\n[VERIFICATION] Testing data loading...")
    test_csv = pd.read_csv(output_csv)
    test_npy = np.load(output_npy)
    with open(output_pickle, 'rb') as f:
        test_pickle = pickle.load(f)
    
    print(f"  ✓ CSV loaded: {test_csv.shape}")
    print(f"  ✓ NumPy loaded: {test_npy.shape}")
    print(f"  ✓ Pickle loaded: metadata={test_pickle['metadata'].shape}, "
          f"embeddings={test_pickle['embeddings'].shape}")
    
    # Summary
    print("\n" + "=" * 80)
    print("PROCESSING COMPLETE!")
    print("=" * 80)
    print(f"Total resumes processed: {len(processed_data)}")
    print(f"Embedding model: sentence-transformers/all-MiniLM-L6-v2")
    print(f"Embedding dimension: {embedding_dim}")
    print(f"Categories: {processed_data['category'].nunique()}")
    print(f"\nOutput files created:")
    print(f"  1. {output_csv} - Full data with embeddings")
    print(f"  2. {output_npy} - Embeddings array (NumPy)")
    print(f"  3. {output_metadata} - Metadata only")
    print(f"  4. {output_pickle} - Complete dataset (pickle)")
    print("=" * 80)

if __name__ == '__main__':
    main()

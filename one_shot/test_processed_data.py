#!/usr/bin/env python3
"""
Quick test to verify the processed resume data
"""

import pandas as pd
import numpy as np
import pickle

print("Testing processed resume data...")
print("=" * 60)

# Test 1: Load pickle
print("\n1. Loading pickle file...")
with open('processed_resumes_complete.pkl', 'rb') as f:
    data = pickle.load(f)

print(f"   ✓ Metadata shape: {data['metadata'].shape}")
print(f"   ✓ Embeddings shape: {data['embeddings'].shape}")
print(f"   ✓ Model: {data['model_name']}")
print(f"   ✓ Processed: {data['processed_date']}")

# Test 2: Load CSV
print("\n2. Loading CSV file...")
df = pd.read_csv('processed_resumes_with_embeddings.csv')
print(f"   ✓ CSV shape: {df.shape}")
print(f"   ✓ Sample columns: {list(df.columns[:5])} ... {list(df.columns[-3:])}")

# Test 3: Load NumPy
print("\n3. Loading NumPy embeddings...")
embeddings = np.load('resume_embeddings.npy')
print(f"   ✓ NumPy shape: {embeddings.shape}")

# Test 4: Load metadata
print("\n4. Loading metadata CSV...")
metadata = pd.read_csv('resume_metadata.csv')
print(f"   ✓ Metadata shape: {metadata.shape}")
print(f"   ✓ Columns: {list(metadata.columns)}")

# Test 5: Verify embedding dimensions
print("\n5. Verifying embedding dimensions...")
embedding_cols = [col for col in df.columns if col.startswith('embedding_')]
print(f"   ✓ Number of embedding columns in CSV: {len(embedding_cols)}")
print(f"   ✓ NumPy embedding dimension: {embeddings.shape[1]}")
print(f"   ✓ Pickle embedding dimension: {data['embedding_dim']}")

# Test 6: Sample data
print("\n6. Sample resume data...")
print(f"   Category: {metadata['category'][0]}")
print(f"   Resume (first 100 chars): {metadata['resume_text'][0][:100]}...")
print(f"   Embedding (first 5 values): {embeddings[0][:5]}")

# Test 7: Verify consistency
print("\n7. Verifying data consistency...")
assert len(metadata) == len(embeddings), "Metadata and embeddings length mismatch!"
assert embeddings.shape == data['embeddings'].shape, "NumPy and pickle embeddings shape mismatch!"
assert len(df) == len(metadata), "CSV and metadata length mismatch!"
print("   ✓ All data files are consistent!")

print("\n" + "=" * 60)
print("✅ All tests passed! Data is ready to use.")
print("=" * 60)

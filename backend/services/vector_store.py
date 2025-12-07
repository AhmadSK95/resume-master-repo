import chromadb
from sentence_transformers import SentenceTransformer
import hashlib
import os

MODEL = "all-MiniLM-L6-v2"

class ResumeIndex:
    def __init__(self, persist_dir="../data/chroma"):
        # Normalize persist_dir to absolute path to avoid cwd issues
        self.persist_dir = os.path.abspath(persist_dir)
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # Use PersistentClient for automatic persistence
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.col = self.client.get_or_create_collection(
            name="resumes",
            metadata={"hnsw:space": "cosine"}
        )
        self.model = SentenceTransformer(MODEL)

    def _embed(self, texts):
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def _id(self, key:bytes):
        return hashlib.sha256(key).hexdigest()

    def upsert_resume(self, resume_path:str, text:str, metadata:dict):
        rid = self._id(resume_path.encode())
        self.col.upsert(ids=[rid], documents=[text], metadatas=[metadata], embeddings=self._embed([text]))
        return rid

    def query_similar(self, jd_text: str, top_k: int = 30, where=None):
        q = self._embed([jd_text])[0]
        return self.col.query(query_embeddings=[q], n_results=top_k, where=where)

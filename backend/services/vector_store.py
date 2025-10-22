import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import hashlib

MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# MODEL = "sentence-transformers/all-mpnet-base-v2"
# Model
class ResumeIndex:
    def __init__(self, persist_dir="../data/chroma"):
        self.client = chromadb.Client(Settings(persist_directory=persist_dir, anonymized_telemetry=False))
        self.col = self.client.get_or_create_collection(name="resumes", metadata={"hnsw:space":"cosine"})
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

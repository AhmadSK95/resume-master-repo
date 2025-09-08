from pypdf import PdfReader
from docx import Document
import os

def read_pdf(path):
    text = []
    with open(path, 'rb') as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text.append(page.extract_text() or "")
    return "\n".join(text)

def read_docx(path):
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def load_and_clean(path:str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    ext = path.lower().split('.')[-1]
    if ext == 'pdf':
        raw = read_pdf(path)
    elif ext in ('docx',):
        raw = read_docx(path)
    else:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            raw = f.read()
    lines = [l.strip() for l in raw.splitlines()]
    lines = [l for l in lines if l]
    return "\n".join(lines)

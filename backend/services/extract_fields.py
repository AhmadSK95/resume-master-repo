import re
from rapidfuzz import fuzz

SKILL_BANK = {
  'python','java','c++','flask','django','react','node','aws','gcp','azure',
  'docker','kubernetes','sql','nosql','postgres','mysql','mongodb','rest','grpc',
  'lambda','s3','ec2','terraform','git','linux','pandas','spark','hadoop','airflow'
}

TITLE_HINTS = [
  'software engineer','sde','backend engineer','full stack','data engineer','ml engineer',
  'software developer','senior software','principal','lead engineer'
]

YEAR_RE = re.compile(r'(\d+)(?:\+)?\s*(?:years|yrs)')

def simple_skills(text:str):
    low = re.sub(r'[^a-z0-9\n ]+',' ', text.lower())
    toks = set(low.split())
    return sorted(list(SKILL_BANK & toks))

def simple_titles(text:str):
    low = text.lower()
    found = set()
    for t in TITLE_HINTS:
        if t in low:
            found.add(t)
    return sorted(list(found)) or ["unknown"]

def simple_years(text:str):
    vals = [int(m.group(1)) for m in YEAR_RE.finditer(text.lower())]
    return max(vals) if vals else 0

def extract_fields(text:str, use_llm:bool=False):
    return {
        "skills": simple_skills(text),
        "titles": simple_titles(text),
        "years_exp": simple_years(text)
    }

def infer_jd_skills(jd_text:str):
    return simple_skills(jd_text)

def infer_jd_title(jd_text:str):
    cands = simple_titles(jd_text)
    return cands[0] if cands else "software engineer"

def infer_req_years(jd_text:str):
    return simple_years(jd_text)

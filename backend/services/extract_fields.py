import re
from rapidfuzz import fuzz

SKILL_BANK = {
  # Languages
  'python','java','javascript','typescript','c++','c#','go','golang','rust','ruby',
  'php','swift','kotlin','scala','r','matlab','perl','shell','bash',
  # Frontend
  'react','vue','angular','svelte','html','css','sass','tailwind','bootstrap','jquery',
  'redux','nextjs','webpack','vite',
  # Backend
  'node','nodejs','express','flask','django','fastapi','spring','springboot',
  'rails','laravel','dotnet','aspnet',
  # Databases
  'sql','nosql','postgres','postgresql','mysql','mongodb','redis','cassandra',
  'dynamodb','elasticsearch','oracle','mssql','sqlite',
  # Cloud
  'aws','gcp','azure','lambda','s3','ec2','cloudfront','rds','redshift',
  'cloud','cloudformation','ecs','eks','fargate',
  # DevOps & Tools
  'docker','kubernetes','k8s','terraform','ansible','jenkins','circleci','github',
  'gitlab','git','linux','unix','nginx','apache','ci/cd','helm',
  # Data & ML
  'pandas','numpy','spark','hadoop','airflow','kafka','scikit-learn','tensorflow',
  'pytorch','keras','jupyter','tableau','powerbi','etl','databricks',
  # Other
  'rest','restful','api','graphql','grpc','microservices','agile','scrum','jira'
}

TITLE_HINTS = [
  # Software Engineering
  'software engineer','software developer','sde','engineer','developer','programmer',
  'backend engineer','frontend engineer','full stack','fullstack','devops engineer',
  'site reliability engineer','sre','platform engineer','systems engineer',
  # Data & ML
  'data engineer','data scientist','ml engineer','machine learning engineer','ai engineer',
  'data analyst','business analyst','analytics engineer','research scientist',
  # Management & Leadership
  'engineering manager','technical lead','tech lead','team lead','lead engineer',
  'staff engineer','principal engineer','senior engineer','architect','solutions architect',
  # Specialized
  'security engineer','qa engineer','test engineer','mobile developer','ios developer',
  'android developer','cloud engineer','infrastructure engineer','network engineer',
  # Other
  'product manager','project manager','scrum master','consultant','intern','associate'
]

YEAR_RE = re.compile(r'(\d+)(?:\+)?\s*(?:years|yrs)')

def simple_skills(text:str):
    low = re.sub(r'[^a-z0-9\n ]+',' ', text.lower())
    toks = set(low.split())
    return sorted(list(SKILL_BANK & toks))

def simple_titles(text:str):
    low = text.lower()
    found = set()
    
    # First try exact matches from TITLE_HINTS
    for t in TITLE_HINTS:
        if t in low:
            found.add(t)
    
    # If no matches found, try to extract lines that look like job titles
    # (capitalized phrases before company names or dates)
    if not found:
        lines = text.split('\n')
        for line in lines[:20]:  # Check first 20 lines
            line = line.strip()
            # Look for capitalized title-like patterns
            if line and len(line) < 80:
                # Check if line contains common title words
                if any(word in line.lower() for word in ['engineer', 'developer', 'manager', 'analyst', 'scientist', 'architect', 'lead', 'senior', 'junior']):
                    found.add(line.lower())
    
    return sorted(list(found)) if found else ["unknown"]

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

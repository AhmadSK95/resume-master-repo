const API = import.meta.env.VITE_API_URL || "http://localhost:5001";

export async function analyze(jdText, files) {
  const serverPaths = files.map(f => f.path || f);
  const res = await fetch(`${API}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jd_text: jdText, server_resume_paths: serverPaths, use_llm: false })
  });
  if (!res.ok) throw new Error(`Analyze failed: ${res.status}`);
  return res.json();
}

export async function analyzeResume(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API}/api/analyze-resume`, {
    method: "POST",
    body: formData
  });
  if (!res.ok) throw new Error(`Analyze resume failed: ${res.status}`);
  return res.json();
}

export async function improveResumeWithJD(file, jdText) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('jd_text', jdText);

  const res = await fetch(`${API}/api/improve-with-jd`, {
    method: "POST",
    body: formData
  });
  if (!res.ok) throw new Error(`Improve with JD failed: ${res.status}`);
  return res.json();
}

export async function findReferences({ query, topK = 10, includeComparison = false, userResumeText = "" }) {
  const res = await fetch(`${API}/api/find-references`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k: topK, include_comparison: includeComparison, user_resume_text: userResumeText })
  });
  if (!res.ok) throw new Error(`Find references failed: ${res.status}`);
  return res.json();
}

export async function renderPdf(title, content) {
  const res = await fetch(`${API}/api/render-pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, content })
  });
  if (!res.ok) throw new Error(`PDF render failed: ${res.status}`);
  const blob = await res.blob();
  return blob;
}

export async function queryWithPrompt(prompt, topK = 20, useOpenAI = true) {
  const res = await fetch(`${API}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, top_k: topK, use_openai: useOpenAI })
  });
  if (!res.ok) throw new Error(`Query failed: ${res.status}`);
  return res.json();
}

export async function checkHealth() {
  const res = await fetch(`${API}/api/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}

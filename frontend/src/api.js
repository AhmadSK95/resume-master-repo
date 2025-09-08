const API = import.meta.env.VITE_API_URL || "http://localhost:5000";

export async function analyze(jdText, files) {
  // We'll send file names only; for MVP, assume files are already on server (or add upload later)
  const serverPaths = files.map(f => f.path || f); // allow raw paths
  const res = await fetch(`${API}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jd_text: jdText, server_resume_paths: serverPaths, use_llm: false })
  });
  if (!res.ok) throw new Error(`Analyze failed: ${res.status}`);
  return res.json();
}

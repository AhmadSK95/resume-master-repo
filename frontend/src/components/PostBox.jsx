import { useState } from 'react';
import { analyze } from '../api';
export default function PostBox(){
  const [jd, setJd] = useState("");
  const [paths, setPaths] = useState(""); // comma‑sep server file paths for MVP
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

  const onAnalyze = async () => {
    setLoading(true); setError(""); setResults([]);
    try {
      const serverPaths = paths.split(",").map(s => s.trim()).filter(Boolean);
      const data = await analyze(jd, serverPaths);
      setResults(data.top_k || []);
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 max-w-3xl mx-auto">
      <h1>📮 Post‑Box Resume Matcher</h1>
      <label>Job Description</label>
      <textarea value={jd} onChange={e=>setJd(e.target.value)} rows={8} style={{width:'100%'}}/>

      <label className="block mt-3">Server Resume Paths (comma‑separated)</label>
      <input value={paths} onChange={e=>setPaths(e.target.value)} style={{width:'100%'}} placeholder="data/resumes/a.pdf, data/resumes/b.docx"/>

      <div className="mt-3">
        <button onClick={onAnalyze} disabled={loading || !jd}>
          {loading ? 'Analyzing…' : 'Analyze'}
        </button>
        <button onClick={()=>{setJd(""); setPaths(""); setResults([])}} className="ml-2">Clear</button>
      </div>

      {error && <p style={{color:'red'}}>{error}</p>}

      <div className="mt-4">
        {results.map((r)=> (
          <div key={r.resume_id} style={{border:'1px solid #ddd', borderRadius:8, padding:12, marginBottom:8}}>
            <div style={{display:'flex', justifyContent:'space-between'}}>
              <strong>{r.candidate_name || r.resume_id}</strong>
              <span>{Math.round((r.score||0)*100)}%</span>
            </div>
            <ul>
              {(r.why||[]).map((w,i)=>(<li key={i}>• {w}</li>))}
            </ul>
            {r.highlights?.skills_found?.length ? (
              <small>Skills: {r.highlights.skills_found.join(', ')}</small>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}

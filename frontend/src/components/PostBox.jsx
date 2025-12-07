import { useState, useEffect } from 'react';
import { analyzeResume, improveResumeWithJD, findReferences, renderPdf, checkHealth } from '../api';
import ReferenceResumeCard from './ReferenceResumeCard';
import ResumeViewer from './ResumeViewer';

export default function PostBox() {
  const [mode, setMode] = useState('improve'); // 'improve' or 'references'

  // Improve mode state
  const [file, setFile] = useState(null);
  const [jdText, setJdText] = useState("");
  const [analysisData, setAnalysisData] = useState(null);
  const [userResumeText, setUserResumeText] = useState("");

  // References mode state
  const [prompt, setPrompt] = useState("");
  const [includeComparison, setIncludeComparison] = useState(true);
  const [referencesData, setReferencesData] = useState(null);

  // Globals
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [dbCount, setDbCount] = useState(0);

  useEffect(() => {
    checkHealth().then(data => setDbCount(data.vector_db_count || 0)).catch(() => {});
  }, [analysisData]);

  const onAnalyzeResume = async () => {
    if (!file) return;
    setLoading(true); setError("");
    try {
      let data;
      if (jdText.trim()) {
        // Use JD-enhanced analysis
        data = await improveResumeWithJD(file, jdText);
      } else {
        // Use basic analysis
        data = await analyzeResume(file);
      }
      setAnalysisData(data);
      setUserResumeText(data.resume_text_full || '');
      setFile(null);
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setLoading(false);
    }
  };

  const onFindReferences = async () => {
    if (!prompt.trim()) return;
    setLoading(true); setError("");
    try {
      const data = await findReferences({
        query: prompt,
        topK: 10,
        includeComparison: includeComparison && !!userResumeText,
        userResumeText
      });
      setReferencesData(data);
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setLoading(false);
    }
  };

  const onDownloadPdf = async (title, content) => {
    try {
      const blob = await renderPdf(title, content);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${title.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(String(e.message || e));
    }
  };

  return (
    <div style={{maxWidth: 900, margin: '0 auto', padding: 24, fontFamily: 'system-ui'}}>
      <h1 style={{fontSize: 32, marginBottom: 8}}>🧠 AI Resume Coach</h1>
      <p style={{color: '#666', marginBottom: 24}}>Reference DB: {dbCount} resumes indexed</p>

      {/* Mode Tabs */}
      <div style={{marginBottom: 24, borderBottom: '2px solid #eee'}}>
        <button 
          onClick={() => setMode('improve')}
          style={{
            padding: '10px 20px',
            border: 'none',
            background: mode === 'improve' ? '#007bff' : 'transparent',
            color: mode === 'improve' ? 'white' : '#333',
            cursor: 'pointer',
            marginRight: 8
          }}
        >
          ✨ Improve My Resume
        </button>
        <button 
          onClick={() => setMode('references')}
          style={{
            padding: '10px 20px',
            border: 'none',
            background: mode === 'references' ? '#007bff' : 'transparent',
            color: mode === 'references' ? 'white' : '#333',
            cursor: 'pointer'
          }}
        >
          📚 Find Reference Resumes
        </button>
      </div>

      {/* Improve Mode */}
      {mode === 'improve' && (
        <div>
          <label style={{display: 'block', marginBottom: 8, fontWeight: 600}}>Upload your resume (PDF, DOCX, TXT):</label>
          <input 
            type="file" 
            accept=".pdf,.docx,.txt"
            onChange={e => setFile(e.target.files[0])}
            style={{marginBottom: 12, padding: 8}}
          />
          
          <label style={{display: 'block', marginTop: 16, marginBottom: 8, fontWeight: 600}}>Job Description (Optional - for tailored suggestions):</label>
          <textarea 
            value={jdText} 
            onChange={e => setJdText(e.target.value)}
            rows={6}
            placeholder="Paste the job description here to get targeted improvement suggestions and see matching reference resumes..."
            style={{width: '100%', padding: 12, fontSize: 14, borderRadius: 6, border: '1px solid #ddd', fontFamily: 'system-ui'}}
          />
          
          <div style={{marginTop: 12, display: 'flex', alignItems: 'center', gap: 16}}>
            <button 
              onClick={onAnalyzeResume}
              disabled={loading || !file}
              style={{
                padding: '10px 24px',
                background: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: 6,
                cursor: loading ? 'wait' : 'pointer',
                fontSize: 14,
                fontWeight: 600
              }}
            >
              {loading ? '⏳ Analyzing...' : (jdText.trim() ? '🎯 Analyze for Job' : '🔍 Analyze Resume')}
            </button>

            <button 
              onClick={() => { setAnalysisData(null); setUserResumeText(''); setJdText(''); setError(''); }}
              style={{
                padding: '10px 24px',
                background: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: 6,
                cursor: 'pointer',
                fontSize: 14
              }}
            >
              Clear
            </button>
          </div>

          {error && <p style={{color: 'red', marginTop: 16, padding: 12, background: '#fee', borderRadius: 6}}>{error}</p>}

          {analysisData && (
            <div style={{marginTop: 24}}>
              <div style={{display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12}}>
                <span style={{background: analysisData.score >= 70 ? '#28a745' : analysisData.score >= 50 ? '#ffc107' : '#dc3545', color: 'white', padding: '8px 16px', borderRadius: 20, fontWeight: 700, fontSize: 16}}>
                  {analysisData.jd_text ? 'Match Score' : 'Score'}: {analysisData.score}/100
                </span>
                <span style={{color: '#666', fontSize: 14}}>File: {analysisData.filename}</span>
              </div>
              
              <div style={{background: '#f0f9ff', padding: 20, borderRadius: 8, marginBottom: 16, border: '2px solid #007bff'}}>
                <h3 style={{marginTop: 0, color: '#007bff'}}>
                  {analysisData.jd_text ? '🎯 Job-Specific Insights' : '✨ AI Feedback'}
                </h3>
                <div style={{whiteSpace: 'pre-wrap', lineHeight: 1.6}}>{analysisData.analysis}</div>
              </div>

              {analysisData.fields && (
                <div style={{border: '1px solid #eee', padding: 12, borderRadius: 8, background: '#fff', marginBottom: 16}}>
                  <strong>Detected Fields:</strong>
                  <div style={{fontSize: 14, marginTop: 6}}>
                    <div><strong>Skills:</strong> {(analysisData.fields.skills || []).join(', ') || 'None detected'}</div>
                    <div><strong>Titles:</strong> {(analysisData.fields.titles || []).join(', ') || 'None detected'}</div>
                    <div><strong>Years:</strong> {analysisData.fields.years_exp || 0}</div>
                  </div>
                </div>
              )}

              {analysisData.reference_resumes && analysisData.reference_resumes.length > 0 && (
                <div style={{marginTop: 24}}>
                  <h3 style={{color: '#333'}}>📚 Top Reference Resumes for This Job</h3>
                  <p style={{color: '#666', fontSize: 14, marginBottom: 16}}>These resumes from our database match the job description well. Use them as inspiration for improvements.</p>
                  {analysisData.reference_resumes.map((ref, idx) => (
                    <ReferenceResumeCard
                      key={idx}
                      reference={ref}
                      index={idx}
                      onDownloadPdf={onDownloadPdf}
                    />
                  ))}
                </div>
              )}

              <ResumeViewer
                resumeText={analysisData.resume_text_full}
                filepath={analysisData.filepath}
              />
            </div>
          )}
        </div>
      )}

      {/* References Mode */}
      {mode === 'references' && (
        <div>
          <label style={{display: 'block', marginBottom: 8, fontWeight: 600}}>Describe the reference resume you want:</label>
          <textarea 
            value={prompt} 
            onChange={e => setPrompt(e.target.value)}
            rows={4}
            placeholder="E.g., Senior Python backend engineer with ML and 5+ years"
            style={{width: '100%', padding: 12, fontSize: 14, borderRadius: 6, border: '1px solid #ddd'}}
          />

          <div style={{marginTop: 12, display: 'flex', alignItems: 'center', gap: 16}}>
            <label style={{display: 'flex', alignItems: 'center', gap: 6}}>
              <input 
                type="checkbox" 
                checked={includeComparison && !!userResumeText}
                onChange={e => setIncludeComparison(e.target.checked)}
                disabled={!userResumeText}
              />
              Compare with my uploaded resume
            </label>

            <button 
              onClick={onFindReferences}
              disabled={loading || !prompt.trim()}
              style={{
                padding: '10px 24px',
                background: '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: 6,
                cursor: loading ? 'wait' : 'pointer',
                fontSize: 14,
                fontWeight: 600
              }}
            >
              {loading ? '🔎 Searching...' : '🚀 Find References'}
            </button>
          </div>

          {error && <p style={{color: 'red', marginTop: 16, padding: 12, background: '#fee', borderRadius: 6}}>{error}</p>}

          {referencesData?.comparison_analysis?.comparison && (
            <div style={{background: '#fff7e6', padding: 16, borderRadius: 8, border: '1px solid #ffe8b2', marginTop: 16}}>
              <h3 style={{marginTop: 0, color: '#b36b00'}}>🔁 Comparison With Your Resume</h3>
              <div style={{whiteSpace: 'pre-wrap'}}>{referencesData.comparison_analysis.comparison}</div>
            </div>
          )}

          {referencesData?.references && (
            <div style={{marginTop: 24}}>
              <h3>Top Reference Resumes:</h3>
              {referencesData.references.map((ref, idx) => (
                <div key={idx} style={{
                  border: '1px solid #ddd',
                  borderRadius: 8,
                  padding: 16,
                  marginBottom: 12,
                  background: 'white'
                }}>
                  <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: 8}}>
                    <strong>Reference {idx + 1} — {ref.metadata.category}</strong>
                    <span style={{
                      background: ref.similarity_score >= 70 ? '#28a745' : ref.similarity_score >= 50 ? '#ffc107' : '#6c757d',
                      color: 'white', padding: '4px 12px', borderRadius: 20, fontWeight: 700
                    }}>{Math.round(ref.similarity_score)}%</span>
                  </div>
                  <div style={{fontSize: 14, color: '#666', marginBottom: 6}}>
                    <strong>Skills:</strong> {(ref.metadata.skills || []).slice(0, 10).join(', ')}
                  </div>
                  <div style={{fontSize: 12, color: '#999', marginBottom: 8}}>
                    {ref.text.slice(0, 200)}...
                  </div>
                  <div style={{display: 'flex', gap: 8}}>
                    <button onClick={() => onDownloadPdf(`Reference_${idx + 1}_${ref.metadata.category}`, ref.text)} style={{padding: '8px 12px'}}>⬇️ Download PDF</button>
                    <button onClick={() => navigator.clipboard.writeText(ref.text)} style={{padding: '8px 12px'}}>📋 Copy Text</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

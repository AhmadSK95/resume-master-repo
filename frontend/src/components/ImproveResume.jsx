import { useState, useEffect } from 'react';
import { analyzeResume, improveResumeWithJD, renderPdf, checkHealth } from '../api';
import ResumePreview from './ResumePreview';
import JDPanel from './JDPanel';
import InsightsPanel from './InsightsPanel';
import { parseResume, generateBulletSuggestions } from '../utils/resumeParser';

export default function ImproveResume() {
  // State
  const [file, setFile] = useState(null);
  const [jdText, setJdText] = useState("");
  const [analysisData, setAnalysisData] = useState(null);
  const [resumeData, setResumeData] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [dbCount, setDbCount] = useState(0);
  const [showSplitView, setShowSplitView] = useState(false);

  useEffect(() => {
    checkHealth().then(data => setDbCount(data.vector_db_count || 0)).catch(() => {});
  }, []);

  const onAnalyzeResume = async () => {
    if (!file) return;
    setLoading(true); 
    setError("");
    setShowSplitView(false);
    
    try {
      let data;
      if (jdText.trim()) {
        data = await improveResumeWithJD(file, jdText);
      } else {
        data = await analyzeResume(file);
      }
      
      setAnalysisData(data);
      
      // Parse resume into structured format
      const parsed = parseResume(data.resume_text_full || '');
      setResumeData(parsed);
      
      // Use backend suggestions if available, otherwise try frontend parsing
      const sug = data.suggestions || generateBulletSuggestions(parsed, data.analysis);
      setSuggestions(sug);
      
      // Show split view if JD was provided
      if (jdText.trim()) {
        setShowSplitView(true);
      }
      
      setFile(null);
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setLoading(false);
    }
  };

  const onApplySuggestion = (suggestion) => {
    // In a real implementation, this would update the resumeData
    // For now, just show a notification
    alert('Suggestion applied! (In production, this would update the resume preview)');
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

  const handleClear = () => {
    setAnalysisData(null);
    setResumeData(null);
    setSuggestions([]);
    setJdText('');
    setError('');
    setShowSplitView(false);
  };
  
  const handleExport = () => {
    if (resumeData) {
      window.print();
    }
  };

  return (
    <div style={styles.container}>

      {/* Input Section */}
      <div style={styles.inputSection}>
        <div style={styles.inputCard}>
          <div style={styles.inputRow}>
            <div style={styles.fileUploadSection}>
              <label style={styles.label}>
                📄 Upload Resume
              </label>
              <input 
                type="file" 
                accept=".pdf,.docx,.txt"
                onChange={e => setFile(e.target.files[0])}
                style={styles.fileInput}
              />
              {file && (
                <div style={styles.fileNameDisplay}>
                  ✓ {file.name}
                </div>
              )}
            </div>
            
            <div style={styles.jdInputSection}>
              <label style={styles.label}>
                📋 Job Description (Optional)
              </label>
              <textarea 
                value={jdText} 
                onChange={e => setJdText(e.target.value)}
                rows={3}
                placeholder="Paste job description for tailored analysis..."
                style={styles.jdTextarea}
              />
            </div>
          </div>
          
          <div style={styles.actionRow}>
            <button 
              onClick={onAnalyzeResume}
              disabled={loading || !file}
              style={{
                ...styles.primaryButton,
                opacity: loading || !file ? 0.5 : 1,
                cursor: loading || !file ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? '⏳ Analyzing...' : (jdText.trim() ? '🎯 Analyze Against Job' : '🔍 Analyze Resume')}
            </button>
            
            {analysisData && (
              <>
                <button onClick={handleClear} style={styles.secondaryButton}>
                  Clear
                </button>
                <button onClick={handleExport} style={styles.secondaryButton}>
                  📥 Export
                </button>
              </>
            )}
          </div>

          {error && (
            <div style={styles.errorAlert}>
              ⚠️ {error}
            </div>
          )}
        </div>
      </div>

      {/* Main Content - Split View or Single View */}
      {analysisData && showSplitView ? (
        <div style={styles.splitView}>
          {/* Left: JD Panel */}
          <div style={styles.leftPanel}>
            <JDPanel 
              jdText={jdText}
              onChange={setJdText}
              detectedFields={analysisData.fields}
            />
          </div>
          
          {/* Right: Resume Preview */}
          <div style={styles.rightPanel}>
            <div style={styles.panelHeader}>
              <h3 style={styles.panelTitle}>Resume Preview</h3>
              <div style={styles.headerActions}>
                <button 
                  onClick={() => navigator.clipboard.writeText(resumeData?.rawText || '')}
                  style={styles.iconButton}
                  title="Copy resume text"
                >
                  📋
                </button>
              </div>
            </div>
            <ResumePreview resumeData={resumeData} />
          </div>
        </div>
      ) : analysisData && !showSplitView ? (
        <div style={styles.singleView}>
          <ResumePreview resumeData={resumeData} />
        </div>
      ) : null}
      
      {/* Bottom: Insights Panel */}
      {analysisData && (
        <div style={styles.insightsSection}>
          <InsightsPanel
            analysisData={analysisData}
            suggestions={suggestions}
            onApplySuggestion={onApplySuggestion}
            onDownloadPdf={onDownloadPdf}
          />
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: 24
  },
  inputSection: {
    maxWidth: 1400,
    margin: '0 auto',
    padding: '24px 32px'
  },
  inputCard: {
    background: 'white',
    borderRadius: 12,
    padding: 24,
    boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
  },
  inputRow: {
    display: 'grid',
    gridTemplateColumns: '1fr 2fr',
    gap: 24,
    marginBottom: 20
  },
  fileUploadSection: {
    display: 'flex',
    flexDirection: 'column'
  },
  jdInputSection: {
    display: 'flex',
    flexDirection: 'column'
  },
  label: {
    fontSize: 14,
    fontWeight: 600,
    color: '#333',
    marginBottom: 8,
    display: 'block'
  },
  fileInput: {
    padding: 10,
    fontSize: 14,
    border: '2px dashed #ddd',
    borderRadius: 8,
    cursor: 'pointer',
    background: '#fafafa'
  },
  fileNameDisplay: {
    marginTop: 8,
    padding: 8,
    background: '#d4f4dd',
    color: '#0c6b2f',
    borderRadius: 6,
    fontSize: 13,
    fontWeight: 500
  },
  jdTextarea: {
    padding: 12,
    fontSize: 14,
    border: '1px solid #ddd',
    borderRadius: 8,
    fontFamily: 'inherit',
    resize: 'vertical',
    lineHeight: 1.5
  },
  actionRow: {
    display: 'flex',
    gap: 12,
    alignItems: 'center'
  },
  primaryButton: {
    padding: '12px 24px',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    border: 'none',
    borderRadius: 8,
    fontSize: 15,
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'transform 0.2s',
    boxShadow: '0 2px 8px rgba(102, 126, 234, 0.3)'
  },
  secondaryButton: {
    padding: '12px 24px',
    background: 'white',
    color: '#666',
    border: '1px solid #ddd',
    borderRadius: 8,
    fontSize: 14,
    fontWeight: 500,
    cursor: 'pointer'
  },
  iconButton: {
    padding: '6px 12px',
    background: 'transparent',
    border: '1px solid #ddd',
    borderRadius: 6,
    cursor: 'pointer',
    fontSize: 16
  },
  errorAlert: {
    marginTop: 16,
    padding: 12,
    background: '#ffebe9',
    color: '#c41d00',
    borderRadius: 8,
    fontSize: 14,
    border: '1px solid #ffcccb'
  },
  splitView: {
    maxWidth: 1400,
    margin: '0 auto',
    padding: '0 32px 24px',
    display: 'grid',
    gridTemplateColumns: '1fr 1.5fr',
    gap: 24,
    minHeight: 600
  },
  singleView: {
    maxWidth: 1400,
    margin: '0 auto',
    padding: '0 32px 24px'
  },
  leftPanel: {
    height: 600,
    position: 'sticky',
    top: 24
  },
  rightPanel: {
    display: 'flex',
    flexDirection: 'column',
    minHeight: 600
  },
  panelHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12
  },
  panelTitle: {
    margin: 0,
    fontSize: 18,
    fontWeight: 600,
    color: '#333'
  },
  headerActions: {
    display: 'flex',
    gap: 8
  },
  insightsSection: {
    maxWidth: 1400,
    margin: '0 auto',
    padding: '0 32px 32px'
  }
};

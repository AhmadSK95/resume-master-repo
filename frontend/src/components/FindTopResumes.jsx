import { useState } from 'react';
import { searchResumesForJD } from '../api';
import ReferenceResumeCard from './ReferenceResumeCard';

export default function FindTopResumes() {
  const [jdText, setJdText] = useState('');
  const [topK, setTopK] = useState(10);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!jdText.trim()) {
      setError('Please enter a job description');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const data = await searchResumesForJD(jdText, topK);
      setResults(data);
    } catch (e) {
      setError(e.message || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (title, content) => {
    // TODO: Implement PDF download
    alert('Download feature coming soon!');
  };

  return (
    <div style={styles.container}>
      {/* Search Section */}
      <div style={styles.searchCard}>
        <h2 style={styles.title}>🔍 Find Top Matching Resumes</h2>
        <p style={styles.subtitle}>
          Search through 10,730 resumes using semantic search powered by RAG
        </p>

        <div style={styles.inputSection}>
          <label style={styles.label}>Job Description</label>
          <textarea
            value={jdText}
            onChange={e => setJdText(e.target.value)}
            placeholder="Paste the job description here...&#10;&#10;Example:&#10;We are looking for a Senior Data Engineer with 5+ years of experience in Python, SQL, and cloud data platforms (AWS/GCP). Must have experience with Airflow, Spark, and data warehousing..."
            rows={8}
            style={styles.textarea}
          />
          <div style={styles.charCount}>
            {jdText.length} characters
          </div>
        </div>

        <div style={styles.controls}>
          <div style={styles.sliderSection}>
            <label style={styles.label}>
              Number of results: <strong>{topK}</strong>
            </label>
            <input
              type="range"
              min="5"
              max="50"
              value={topK}
              onChange={e => setTopK(parseInt(e.target.value))}
              style={styles.slider}
            />
            <div style={styles.sliderLabels}>
              <span>5</span>
              <span>25</span>
              <span>50</span>
            </div>
          </div>

          <button
            onClick={handleSearch}
            disabled={loading || !jdText.trim()}
            style={{
              ...styles.searchButton,
              opacity: loading || !jdText.trim() ? 0.5 : 1,
              cursor: loading || !jdText.trim() ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? '🔄 Searching...' : '🚀 Search Resumes'}
          </button>
        </div>

        {error && (
          <div style={styles.errorAlert}>⚠️ {error}</div>
        )}
      </div>

      {/* Results Section */}
      {results && (
        <div style={styles.resultsSection}>
          <div style={styles.resultsHeader}>
            <h3 style={styles.resultsTitle}>
              📊 Top {results.resumes?.length || 0} Matching Resumes
            </h3>
            {results.rag_insights && (
              <div style={styles.insightsBadge}>
                🤖 RAG-Enhanced Results
              </div>
            )}
          </div>

          {/* RAG Insights */}
          {results.rag_insights && (
            <div style={styles.ragInsights}>
              <h4 style={styles.insightsTitle}>💡 Search Insights</h4>
              <div style={styles.insightsList}>
                {results.rag_insights.key_requirements && (
                  <div style={styles.insightItem}>
                    <strong>Key Requirements Detected:</strong>
                    <div style={styles.tags}>
                      {results.rag_insights.key_requirements.slice(0, 8).map((req, idx) => (
                        <span key={idx} style={styles.tag}>{req}</span>
                      ))}
                    </div>
                  </div>
                )}
                
                {results.rag_insights.match_summary && (
                  <div style={styles.insightItem}>
                    <strong>Match Strategy:</strong> {results.rag_insights.match_summary}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Resume Cards */}
          <div style={styles.resultsGrid}>
            {results.resumes?.map((resume, idx) => (
              <ReferenceResumeCard
                key={idx}
                reference={resume}
                index={idx}
                onDownloadPdf={handleDownload}
              />
            ))}
          </div>

          {results.resumes?.length === 0 && (
            <div style={styles.emptyState}>
              <p>No matching resumes found. Try a different job description.</p>
            </div>
          )}
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
  searchCard: {
    background: 'white',
    borderRadius: 12,
    padding: 32,
    boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
  },
  title: {
    margin: '0 0 8px 0',
    fontSize: 24,
    fontWeight: 700,
    color: '#333'
  },
  subtitle: {
    margin: '0 0 24px 0',
    fontSize: 15,
    color: '#666',
    lineHeight: 1.5
  },
  inputSection: {
    marginBottom: 24
  },
  label: {
    display: 'block',
    fontSize: 14,
    fontWeight: 600,
    color: '#333',
    marginBottom: 8
  },
  textarea: {
    width: '100%',
    padding: 16,
    fontSize: 14,
    border: '2px solid #e0e0e0',
    borderRadius: 8,
    fontFamily: 'inherit',
    resize: 'vertical',
    lineHeight: 1.6,
    transition: 'border-color 0.2s',
    outline: 'none'
  },
  charCount: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
    textAlign: 'right'
  },
  controls: {
    display: 'flex',
    gap: 24,
    alignItems: 'flex-end'
  },
  sliderSection: {
    flex: 1
  },
  slider: {
    width: '100%',
    marginTop: 8
  },
  sliderLabels: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: 12,
    color: '#999',
    marginTop: 4
  },
  searchButton: {
    padding: '14px 32px',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    border: 'none',
    borderRadius: 8,
    fontSize: 15,
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'transform 0.2s, box-shadow 0.2s',
    boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)',
    whiteSpace: 'nowrap'
  },
  errorAlert: {
    marginTop: 16,
    padding: 12,
    background: '#fff3cd',
    border: '1px solid #ffc107',
    borderRadius: 6,
    color: '#856404',
    fontSize: 14
  },
  resultsSection: {
    background: 'white',
    borderRadius: 12,
    padding: 32,
    boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
  },
  resultsHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
    paddingBottom: 16,
    borderBottom: '2px solid #f0f0f0'
  },
  resultsTitle: {
    margin: 0,
    fontSize: 20,
    fontWeight: 700,
    color: '#333'
  },
  insightsBadge: {
    padding: '6px 12px',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    borderRadius: 16,
    fontSize: 13,
    fontWeight: 600
  },
  ragInsights: {
    background: '#f8f9ff',
    border: '1px solid #e0e7ff',
    borderRadius: 8,
    padding: 20,
    marginBottom: 24
  },
  insightsTitle: {
    margin: '0 0 12px 0',
    fontSize: 16,
    fontWeight: 600,
    color: '#667eea'
  },
  insightsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: 12
  },
  insightItem: {
    fontSize: 14,
    lineHeight: 1.6,
    color: '#444'
  },
  tags: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 8,
    marginTop: 8
  },
  tag: {
    padding: '4px 12px',
    background: 'white',
    border: '1px solid #667eea',
    borderRadius: 16,
    fontSize: 12,
    color: '#667eea',
    fontWeight: 500
  },
  resultsGrid: {
    display: 'flex',
    flexDirection: 'column',
    gap: 16
  },
  emptyState: {
    textAlign: 'center',
    padding: 60,
    color: '#999'
  }
};

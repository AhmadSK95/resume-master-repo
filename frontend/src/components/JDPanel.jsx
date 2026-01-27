/**
 * JDPanel - Job Description input with detected signals
 */
export default function JDPanel({ jdText, onChange, detectedFields }) {
  const charCount = jdText.length;
  
  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h3 style={styles.title}>Job Description</h3>
        <span style={styles.charCount}>{charCount} characters</span>
      </div>
      
      <textarea
        value={jdText}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Paste the job description here to get targeted suggestions and see how your resume matches..."
        style={styles.textarea}
      />
      
      {detectedFields && (
        <div style={styles.signals}>
          <div style={styles.signalTitle}>Detected from JD:</div>
          <div style={styles.signalsGrid}>
            {detectedFields.titles && detectedFields.titles.length > 0 && (
              <div style={styles.signalItem}>
                <strong>Titles:</strong>
                <div style={styles.chips}>
                  {detectedFields.titles.slice(0, 3).map((title, idx) => (
                    <span key={idx} style={styles.chip}>{title}</span>
                  ))}
                </div>
              </div>
            )}
            
            {detectedFields.skills && detectedFields.skills.length > 0 && (
              <div style={styles.signalItem}>
                <strong>Key Skills:</strong>
                <div style={styles.chips}>
                  {detectedFields.skills.slice(0, 10).map((skill, idx) => (
                    <span key={idx} style={styles.chip}>{skill}</span>
                  ))}
                </div>
              </div>
            )}
            
            {detectedFields.years_exp !== undefined && detectedFields.years_exp > 0 && (
              <div style={styles.signalItem}>
                <strong>Experience:</strong> {detectedFields.years_exp} years
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    background: 'white',
    borderRadius: 8,
    border: '1px solid #ddd',
    overflow: 'hidden'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 16px',
    borderBottom: '1px solid #e9ecef',
    background: '#f8f9fa'
  },
  title: {
    margin: 0,
    fontSize: 16,
    fontWeight: 600,
    color: '#333'
  },
  charCount: {
    fontSize: 12,
    color: '#999'
  },
  textarea: {
    flex: 1,
    border: 'none',
    padding: 16,
    fontSize: 14,
    lineHeight: 1.6,
    fontFamily: 'system-ui, -apple-system, sans-serif',
    resize: 'none',
    outline: 'none'
  },
  signals: {
    padding: 16,
    borderTop: '1px solid #e9ecef',
    background: '#f8f9fa',
    fontSize: 13
  },
  signalTitle: {
    fontWeight: 600,
    color: '#666',
    marginBottom: 8,
    fontSize: 12,
    textTransform: 'uppercase',
    letterSpacing: 0.5
  },
  signalsGrid: {
    display: 'flex',
    flexDirection: 'column',
    gap: 8
  },
  signalItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: 6,
    color: '#555'
  },
  chips: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 6
  },
  chip: {
    padding: '4px 10px',
    background: 'white',
    border: '1px solid #ddd',
    borderRadius: 12,
    fontSize: 12,
    color: '#555'
  }
};

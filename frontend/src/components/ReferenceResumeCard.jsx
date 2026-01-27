export default function ReferenceResumeCard({ reference, index, onDownloadPdf }) {
  const { metadata, text, similarity_score } = reference;

  const getScoreColor = (score) => {
    if (score >= 70) return '#28a745';
    if (score >= 50) return '#ffc107';
    return '#6c757d';
  };
  
  // Extract key highlights from text
  const extractHighlights = (text) => {
    const lines = text.split('\n').filter(l => l.trim());
    const highlights = [];
    
    // Look for impactful statements (numbers, achievements)
    for (const line of lines) {
      if (/\d+%|\d+x|\$\d+|improved|increased|reduced|achieved|led/i.test(line) && line.length < 150) {
        highlights.push(line.trim());
        if (highlights.length >= 3) break;
      }
    }
    
    return highlights;
  };
  
  const highlights = extractHighlights(text);
  
  // Show actual titles if available, filter out 'unknown'
  const displayTitles = (metadata.titles || [])
    .filter(t => t !== 'unknown')
    .slice(0, 3);

  return (
    <div style={{
      border: '1px solid #e0e0e0',
      borderRadius: 12,
      padding: 20,
      marginBottom: 16,
      background: 'white',
      boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
      transition: 'box-shadow 0.2s',
      cursor: 'pointer'
    }}
    onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.12)'}
    onMouseLeave={(e) => e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)'}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <strong style={{ fontSize: 18, color: '#1a1a1a' }}>Reference #{index + 1}</strong>
            {metadata.category && metadata.category !== 'uploaded' && (
              <span style={{
                background: '#e3f2fd',
                color: '#1565c0',
                padding: '4px 12px',
                borderRadius: 16,
                fontSize: 12,
                fontWeight: 600
              }}>
                {metadata.category}
              </span>
            )}
          </div>
          
          {displayTitles.length > 0 && (
            <div style={{ fontSize: 15, color: '#555', marginBottom: 8, fontWeight: 500 }}>
              {displayTitles.join(' • ')}
            </div>
          )}
        </div>
        
        <div style={{
          background: getScoreColor(similarity_score),
          color: 'white',
          padding: '8px 16px',
          borderRadius: 24,
          fontWeight: 700,
          fontSize: 16,
          minWidth: 80,
          textAlign: 'center'
        }}>
          {Math.round(similarity_score)}%
        </div>
      </div>

      {/* Skills Tags */}
      {metadata.skills && metadata.skills.length > 0 && (
        <div style={{ marginBottom: 12 }}>
          <div style={{ fontSize: 12, color: '#666', marginBottom: 6, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5 }}>Skills</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {metadata.skills.slice(0, 12).map((skill, idx) => (
              <span key={idx} style={{
                background: '#f5f5f5',
                color: '#333',
                padding: '5px 12px',
                borderRadius: 16,
                fontSize: 13,
                border: '1px solid #e0e0e0'
              }}>
                {skill}
              </span>
            ))}
            {metadata.skills.length > 12 && (
              <span style={{
                color: '#666',
                padding: '5px 12px',
                fontSize: 13
              }}>
                +{metadata.skills.length - 12} more
              </span>
            )}
          </div>
        </div>
      )}
      
      {/* Experience */}
      {metadata.years > 0 && (
        <div style={{ fontSize: 14, color: '#666', marginBottom: 12 }}>
          <strong style={{ color: '#333' }}>Experience:</strong> {metadata.years} years
        </div>
      )}

      {/* Key Highlights */}
      {highlights.length > 0 && (
        <div style={{ marginBottom: 12 }}>
          <div style={{ fontSize: 12, color: '#666', marginBottom: 6, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5 }}>Key Highlights</div>
          <ul style={{
            margin: 0,
            paddingLeft: 20,
            fontSize: 13,
            lineHeight: 1.6,
            color: '#555'
          }}>
            {highlights.map((highlight, idx) => (
              <li key={idx} style={{ marginBottom: 4 }}>{highlight}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Preview Snippet */}
      {!highlights.length && (
        <div style={{
          fontSize: 13,
          color: '#666',
          marginBottom: 12,
          padding: 12,
          background: '#fafafa',
          borderRadius: 6,
          lineHeight: 1.6,
          borderLeft: '3px solid #e0e0e0',
          fontStyle: 'italic'
        }}>
          {text.slice(0, 200).trim()}...
        </div>
      )}

      <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
        <button
          onClick={() => onDownloadPdf(`Reference_${index + 1}_${displayTitles[0] || 'Resume'}`, text)}
          style={{
            padding: '10px 20px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            borderRadius: 8,
            cursor: 'pointer',
            fontSize: 14,
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: 6
          }}
        >
          <span>⬇</span> Download
        </button>
        <button
          onClick={() => navigator.clipboard.writeText(text)}
          style={{
            padding: '10px 20px',
            background: 'white',
            color: '#333',
            border: '1px solid #ddd',
            borderRadius: 8,
            cursor: 'pointer',
            fontSize: 14,
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            gap: 6
          }}
        >
          <span>📋</span> Copy
        </button>
      </div>
    </div>
  );
}

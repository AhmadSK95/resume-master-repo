export default function ReferenceResumeCard({ reference, index, onDownloadPdf }) {
  const { metadata, text, similarity_score } = reference;

  const getScoreColor = (score) => {
    if (score >= 70) return '#28a745';
    if (score >= 50) return '#ffc107';
    return '#6c757d';
  };

  return (
    <div style={{
      border: '1px solid #ddd',
      borderRadius: 8,
      padding: 16,
      marginBottom: 12,
      background: 'white',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <div>
          <strong style={{ fontSize: 16 }}>Reference Resume {index + 1}</strong>
          <span style={{ marginLeft: 12, color: '#666', fontSize: 14 }}>
            {metadata.category}
          </span>
        </div>
        <span style={{
          background: getScoreColor(similarity_score),
          color: 'white',
          padding: '4px 12px',
          borderRadius: 20,
          fontWeight: 700,
          fontSize: 14
        }}>
          {Math.round(similarity_score)}% Match
        </span>
      </div>

      <div style={{ fontSize: 14, color: '#333', marginBottom: 8 }}>
        <strong>Skills:</strong>{' '}
        <span style={{ color: '#666' }}>
          {(metadata.skills || []).slice(0, 10).join(', ') || 'N/A'}
        </span>
      </div>

      <div style={{ fontSize: 14, color: '#333', marginBottom: 8 }}>
        <strong>Titles:</strong>{' '}
        <span style={{ color: '#666' }}>
          {(metadata.titles || []).slice(0, 3).join(', ') || 'N/A'}
        </span>
      </div>

      <div style={{ fontSize: 14, color: '#333', marginBottom: 12 }}>
        <strong>Experience:</strong>{' '}
        <span style={{ color: '#666' }}>
          {metadata.years || 0} years
        </span>
      </div>

      <div style={{
        fontSize: 13,
        color: '#777',
        marginBottom: 12,
        padding: 10,
        background: '#f9f9f9',
        borderRadius: 4,
        lineHeight: 1.5,
        maxHeight: 100,
        overflow: 'hidden'
      }}>
        {text.slice(0, 250)}...
      </div>

      <div style={{ display: 'flex', gap: 8 }}>
        <button
          onClick={() => onDownloadPdf(`Reference_${index + 1}_${metadata.category}`, text)}
          style={{
            padding: '8px 16px',
            background: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: 6,
            cursor: 'pointer',
            fontSize: 14,
            fontWeight: 500
          }}
        >
          ⬇️ Download PDF
        </button>
        <button
          onClick={() => navigator.clipboard.writeText(text)}
          style={{
            padding: '8px 16px',
            background: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: 6,
            cursor: 'pointer',
            fontSize: 14,
            fontWeight: 500
          }}
        >
          📋 Copy Text
        </button>
      </div>
    </div>
  );
}

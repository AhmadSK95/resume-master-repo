import { computeWordDiff } from '../utils/diff';

/**
 * DiffText - Shows before/after text with highlighted differences
 */
export default function DiffText({ before, after, compact = false }) {
  if (!before && !after) return null;
  
  if (compact) {
    // Show inline diff
    const diff = computeWordDiff(before, after);
    
    return (
      <div style={{ 
        padding: 12, 
        background: '#f8f9fa', 
        borderRadius: 6,
        fontSize: 14,
        lineHeight: 1.6
      }}>
        {diff.parts.map((part, idx) => {
          if (part.type === 'equal') {
            return <span key={idx}>{part.value} </span>;
          } else if (part.type === 'removed') {
            return (
              <span 
                key={idx} 
                style={{ 
                  background: '#ffebe9', 
                  color: '#c41d00',
                  textDecoration: 'line-through',
                  padding: '2px 4px',
                  borderRadius: 3,
                  marginRight: 2
                }}
              >
                {part.value}
              </span>
            );
          } else { // added
            return (
              <span 
                key={idx} 
                style={{ 
                  background: '#d4f4dd', 
                  color: '#0c6b2f',
                  padding: '2px 4px',
                  borderRadius: 3,
                  marginRight: 2
                }}
              >
                {part.value}
              </span>
            );
          }
        })}
      </div>
    );
  }
  
  // Show side-by-side or stacked
  return (
    <div style={{ 
      display: 'grid', 
      gap: 12,
      fontSize: 14,
      lineHeight: 1.6
    }}>
      {before && (
        <div>
          <div style={{ 
            fontWeight: 600, 
            marginBottom: 6,
            color: '#666',
            fontSize: 12,
            textTransform: 'uppercase',
            letterSpacing: 0.5
          }}>
            Before
          </div>
          <div style={{ 
            padding: 12, 
            background: '#ffebe9', 
            borderRadius: 6,
            borderLeft: '3px solid #c41d00'
          }}>
            {before}
          </div>
        </div>
      )}
      
      {after && (
        <div>
          <div style={{ 
            fontWeight: 600, 
            marginBottom: 6,
            color: '#666',
            fontSize: 12,
            textTransform: 'uppercase',
            letterSpacing: 0.5
          }}>
            After
          </div>
          <div style={{ 
            padding: 12, 
            background: '#d4f4dd', 
            borderRadius: 6,
            borderLeft: '3px solid #0c6b2f'
          }}>
            {after}
          </div>
        </div>
      )}
    </div>
  );
}

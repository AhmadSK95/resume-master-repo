import { useState } from 'react';
import DiffText from './DiffText';
import ReferenceResumeCard from './ReferenceResumeCard';

/**
 * InsightsPanel - Tabbed interface for analysis results
 */
export default function InsightsPanel({ 
  analysisData, 
  suggestions,
  onApplySuggestion,
  onDownloadPdf 
}) {
  const [activeTab, setActiveTab] = useState('overview');
  
  if (!analysisData) return null;
  
  const tabs = [
    { id: 'overview', label: '📊 Match Overview', icon: '📊' },
    { id: 'suggestions', label: '✨ Suggestions', icon: '✨', count: suggestions?.length || 0 },
    { id: 'references', label: '📚 References', icon: '📚', count: analysisData.reference_resumes?.length || 0 }
  ];
  
  return (
    <div style={styles.container}>
      <div style={styles.tabs}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              ...styles.tab,
              ...(activeTab === tab.id ? styles.tabActive : {})
            }}
          >
            {tab.label}
            {tab.count > 0 && (
              <span style={styles.badge}>{tab.count}</span>
            )}
          </button>
        ))}
      </div>
      
      <div style={styles.content}>
        {activeTab === 'overview' && (
          <OverviewTab analysisData={analysisData} />
        )}
        
        {activeTab === 'suggestions' && (
          <SuggestionsTab 
            suggestions={suggestions} 
            onApply={onApplySuggestion}
          />
        )}
        
        {activeTab === 'references' && (
          <ReferencesTab 
            references={analysisData.reference_resumes}
            onDownloadPdf={onDownloadPdf}
          />
        )}
      </div>
    </div>
  );
}

function OverviewTab({ analysisData }) {
  const { score, analysis, fields, jd_text, intelligent_extraction } = analysisData;
  
  // Use intelligent extraction data if available
  const hasIntelligent = intelligent_extraction && intelligent_extraction.gap_analysis;
  const gapData = hasIntelligent ? intelligent_extraction.gap_analysis : null;
  
  // Parse analysis for structured content
  const parseAnalysis = (text) => {
    const sections = [];
    const lines = text.split('\n');
    let currentSection = { title: '', content: [] };
    
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      
      // Check if line is a heading (all caps, or starts with ##)
      if (trimmed === trimmed.toUpperCase() && trimmed.length < 50 || trimmed.startsWith('##')) {
        if (currentSection.content.length > 0) {
          sections.push(currentSection);
        }
        currentSection = { 
          title: trimmed.replace(/^#+\s*/, ''), 
          content: [] 
        };
      } else {
        currentSection.content.push(trimmed);
      }
    }
    
    if (currentSection.content.length > 0) {
      sections.push(currentSection);
    }
    
    return sections.length > 0 ? sections : [{ title: '', content: [text] }];
  };
  
  const sections = parseAnalysis(analysis);
  
  // Extract strengths and gaps from analysis
  const extractKeyPoints = (text) => {
    const strengths = [];
    const gaps = [];
    const lines = text.toLowerCase().split('\n');
    
    for (const line of lines) {
      if (line.includes('strength') || line.includes('good') || line.includes('strong')) {
        strengths.push(line.trim());
      }
      if (line.includes('missing') || line.includes('gap') || line.includes('lack') || line.includes('improve')) {
        gaps.push(line.trim());
      }
    }
    
    return { strengths: strengths.slice(0, 3), gaps: gaps.slice(0, 3) };
  };
  
  const { strengths, gaps } = extractKeyPoints(analysis);
  
  return (
    <div style={styles.tabContent}>
      {/* Score Card */}
      {jd_text && (
        <div style={styles.scoreCard}>
          <div style={styles.scoreCircle}>
            <div style={{
              ...styles.scoreValue,
              color: score >= 70 ? '#28a745' : score >= 50 ? '#ffc107' : '#dc3545'
            }}>
              {score}
            </div>
            <div style={styles.scoreLabel}>/ 100</div>
          </div>
          <div style={styles.scoreInfo}>
            <h3 style={styles.scoreTitle}>Match Score</h3>
            <p style={styles.scoreDesc}>
              {score >= 70 ? 'Strong match! Your resume aligns well with this role.' :
               score >= 50 ? 'Good foundation, but some gaps to address.' :
               'Significant improvements needed for this role.'}
            </p>
          </div>
        </div>
      )}
      
      {/* Intelligent Gap Analysis */}
      {gapData && (
        <div style={styles.intelligentSection}>
          {/* Strong Matches */}
          {gapData.strong_matches && gapData.strong_matches.length > 0 && (
            <div style={styles.gapSection}>
              <h4 style={{...styles.pointsTitle, color: '#28a745'}}>
                ✓ Strong Matches ({gapData.strong_matches.length})
              </h4>
              <ul style={styles.bulletList}>
                {gapData.strong_matches.map((item, idx) => (
                  <li key={idx} style={styles.bulletItem}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Critical Gaps */}
          {gapData.critical_gaps && gapData.critical_gaps.length > 0 && (
            <div style={styles.gapSection}>
              <h4 style={{...styles.pointsTitle, color: '#dc3545'}}>
                ⚠️ Critical Gaps ({gapData.critical_gaps.length})
              </h4>
              <ul style={styles.bulletList}>
                {gapData.critical_gaps.map((item, idx) => (
                  <li key={idx} style={styles.bulletItem}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Partial Matches */}
          {gapData.partial_matches && gapData.partial_matches.length > 0 && (
            <div style={styles.gapSection}>
              <h4 style={{...styles.pointsTitle, color: '#ffc107'}}>
                ◐ Partial Matches ({gapData.partial_matches.length})
              </h4>
              <ul style={styles.bulletList}>
                {gapData.partial_matches.map((item, idx) => (
                  <li key={idx} style={styles.bulletItem}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Top Actions */}
          {gapData.top_3_actions && gapData.top_3_actions.length > 0 && (
            <div style={styles.gapSection}>
              <h4 style={{...styles.pointsTitle, color: '#007bff'}}>
                🎯 Top Priority Actions
              </h4>
              <ol style={styles.bulletList}>
                {gapData.top_3_actions.map((item, idx) => (
                  <li key={idx} style={styles.bulletItem}><strong>{item}</strong></li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}
      
      {/* Key Points (fallback if no intelligent data) */}
      {!gapData && (strengths.length > 0 || gaps.length > 0) && (
        <div style={styles.keyPoints}>
          {strengths.length > 0 && (
            <div style={styles.pointsSection}>
              <h4 style={styles.pointsTitle}>
                <span style={{ color: '#28a745' }}>✓</span> Strengths
              </h4>
              <div style={styles.chipGroup}>
                {strengths.slice(0, 5).map((str, idx) => (
                  <span key={idx} style={{...styles.chip, ...styles.chipSuccess}}>
                    {str.length > 60 ? str.slice(0, 60) + '...' : str}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {gaps.length > 0 && (
            <div style={styles.pointsSection}>
              <h4 style={styles.pointsTitle}>
                <span style={{ color: '#dc3545' }}>⚠</span> Areas to Improve
              </h4>
              <div style={styles.chipGroup}>
                {gaps.slice(0, 5).map((gap, idx) => (
                  <span key={idx} style={{...styles.chip, ...styles.chipWarning}}>
                    {gap.length > 60 ? gap.slice(0, 60) + '...' : gap}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Detailed Analysis */}
      <div style={styles.analysisSection}>
        <h4 style={styles.sectionTitle}>
          {jd_text ? '🎯 Detailed Analysis' : '✨ Resume Feedback'}
        </h4>
        {sections.map((section, idx) => (
          <div key={idx} style={styles.analysisBlock}>
            {section.title && (
              <h5 style={styles.analysisBlockTitle}>{section.title}</h5>
            )}
            <div style={styles.analysisContent}>
              {section.content.map((line, lineIdx) => (
                <p key={lineIdx} style={styles.analysisParagraph}>{line}</p>
              ))}
            </div>
          </div>
        ))}
      </div>
      
      {/* Detected Fields */}
      {fields && (
        <div style={styles.fieldsSection}>
          <h4 style={styles.sectionTitle}>📋 Detected Information</h4>
          <div style={styles.fieldsGrid}>
            {fields.skills && fields.skills.length > 0 && (
              <div style={styles.fieldItem}>
                <strong>Skills:</strong>
                <div style={styles.fieldValue}>
                  {fields.skills.slice(0, 15).join(', ')}
                </div>
              </div>
            )}
            {fields.titles && fields.titles.length > 0 && (
              <div style={styles.fieldItem}>
                <strong>Job Titles:</strong>
                <div style={styles.fieldValue}>
                  {fields.titles.join(', ')}
                </div>
              </div>
            )}
            {fields.years_exp !== undefined && (
              <div style={styles.fieldItem}>
                <strong>Years of Experience:</strong>
                <div style={styles.fieldValue}>{fields.years_exp}</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function SuggestionsTab({ suggestions, onApply }) {
  if (!suggestions || suggestions.length === 0) {
    return (
      <div style={styles.tabContent}>
        <div style={styles.emptyState}>
          <p style={{ color: '#999' }}>
            No specific suggestions available yet. The AI analysis above provides general guidance.
          </p>
          <p style={{ color: '#999', fontSize: 13, marginTop: 8 }}>
            Tip: Make sure your resume has clear bullet points under experience sections for targeted suggestions.
          </p>
        </div>
      </div>
    );
  }
  
  return (
    <div style={styles.tabContent}>
      <div style={styles.suggestionsHeader}>
        <h4 style={styles.sectionTitle}>✨ Suggested Improvements</h4>
        <p style={{ color: '#666', fontSize: 14, margin: 0 }}>
          Click "Apply" to update your resume preview
        </p>
      </div>
      
      {suggestions.map((suggestion, idx) => (
        <div key={idx} style={styles.suggestionCard}>
          <div style={styles.suggestionHeader}>
            <span style={styles.suggestionNumber}>#{idx + 1}</span>
            {suggestion.reason && (
              <span style={styles.suggestionReason}>{suggestion.reason}</span>
            )}
          </div>
          
          <DiffText 
            before={suggestion.before} 
            after={suggestion.after}
          />
          
          <div style={styles.suggestionActions}>
            <button 
              onClick={() => onApply && onApply(suggestion)}
              style={styles.applyButton}
            >
              ✓ Apply Suggestion
            </button>
            <button 
              onClick={() => navigator.clipboard.writeText(suggestion.after)}
              style={styles.copyButton}
            >
              📋 Copy
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

function ReferencesTab({ references, onDownloadPdf }) {
  if (!references || references.length === 0) {
    return (
      <div style={styles.tabContent}>
        <div style={styles.emptyState}>
          <p style={{ color: '#999' }}>
            No reference resumes available. Add a job description to see relevant examples.
          </p>
        </div>
      </div>
    );
  }
  
  return (
    <div style={styles.tabContent}>
      <div style={styles.referencesHeader}>
        <h4 style={styles.sectionTitle}>📚 Top Reference Resumes</h4>
        <p style={{ color: '#666', fontSize: 14, margin: 0 }}>
          These resumes from our database match the job description well. Use them as inspiration.
        </p>
      </div>
      
      {references.map((ref, idx) => (
        <ReferenceResumeCard
          key={idx}
          reference={ref}
          index={idx}
          onDownloadPdf={onDownloadPdf}
        />
      ))}
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
  tabs: {
    display: 'flex',
    borderBottom: '2px solid #e9ecef',
    background: '#f8f9fa'
  },
  tab: {
    flex: 1,
    padding: '12px 16px',
    border: 'none',
    background: 'transparent',
    cursor: 'pointer',
    fontSize: 14,
    fontWeight: 500,
    color: '#666',
    transition: 'all 0.2s',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    position: 'relative'
  },
  tabActive: {
    color: '#007bff',
    borderBottom: '3px solid #007bff',
    background: 'white'
  },
  badge: {
    background: '#007bff',
    color: 'white',
    borderRadius: 10,
    padding: '2px 8px',
    fontSize: 12,
    fontWeight: 600
  },
  content: {
    flex: 1,
    overflow: 'auto'
  },
  tabContent: {
    padding: 20
  },
  scoreCard: {
    display: 'flex',
    gap: 20,
    padding: 20,
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    borderRadius: 8,
    color: 'white',
    marginBottom: 20
  },
  scoreCircle: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 100
  },
  scoreValue: {
    fontSize: 48,
    fontWeight: 700,
    lineHeight: 1
  },
  scoreLabel: {
    fontSize: 14,
    opacity: 0.9
  },
  scoreInfo: {
    flex: 1
  },
  scoreTitle: {
    margin: '0 0 8px 0',
    fontSize: 20,
    fontWeight: 600
  },
  scoreDesc: {
    margin: 0,
    fontSize: 14,
    opacity: 0.95,
    lineHeight: 1.5
  },
  keyPoints: {
    display: 'flex',
    flexDirection: 'column',
    gap: 16,
    marginBottom: 20
  },
  pointsSection: {},
  pointsTitle: {
    margin: '0 0 10px 0',
    fontSize: 15,
    fontWeight: 600,
    display: 'flex',
    alignItems: 'center',
    gap: 8
  },
  chipGroup: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 8
  },
  chip: {
    padding: '6px 12px',
    borderRadius: 16,
    fontSize: 13,
    lineHeight: 1.4
  },
  chipSuccess: {
    background: '#d4f4dd',
    color: '#0c6b2f',
    border: '1px solid #9fe6b8'
  },
  chipWarning: {
    background: '#fff3cd',
    color: '#856404',
    border: '1px solid #ffeaa7'
  },
  analysisSection: {
    marginBottom: 20
  },
  sectionTitle: {
    margin: '0 0 16px 0',
    fontSize: 16,
    fontWeight: 600,
    color: '#333'
  },
  analysisBlock: {
    marginBottom: 16
  },
  analysisBlockTitle: {
    margin: '0 0 8px 0',
    fontSize: 14,
    fontWeight: 600,
    color: '#555'
  },
  analysisContent: {
    fontSize: 14,
    lineHeight: 1.6,
    color: '#444'
  },
  analysisParagraph: {
    margin: '0 0 8px 0'
  },
  fieldsSection: {
    padding: 16,
    background: '#f8f9fa',
    borderRadius: 8,
    border: '1px solid #e9ecef'
  },
  fieldsGrid: {
    display: 'flex',
    flexDirection: 'column',
    gap: 12
  },
  fieldItem: {
    fontSize: 14
  },
  fieldValue: {
    color: '#666',
    marginTop: 4
  },
  emptyState: {
    textAlign: 'center',
    padding: '60px 20px',
    color: '#999'
  },
  suggestionsHeader: {
    marginBottom: 20
  },
  suggestionCard: {
    border: '1px solid #e9ecef',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    background: '#fafafa'
  },
  suggestionHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    marginBottom: 12
  },
  suggestionNumber: {
    background: '#007bff',
    color: 'white',
    borderRadius: '50%',
    width: 28,
    height: 28,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 12,
    fontWeight: 600
  },
  suggestionReason: {
    fontSize: 13,
    color: '#666',
    fontStyle: 'italic'
  },
  suggestionActions: {
    display: 'flex',
    gap: 8,
    marginTop: 12
  },
  applyButton: {
    padding: '8px 16px',
    background: '#28a745',
    color: 'white',
    border: 'none',
    borderRadius: 6,
    cursor: 'pointer',
    fontSize: 14,
    fontWeight: 500
  },
  copyButton: {
    padding: '8px 16px',
    background: '#6c757d',
    color: 'white',
    border: 'none',
    borderRadius: 6,
    cursor: 'pointer',
    fontSize: 14,
    fontWeight: 500
  },
  referencesHeader: {
    marginBottom: 20
  },
  intelligentSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: 20,
    marginBottom: 24
  },
  gapSection: {
    padding: 16,
    background: '#ffffff',
    border: '1px solid #e9ecef',
    borderRadius: 8
  },
  bulletList: {
    margin: '8px 0 0 0',
    paddingLeft: 24,
    fontSize: 14,
    lineHeight: 1.6,
    color: '#444'
  },
  bulletItem: {
    marginBottom: 8
  }
};

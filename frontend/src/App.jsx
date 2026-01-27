import { useState } from 'react';
import FindTopResumes from './components/FindTopResumes';
import ImproveResume from './components/ImproveResume';

export default function App() {
  const [activeTab, setActiveTab] = useState('find');

  return (
    <div style={styles.app}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <h1 style={styles.appTitle}>🎯 AI Resume Matcher</h1>
          <p style={styles.appSubtitle}>
            Smart resume matching powered by RAG • 10,730 resumes indexed
          </p>
        </div>
      </header>

      {/* Tab Navigation */}
      <div style={styles.tabBar}>
        <div style={styles.tabBarInner}>
          <button
            onClick={() => setActiveTab('find')}
            style={{
              ...styles.tab,
              ...(activeTab === 'find' ? styles.tabActive : {})
            }}
          >
            <span style={styles.tabIcon}>🔍</span>
            <div style={styles.tabText}>
              <div style={styles.tabTitle}>Find Top Resumes</div>
              <div style={styles.tabDesc}>Search 10K resumes for a JD</div>
            </div>
          </button>

          <button
            onClick={() => setActiveTab('improve')}
            style={{
              ...styles.tab,
              ...(activeTab === 'improve' ? styles.tabActive : {})
            }}
          >
            <span style={styles.tabIcon}>✨</span>
            <div style={styles.tabText}>
              <div style={styles.tabTitle}>Improve My Resume</div>
              <div style={styles.tabDesc}>Get AI-powered suggestions</div>
            </div>
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <div style={styles.content}>
        {activeTab === 'find' ? <FindTopResumes /> : <ImproveResume />}
      </div>
    </div>
  );
}

const styles = {
  app: {
    minHeight: '100vh',
    background: '#f5f7fa',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
  },
  header: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    padding: '24px 32px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
  },
  headerContent: {
    maxWidth: 1400,
    margin: '0 auto'
  },
  appTitle: {
    margin: 0,
    fontSize: 28,
    fontWeight: 700
  },
  appSubtitle: {
    margin: '4px 0 0 0',
    fontSize: 14,
    opacity: 0.9
  },
  tabBar: {
    background: 'white',
    borderBottom: '1px solid #e0e0e0',
    boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
  },
  tabBarInner: {
    maxWidth: 1400,
    margin: '0 auto',
    padding: '0 32px',
    display: 'flex',
    gap: 8
  },
  tab: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    padding: '20px 24px',
    border: 'none',
    background: 'transparent',
    cursor: 'pointer',
    borderBottom: '3px solid transparent',
    transition: 'all 0.2s',
    color: '#666'
  },
  tabActive: {
    borderBottom: '3px solid #667eea',
    background: '#f8f9ff',
    color: '#667eea'
  },
  tabIcon: {
    fontSize: 28
  },
  tabText: {
    textAlign: 'left'
  },
  tabTitle: {
    fontSize: 16,
    fontWeight: 600,
    marginBottom: 2
  },
  tabDesc: {
    fontSize: 13,
    opacity: 0.8
  },
  content: {
    maxWidth: 1400,
    margin: '0 auto',
    padding: '24px 32px'
  }
};

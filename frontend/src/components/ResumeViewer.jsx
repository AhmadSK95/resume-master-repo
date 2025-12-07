import { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

export default function ResumeViewer({ resumeText, filepath }) {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [viewMode, setViewMode] = useState('pdf'); // 'pdf' or 'text'
  const [loadError, setLoadError] = useState(false);

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
    setLoadError(false);
  };

  const onDocumentLoadError = (error) => {
    console.error('PDF load error:', error);
    setLoadError(true);
    setViewMode('text');
  };

  const isPDF = filepath && (filepath.endsWith('.pdf') || filepath.includes('.pdf'));

  return (
    <div style={{
      border: '1px solid #ddd',
      borderRadius: 8,
      padding: 16,
      background: '#fff',
      marginTop: 16
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h3 style={{ margin: 0 }}>📄 Your Resume</h3>
        {isPDF && !loadError && (
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              onClick={() => setViewMode('pdf')}
              style={{
                padding: '6px 12px',
                background: viewMode === 'pdf' ? '#007bff' : '#e9ecef',
                color: viewMode === 'pdf' ? 'white' : '#333',
                border: 'none',
                borderRadius: 4,
                cursor: 'pointer',
                fontSize: 13
              }}
            >
              PDF View
            </button>
            <button
              onClick={() => setViewMode('text')}
              style={{
                padding: '6px 12px',
                background: viewMode === 'text' ? '#007bff' : '#e9ecef',
                color: viewMode === 'text' ? 'white' : '#333',
                border: 'none',
                borderRadius: 4,
                cursor: 'pointer',
                fontSize: 13
              }}
            >
              Text View
            </button>
          </div>
        )}
      </div>

      {viewMode === 'pdf' && isPDF && !loadError ? (
        <div>
          <Document
            file={filepath}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={onDocumentLoadError}
            loading={
              <div style={{ padding: 40, textAlign: 'center', color: '#666' }}>
                Loading PDF...
              </div>
            }
          >
            <Page
              pageNumber={pageNumber}
              renderTextLayer={true}
              renderAnnotationLayer={true}
              width={Math.min(window.innerWidth * 0.6, 800)}
            />
          </Document>
          
          {numPages && numPages > 1 && (
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              gap: 16,
              marginTop: 12,
              padding: 12,
              background: '#f8f9fa',
              borderRadius: 6
            }}>
              <button
                onClick={() => setPageNumber(Math.max(1, pageNumber - 1))}
                disabled={pageNumber <= 1}
                style={{
                  padding: '6px 12px',
                  background: pageNumber <= 1 ? '#e9ecef' : '#007bff',
                  color: pageNumber <= 1 ? '#6c757d' : 'white',
                  border: 'none',
                  borderRadius: 4,
                  cursor: pageNumber <= 1 ? 'not-allowed' : 'pointer',
                  fontSize: 14
                }}
              >
                ← Previous
              </button>
              <span style={{ fontSize: 14, fontWeight: 500 }}>
                Page {pageNumber} of {numPages}
              </span>
              <button
                onClick={() => setPageNumber(Math.min(numPages, pageNumber + 1))}
                disabled={pageNumber >= numPages}
                style={{
                  padding: '6px 12px',
                  background: pageNumber >= numPages ? '#e9ecef' : '#007bff',
                  color: pageNumber >= numPages ? '#6c757d' : 'white',
                  border: 'none',
                  borderRadius: 4,
                  cursor: pageNumber >= numPages ? 'not-allowed' : 'pointer',
                  fontSize: 14
                }}
              >
                Next →
              </button>
            </div>
          )}
        </div>
      ) : (
        <div style={{
          background: '#f8f9fa',
          padding: 16,
          borderRadius: 6,
          maxHeight: 400,
          overflowY: 'auto',
          fontSize: 14,
          lineHeight: 1.6,
          whiteSpace: 'pre-wrap',
          fontFamily: 'monospace',
          color: '#333'
        }}>
          {resumeText || 'No resume text available'}
        </div>
      )}
    </div>
  );
}

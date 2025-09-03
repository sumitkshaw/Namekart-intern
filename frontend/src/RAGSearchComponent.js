import React, { useState, useEffect } from 'react';
import './RAGSearch.css'; // We'll need to create this CSS file

const API_BASE = 'http://localhost:8000/api';

const RAGSearchComponent = ({ onNoteSelect }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [ragResults, setRagResults] = useState(null);
  const [ragStatus, setRagStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);

  // Check RAG system status
  const checkRAGStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/rag/status`);
      const data = await response.json();
      setRagStatus(data);
    } catch (error) {
      console.error('Error checking RAG status:', error);
      setRagStatus({ status: 'error', error: error.message });
    }
  };

  // Perform RAG search
  const performRAGSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE}/notes/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          top_k: 3
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Handle both success/error format and direct data format
      if (data.success === false) {
        setError('Search failed: ' + data.error);
        setRagResults(null);
      } else if (data.data || data.response) {
        // Handle the format from your RAG service
        setRagResults(data.data || data);
      } else {
        setRagResults(data);
      }
    } catch (error) {
      setError('Error performing search: ' + error.message);
      setRagResults(null);
    }
    
    setLoading(false);
  };

  // Refresh RAG index
  const refreshRAGIndex = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE}/rag/refresh`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      await checkRAGStatus();
      setError('RAG index refreshed successfully!');
      // Clear the error after 3 seconds
      setTimeout(() => setError(''), 3000);
    } catch (error) {
      setError('Error refreshing RAG index: ' + error.message);
    }
    setLoading(false);
  };

  // Handle search on Enter key
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      performRAGSearch();
    }
  };

  // Format similarity score as percentage
  const formatSimilarity = (score) => {
    return Math.round(score * 100);
  };

  // Check RAG status on component mount
  useEffect(() => {
    checkRAGStatus();
  }, []);

  return (
    <div className="rag-search-container">
      {/* RAG Status Indicator */}
      <div className="rag-status">
        <div className="rag-status-header" onClick={() => setIsExpanded(!isExpanded)}>
          <span className={`rag-status-indicator ${ragStatus?.status}`}>
            {ragStatus?.status === 'active' ? '🟢' : 
             ragStatus?.status === 'error' ? '🔴' : '🟡'}
          </span>
          <span className="rag-status-text">
            AI Search (MANUALLY DISABLED DUE TO IMAGE SIZE INCREASING 4GB) {ragStatus?.status === 'active' ? 'Ready' : 
                     ragStatus?.status === 'error' ? 'Error' : 'Loading'}
          </span>
          <span className="rag-expand-icon">{isExpanded ? '▼' : '▶'}</span>
        </div>
        
        {isExpanded && ragStatus && (
          <div className="rag-status-details">
            <p><strong>Status:</strong> {ragStatus.status}</p>
            {ragStatus.indexed_chunks && (
              <p><strong>Indexed chunks:</strong> {ragStatus.indexed_chunks}</p>
            )}
            {ragStatus.model && (
              <p><strong>Model:</strong> {ragStatus.model}</p>
            )}
            {ragStatus.error && (
              <p className="error-text"><strong>Error:</strong> {ragStatus.error}</p>
            )}
            <button 
              onClick={refreshRAGIndex} 
              className="btn-refresh"
              disabled={loading}
            >
              {loading ? 'Refreshing...' : 'Refresh Index'}
            </button>
          </div>
        )}
      </div>

      {/* Search Input */}
      <div className="rag-search-input">
        <div className="search-input-container">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Search your notes with AI... (Press Enter to search)"
            className="search-input"
            disabled={loading || ragStatus?.status !== 'active'}
          />
          <button
            onClick={performRAGSearch}
            disabled={!searchQuery.trim() || loading || ragStatus?.status !== 'active'}
            className="btn-search"
          >
            {loading ? '🔍' : '🔍'}
          </button>
        </div>
      </div>

      {/* Error Messages */}
      {error && (
        <div className={`message ${error.includes('successfully') ? 'success' : 'error'}`}>
          {error}
          <button onClick={() => setError('')} className="close-message">×</button>
        </div>
      )}

      {/* Loading Indicator */}
      {loading && (
        <div className="rag-loading">
          <div className="spinner"></div>
          <span>Searching through your notes...</span>
        </div>
      )}

      {/* Search Results */}
      {ragResults && (
        <div className="rag-results">
          <div className="results-header">
            <h3>AI Search Results</h3>
            {ragResults.query && (
              <p className="search-query">Query: "{ragResults.query}"</p>
            )}
          </div>

          {/* AI Generated Response */}
          {ragResults.response && (
            <div className="ai-response">
              <h4>AI Summary</h4>
              <p>{ragResults.response}</p>
            </div>
          )}

          {/* Source Documents */}
          {ragResults.sources && ragResults.sources.length > 0 && (
            <div className="search-sources">
              <h4>Relevant Notes</h4>
              <div className="sources-list">
                {ragResults.sources.map((source, index) => (
                  <div key={index} className="source-item">
                    <div className="source-header">
                      <span className="source-similarity">
                        {formatSimilarity(source.similarity)}% match
                      </span>
                      <button
                        className="btn-view-note"
                        onClick={() => onNoteSelect && onNoteSelect(source.note_id)}
                      >
                        View Full Note
                      </button>
                    </div>
                    <div className="source-content">
                      <p>{source.preview}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Context Used (for debugging) */}
          {ragResults.context_used && ragResults.context_used.length > 0 && (
            <details className="context-details">
              <summary>View Context Used (Debug)</summary>
              <div className="context-list">
                {ragResults.context_used.map((context, index) => (
                  <div key={index} className="context-item">
                    <p>{context}</p>
                  </div>
                ))}
              </div>
            </details>
          )}

          {/* Clear Results Button */}
          <div className="results-actions">
            <button
              onClick={() => {
                setRagResults(null);
                setSearchQuery('');
              }}
              className="btn-clear"
            >
              Clear Results
            </button>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!ragResults && !loading && searchQuery && (
        <div className="empty-results">
          <p>No results found. Try a different search term.</p>
        </div>
      )}
    </div>
  );
};

export default RAGSearchComponent;
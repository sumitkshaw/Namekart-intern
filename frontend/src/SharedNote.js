import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import './SharedNote.css';

function SharedNote() {
  const { shareId } = useParams();
  const [note, setNote] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Decode the shared note from the URL parameter
    try {
      const decodedData = atob(shareId);
      const noteData = JSON.parse(decodedData);
      setNote(noteData);
    } catch (err) {
      setError('Invalid share link or corrupted data');
    }
    setLoading(false);
  }, [shareId]);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="shared-note-container">
        <div className="loading">
          <div className="spinner"></div>
          <span>Loading shared note...</span>
        </div>
      </div>
    );
  }

  if (error || !note) {
    return (
      <div className="shared-note-container">
        <div className="error-container">
          <h2>❌ Unable to load shared note</h2>
          <p>{error || 'Note not found'}</p>
          <Link to="/" className="btn btn-primary">
            Go to Notes App
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="shared-note-container">
      <div className="shared-note-header">
        <h1>📝 Shared Note</h1>
        <Link to="/" className="btn btn-secondary">
          Go to Notes App
        </Link>
      </div>
      
      <div className="shared-note-card">
        <div className="shared-note-meta">
          <span className="shared-note-date">
            Created: {formatDate(note.created_at)}
          </span>
          <span className="shared-note-version">
            v{note.version}
          </span>
        </div>
        
        <div className="shared-note-content">
          {note.content}
        </div>
        
        <div className="shared-note-footer">
          <p className="shared-disclaimer">
            📢 This note was shared from My Notes App
          </p>
        </div>
      </div>
    </div>
  );
}

export default SharedNote;
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import RAGSearchComponent from './RAGSearchComponent';
import ShareModal from './ShareModal';
import { useAuth } from './AuthContext';
import './App.css';

const API_BASE = 'http://localhost:8000/api';

function MainApp() {
  const [notes, setNotes] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState('');
  const [editingVersion, setEditingVersion] = useState(null);
  const [newNote, setNewNote] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [highlightedNoteId, setHighlightedNoteId] = useState(null);
  const [shareModalOpen, setShareModalOpen] = useState(false);
  const [noteToShare, setNoteToShare] = useState(null);

  const { currentUser, logout } = useAuth();

  // Refs for scrolling to specific notes
  const noteRefs = useRef({});

  // Handle logout
  async function handleLogout() {
    try {
      await logout();
    } catch (error) {
      console.error('Failed to log out', error);
    }
  }

  // Fetch all notes
  const fetchNotes = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`${API_BASE}/notes`);
      setNotes(response.data);
    } catch (error) {
      setError('Error fetching notes: ' + (error.response?.data?.detail || error.message));
      console.error('Error fetching notes:', error);
    }
    setLoading(false);
  };

  // Create new note
  const createNote = async () => {
    if (!newNote.trim()) return;

    setLoading(true);
    setError('');
    try {
      const response = await axios.post(`${API_BASE}/notes`, {
        content: newNote
      });
      setNotes([response.data, ...notes]);
      setNewNote('');
    } catch (error) {
      setError('Error creating note: ' + (error.response?.data?.detail || error.message));
      console.error('Error creating note:', error);
    }
    setLoading(false);
  };

  // Update note with version control
  const updateNote = async (id, content, version) => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.put(`${API_BASE}/notes/${id}`, {
        content: content,
        version: version
      });
      setNotes(notes.map(note => 
        note.id === id ? response.data : note
      ));
      setEditingId(null);
      setEditText('');
      setEditingVersion(null);
    } catch (error) {
      if (error.response?.status === 409) {
        // Conflict - note was modified by someone else
        setError('⚠️ Conflict: This note was updated by someone else. Refreshing notes...');
        setTimeout(() => {
          fetchNotes();
          cancelEditing();
        }, 2000);
      } else {
        setError('Error updating note: ' + (error.response?.data?.detail || error.message));
      }
      console.error('Error updating note:', error);
    }
    setLoading(false);
  };

  // Delete note
  const deleteNote = async (id) => {
    if (!window.confirm('Are you sure you want to delete this note?')) {
      return;
    }

    setLoading(true);
    setError('');
    try {
      await axios.delete(`${API_BASE}/notes/${id}`);
      setNotes(notes.filter(note => note.id !== id));
    } catch (error) {
      setError('Error deleting note: ' + (error.response?.data?.detail || error.message));
      console.error('Error deleting note:', error);
    }
    setLoading(false);
  };

  const startEditing = (note) => {
    setEditingId(note.id);
    setEditText(note.content);
    setEditingVersion(note.version);
  };

  const cancelEditing = () => {
    setEditingId(null);
    setEditText('');
    setEditingVersion(null);
  };

  const saveEdit = () => {
    if (!editText.trim()) return;
    updateNote(editingId, editText, editingVersion);
  };

  // Share functionality
  const openShareModal = (note) => {
    setNoteToShare(note);
    setShareModalOpen(true);
  };

  const closeShareModal = () => {
    setShareModalOpen(false);
    setNoteToShare(null);
  };

  // Handle note selection from RAG search results
  const handleNoteSelect = (noteId) => {
    // Clear any existing highlight
    setHighlightedNoteId(null);
    
    // Set the note to be highlighted
    setHighlightedNoteId(noteId);
    
    // Scroll to the note
    setTimeout(() => {
      if (noteRefs.current[noteId]) {
        noteRefs.current[noteId].scrollIntoView({
          behavior: 'smooth',
          block: 'center'
        });
      }
    }, 100);
    
    // Remove highlight after 3 seconds
    setTimeout(() => {
      setHighlightedNoteId(null);
    }, 3000);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      createNote();
    }
  };

  const handleEditKeyPress = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      saveEdit();
    } else if (e.key === 'Escape') {
      cancelEditing();
    }
  };

  // Fetch notes on component mount
  useEffect(() => {
    fetchNotes();
  }, []);

  return (
    <div className="app">
      <div className="container">
        {/* Header with Authentication */}
        <header className="header header-with-auth">
          <div className="header-content">
            <h1>My Notes App</h1>
            <p>Capture your thoughts and ideas with AI-powered search</p>
            <small style={{opacity: 0.8}}>Enhanced with RAG search, conflict detection & sharing!</small>
          </div>
          <div className="auth-controls">
            <div className="user-info">
              Welcome, {currentUser?.email}
            </div>
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          </div>
        </header>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            {error}
            <button onClick={() => setError('')} className="close-error">×</button>
          </div>
        )}

        {/* RAG Search Component */}
        <RAGSearchComponent onNoteSelect={handleNoteSelect} />

        {/* Create New Note */}
        <div className="create-note-section">
          <textarea
            value={newNote}
            onChange={(e) => setNewNote(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Write a new note... (Ctrl+Enter to save)"
            className="new-note-textarea"
            rows="4"
          />
          <div className="create-note-actions">
            <button
              onClick={createNote}
              disabled={!newNote.trim() || loading}
              className="btn btn-primary"
            >
              {loading ? 'Adding...' : 'Add Note'}
            </button>
            {newNote && (
              <button
                onClick={() => setNewNote('')}
                className="btn btn-secondary"
              >
                Clear
              </button>
            )}
          </div>
        </div>

        {/* Loading Indicator */}
        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <span>Loading...</span>
          </div>
        )}

        {/* Notes List */}
        <div className="notes-list">
          {notes.length === 0 && !loading ? (
            <div className="no-notes">
              <h3>No notes yet</h3>
              <p>Create your first note above!</p>
            </div>
          ) : (
            notes.map((note) => (
              <div 
                key={note.id} 
                className={`note-card ${highlightedNoteId === note.id ? 'highlighted' : ''}`}
                ref={(el) => noteRefs.current[note.id] = el}
              >
                <div className="note-header">
                  <div className="note-meta">
                    <span className="note-date">
                      {formatDate(note.created_at)}
                    </span>
                    <span className="note-version">
                      v{note.version}
                    </span>
                  </div>
                  <div className="note-actions">
                    {editingId === note.id ? (
                      <>
                        <button
                          onClick={saveEdit}
                          className="btn-icon btn-save"
                          title="Save (Ctrl+Enter)"
                        >
                          ✓
                        </button>
                        <button
                          onClick={cancelEditing}
                          className="btn-icon btn-cancel"
                          title="Cancel (Esc)"
                        >
                          ✕
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          onClick={() => startEditing(note)}
                          className="btn-icon btn-edit"
                          title="Edit"
                        >
                          ✎
                        </button>
                        <button
                          onClick={() => openShareModal(note)}
                          className="btn-icon btn-share"
                          title="Share"
                        >
                          🔗
                        </button>
                        <button
                          onClick={() => deleteNote(note.id)}
                          className="btn-icon btn-delete"
                          title="Delete"
                        >
                          🗑
                        </button>
                      </>
                    )}
                  </div>
                </div>
                
                {editingId === note.id ? (
                  <div>
                    <textarea
                      value={editText}
                      onChange={(e) => setEditText(e.target.value)}
                      onKeyDown={handleEditKeyPress}
                      className="edit-textarea"
                      rows="4"
                      autoFocus
                    />
                    <small style={{color: '#666', fontSize: '0.8rem'}}>
                      Editing version {editingVersion}
                    </small>
                  </div>
                ) : (
                  <p className="note-content">{note.content}</p>
                )}
              </div>
            ))
          )}
        </div>

        {/* Refresh Button */}
        <div className="refresh-section">
          <button
            onClick={fetchNotes}
            className="btn btn-secondary"
            disabled={loading}
          >
            Refresh Notes
          </button>
        </div>

        {/* Share Modal */}
        <ShareModal 
          note={noteToShare}
          isOpen={shareModalOpen}
          onClose={closeShareModal}
        />
      </div>
    </div>
  );
}

export default MainApp;
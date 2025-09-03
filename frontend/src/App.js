import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [notes, setNotes] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState('');
  const [newNote, setNewNote] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch all notes
  const fetchNotes = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`${API_BASE}/notes`);
      setNotes(response.data);
    } catch (error) {
      setError('Error fetching notes');
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
      setError('Error creating note');
      console.error('Error creating note:', error);
    }
    setLoading(false);
  };

  // Update note
  const updateNote = async (id, content) => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.put(`${API_BASE}/notes/${id}`, {
        content: content
      });
      setNotes(notes.map(note => 
        note.id === id ? response.data : note
      ));
      setEditingId(null);
      setEditText('');
    } catch (error) {
      setError('Error updating note');
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
      setError('Error deleting note');
      console.error('Error deleting note:', error);
    }
    setLoading(false);
  };

  const startEditing = (note) => {
    setEditingId(note.id);
    setEditText(note.content);
  };

  const cancelEditing = () => {
    setEditingId(null);
    setEditText('');
  };

  const saveEdit = () => {
    if (!editText.trim()) return;
    updateNote(editingId, editText);
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
        {/* Header */}
        <header className="header">
          <h1>My Notes App</h1>
          <p>Capture your thoughts and ideas</p>
        </header>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            {error}
            <button onClick={() => setError('')} className="close-error">×</button>
          </div>
        )}

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
              <div key={note.id} className="note-card">
                <div className="note-header">
                  <span className="note-date">
                    {formatDate(note.created_at)}
                  </span>
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
                  <textarea
                    value={editText}
                    onChange={(e) => setEditText(e.target.value)}
                    onKeyDown={handleEditKeyPress}
                    className="edit-textarea"
                    rows="4"
                    autoFocus
                  />
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
      </div>
    </div>
  );
}

export default App;
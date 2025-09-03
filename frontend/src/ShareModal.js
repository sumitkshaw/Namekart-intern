import React, { useState } from 'react';
import './ShareModal.css';

function ShareModal({ note, isOpen, onClose }) {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !note) return null;

  // Generate shareable link by encoding note data in base64
  const generateShareLink = () => {
    const noteData = {
      id: note.id,
      content: note.content,
      created_at: note.created_at,
      version: note.version
    };
    const encodedData = btoa(JSON.stringify(noteData));
    return `${window.location.origin}/share/${encodedData}`;
  };

  const shareLink = generateShareLink();

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(shareLink);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy link:', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = shareLink;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const shareViaEmail = () => {
    const subject = encodeURIComponent('Check out this note');
    const body = encodeURIComponent(`Hi! I wanted to share this note with you:\n\n${shareLink}`);
    window.open(`mailto:?subject=${subject}&body=${body}`);
  };

  const shareViaWhatsApp = () => {
    const text = encodeURIComponent(`Check out this note: ${shareLink}`);
    window.open(`https://wa.me/?text=${text}`, '_blank');
  };

  const shareViaTwitter = () => {
    const text = encodeURIComponent('Check out this note:');
    const url = encodeURIComponent(shareLink);
    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank');
  };

  return (
    <div className="share-modal-overlay" onClick={onClose}>
      <div className="share-modal" onClick={(e) => e.stopPropagation()}>
        <div className="share-modal-header">
          <h2>📤 Share Note</h2>
          <button className="share-modal-close" onClick={onClose}>×</button>
        </div>
        
        <div className="share-modal-content">
          <div className="note-preview">
            <h3>Note Preview:</h3>
            <div className="note-preview-content">
              {note.content.length > 100 
                ? `${note.content.substring(0, 100)}...` 
                : note.content
              }
            </div>
          </div>
          
          <div className="share-link-section">
            <label>Share Link:</label>
            <div className="share-link-container">
              <input 
                type="text" 
                value={shareLink} 
                readOnly 
                className="share-link-input"
              />
              <button 
                onClick={copyToClipboard}
                className={`copy-btn ${copied ? 'copied' : ''}`}
              >
                {copied ? '✓ Copied!' : '📋 Copy'}
              </button>
            </div>
          </div>
          
          <div className="share-options">
            <h3>Share via:</h3>
            <div className="share-buttons">
              <button onClick={shareViaEmail} className="share-btn email-btn">
                📧 Email
              </button>
              <button onClick={shareViaWhatsApp} className="share-btn whatsapp-btn">
                💬 WhatsApp
              </button>
              <button onClick={shareViaTwitter} className="share-btn twitter-btn">
                🐦 Twitter
              </button>
            </div>
          </div>
          
          <div className="share-info">
            <p>⚠️ <strong>Note:</strong> This link contains the note content and can be accessed by anyone who has it. The shared note is a snapshot and won't update if you modify the original.</p>
          </div>
        </div>
        
        <div className="share-modal-footer">
          <button onClick={onClose} className="btn btn-secondary">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default ShareModal;
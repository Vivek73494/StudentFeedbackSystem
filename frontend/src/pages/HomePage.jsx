import React from 'react';

export default function HomePage({ onNavigate }) {
  return (
    <div className="page-bg-overlay home-bg">
      <div className="glass-container">
        <h1 className="main-title">Online Student Feedback</h1>
        <p className="subtitle">Select Your Portal</p>
        
        <div className="button-group">
          <button
            className="glass-button"
            onClick={() => onNavigate('student-login')}
          >
            <span className="icon">👨‍🎓</span>
            <span className="button-text">Student Login</span>
          </button>
          
          <button
            className="glass-button"
            onClick={() => onNavigate('faculty-login')}
          >
            <span className="icon">👨‍🏫</span>
            <span className="button-text">Faculty Login</span>
          </button>
          
          <button
            className="glass-button"
            onClick={() => onNavigate('admin-login')}
          >
            <span className="icon">⚙️</span>
            <span className="button-text">Admin Login</span>
          </button>
        </div>
      </div>
    </div>
  );
}

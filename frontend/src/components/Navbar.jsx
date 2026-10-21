import React from 'react';

export default function Navbar({ title, user, onLogout }) {
  const getRoleIcon = (role) => {
    switch (role) {
      case 'student':
        return '👨‍🎓';
      case 'faculty':
        return '👨‍🏫';
      case 'admin':
        return '⚙️';
      default:
        return '👤';
    }
  };

  return (
    <nav className="dashboard-navbar">
      <div className="navbar-brand">
        <span style={{ fontSize: '1.7rem' }}>🎓</span>
        <span>{title || 'Student Feedback System'}</span>
      </div>
      <div className="navbar-user-info">
        {user && (
          <div className="user-badge">
            <span>{getRoleIcon(user.role)}</span>
            <span>
              <strong>{user.name || user.username}</strong> ({user.role?.toUpperCase()})
            </span>
          </div>
        )}
        <button className="logout-btn" onClick={onLogout}>
          <span>🚪</span>
          <span>Logout</span>
        </button>
      </div>
    </nav>
  );
}

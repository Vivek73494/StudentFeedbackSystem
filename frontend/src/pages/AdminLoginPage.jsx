import React, { useState } from 'react';
import { authService } from '../services/api';
import Alert from '../components/Alert';

export default function AdminLoginPage({ onLoginSuccess, onNavigate }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      setAlert({ type: 'error', message: 'Please enter both username and password' });
      return;
    }

    setLoading(true);
    setAlert(null);
    try {
      const res = await authService.login(username, password, 'admin');
      setAlert({ type: 'success', message: 'Admin login successful!' });
      setTimeout(() => {
        onLoginSuccess(res.user);
      }, 500);
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Invalid admin login' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-bg-overlay admin-login-bg">
      <div className="glass-container">
        <h1 className="main-title">Admin Login</h1>
        <p className="subtitle">System administration and report management</p>

        {alert && (
          <Alert
            type={alert.type}
            message={alert.message}
            onClose={() => setAlert(null)}
          />
        )}

        <form onSubmit={handleLogin} autoComplete="off">
          <div className="input-group">
            <label className="input-label">Username</label>
            <input
              type="text"
              className="form-control"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label className="input-label">Password</label>
            <input
              type="password"
              className="form-control"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="glass-button login-btn" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <button
          onClick={() => onNavigate('home')}
          className="back-link"
          style={{ background: 'none', border: 'none', cursor: 'pointer' }}
        >
          ← Back to Home
        </button>
      </div>
    </div>
  );
}

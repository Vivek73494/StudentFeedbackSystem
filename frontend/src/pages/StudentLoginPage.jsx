import React, { useState } from 'react';
import { authService } from '../services/api';
import Alert from '../components/Alert';

export default function StudentLoginPage({ onLoginSuccess, onNavigate }) {
  const [isRegistering, setIsRegistering] = useState(false);
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState(null);

  // Form states
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [rollNumber, setRollNumber] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      setAlert({ type: 'error', message: 'Please enter both username and password' });
      return;
    }

    setLoading(true);
    setAlert(null);
    try {
      const res = await authService.login(username, password, 'student');
      setAlert({ type: 'success', message: 'Student login successful!' });
      setTimeout(() => {
        onLoginSuccess(res.user);
      }, 500);
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Invalid student login' });
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!username || !password || !name) {
      setAlert({ type: 'error', message: 'Username, password, and name are required' });
      return;
    }

    setLoading(true);
    setAlert(null);
    try {
      await authService.registerStudent({
        username,
        password,
        name,
        student_email: email,
        roll_number: rollNumber,
      });
      setAlert({ type: 'success', message: 'Registration successful! You can now log in.' });
      setIsRegistering(false);
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Registration failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-bg-overlay student-login-bg">
      <div className="glass-container">
        <h1 className="main-title">{isRegistering ? 'Student Register' : 'Student Login'}</h1>
        <p className="subtitle">
          {isRegistering ? 'Create your student feedback account' : 'Access your feedback portal'}
        </p>

        {alert && (
          <Alert
            type={alert.type}
            message={alert.message}
            onClose={() => setAlert(null)}
          />
        )}

        {isRegistering ? (
          <form onSubmit={handleRegister} autoComplete="off">
            <div className="input-group">
              <label className="input-label">Username *</label>
              <input
                type="text"
                className="form-control"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>

            <div className="input-group">
              <label className="input-label">Full Name *</label>
              <input
                type="text"
                className="form-control"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div className="input-group">
              <label className="input-label">Email</label>
              <input
                type="email"
                className="form-control"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div className="input-group">
              <label className="input-label">Roll Number</label>
              <input
                type="text"
                className="form-control"
                value={rollNumber}
                onChange={(e) => setRollNumber(e.target.value)}
              />
            </div>

            <div className="input-group">
              <label className="input-label">Password *</label>
              <input
                type="password"
                className="form-control"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="glass-button login-btn" disabled={loading}>
              {loading ? 'Registering...' : 'Register Account'}
            </button>

            <p style={{ marginTop: '16px', color: '#ffffff', fontSize: '0.9rem' }}>
              Already registered?{' '}
              <button
                type="button"
                onClick={() => {
                  setIsRegistering(false);
                  setAlert(null);
                }}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#4facfe',
                  fontWeight: '600',
                  cursor: 'pointer',
                  textDecoration: 'underline',
                }}
              >
                Log In
              </button>
            </p>
          </form>
        ) : (
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

            <p style={{ marginTop: '16px', color: '#ffffff', fontSize: '0.9rem' }}>
              New student?{' '}
              <button
                type="button"
                onClick={() => {
                  setIsRegistering(true);
                  setAlert(null);
                }}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#4facfe',
                  fontWeight: '600',
                  cursor: 'pointer',
                  textDecoration: 'underline',
                }}
              >
                Register Here
              </button>
            </p>
          </form>
        )}

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

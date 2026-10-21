import React, { useState, useEffect } from 'react';
import HomePage from './pages/HomePage';
import StudentLoginPage from './pages/StudentLoginPage';
import FacultyLoginPage from './pages/FacultyLoginPage';
import AdminLoginPage from './pages/AdminLoginPage';
import StudentDashboard from './pages/StudentDashboard';
import FacultyDashboard from './pages/FacultyDashboard';
import AdminDashboard from './pages/AdminDashboard';
import { authService } from './services/api';

export default function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [currentUser, setCurrentUser] = useState(null);
  const [loadingInitial, setLoadingInitial] = useState(true);

  useEffect(() => {
    // Check local storage and backend session on startup
    const checkAuth = async () => {
      const stored = authService.getStoredUser();
      if (stored) {
        setCurrentUser(stored);
      }
      try {
        const res = await authService.getMe();
        if (res.authenticated && res.user) {
          setCurrentUser(res.user);
        } else if (!stored) {
          setCurrentUser(null);
        }
      } catch (err) {
        // Fallback to local user if backend offline or CORS error during boot
      } finally {
        setLoadingInitial(false);
      }
    };

    checkAuth();
  }, []);

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
  };

  const handleLogout = async () => {
    await authService.logout();
    setCurrentUser(null);
    setCurrentPage('home');
  };

  if (loadingInitial) {
    return (
      <div
        style={{
          display: 'flex',
          height: '100vh',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff',
          fontSize: '1.2rem',
          fontWeight: 600,
        }}
      >
        Initializing Student Feedback System...
      </div>
    );
  }

  // If user is authenticated, route to their role dashboard
  if (currentUser) {
    switch (currentUser.role) {
      case 'student':
        return <StudentDashboard user={currentUser} onLogout={handleLogout} />;
      case 'faculty':
        return <FacultyDashboard user={currentUser} onLogout={handleLogout} />;
      case 'admin':
        return <AdminDashboard user={currentUser} onLogout={handleLogout} />;
      default:
        return (
          <div style={{ padding: '40px', color: 'white', textAlign: 'center' }}>
            Unknown user role. <button onClick={handleLogout}>Logout</button>
          </div>
        );
    }
  }

  // If not authenticated, route based on selected portal
  switch (currentPage) {
    case 'student-login':
      return (
        <StudentLoginPage
          onLoginSuccess={handleLoginSuccess}
          onNavigate={(page) => setCurrentPage(page)}
        />
      );
    case 'faculty-login':
      return (
        <FacultyLoginPage
          onLoginSuccess={handleLoginSuccess}
          onNavigate={(page) => setCurrentPage(page)}
        />
      );
    case 'admin-login':
      return (
        <AdminLoginPage
          onLoginSuccess={handleLoginSuccess}
          onNavigate={(page) => setCurrentPage(page)}
        />
      );
    case 'home':
    default:
      return <HomePage onNavigate={(page) => setCurrentPage(page)} />;
  }
}

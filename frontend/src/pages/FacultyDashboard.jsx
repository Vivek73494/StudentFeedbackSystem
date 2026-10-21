import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import Alert from '../components/Alert';
import StarRating from '../components/StarRating';
import StatCard from '../components/StatCard';
import { feedbackService, reportService } from '../services/api';

export default function FacultyDashboard({ user, onLogout }) {
  const [feedbacks, setFeedbacks] = useState([]);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState(null);
  const [showReportText, setShowReportText] = useState(false);

  useEffect(() => {
    loadFacultyData();
  }, [user]);

  const loadFacultyData = async () => {
    setLoading(true);
    try {
      const [feedbackList, reportData] = await Promise.all([
        feedbackService.getFacultyFeedback(user?.username),
        reportService.getFacultyReport(user?.username),
      ]);
      setFeedbacks(feedbackList || []);
      setReport(reportData || null);
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Failed to load faculty feedback data' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-page faculty-dashboard-page">
      <div className="dashboard-container">
        <Navbar title="Faculty Feedback Portal" user={user} onLogout={onLogout} />

        {alert && (
          <Alert
            type={alert.type}
            message={alert.message}
            onClose={() => setAlert(null)}
          />
        )}

        {/* FACULTY PROFILE BANNER */}
        <div className="info-banner">
          <div>
            <h3>Welcome, {user?.name || user?.username}! 👨‍🏫</h3>
            <p>
              Assigned Course: <strong>{user?.course_name || 'N/A'}</strong> (Code: <code>{user?.course_code || 'N/A'}</code>)
              {user?.department && <span> • Department: {user.department}</span>}
            </p>
          </div>
          <div>
            <button
              className="btn-primary"
              onClick={() => setShowReportText(!showReportText)}
              style={{ background: 'rgba(255, 255, 255, 0.25)', border: '1px solid white' }}
            >
              {showReportText ? 'Hide Formatted Report' : '📄 View Full Report'}
            </button>
          </div>
        </div>

        {/* STATS OVERVIEW */}
        <div className="stats-grid">
          <StatCard
            title="Total Submissions"
            value={report?.total_responses ?? feedbacks.length}
            icon="👥"
            borderColor="#4facfe"
          />
          <StatCard
            title="Average Course Rating"
            value={
              report?.average_rating ? (
                <span>
                  {report.average_rating} <small style={{ fontSize: '1rem', color: '#718096' }}>/ 5.0</small>
                </span>
              ) : (
                '0.0'
              )
            }
            icon="⭐"
            borderColor="#ecc94b"
          />
          <StatCard
            title="Course Code"
            value={user?.course_code || 'N/A'}
            icon="🏷️"
            borderColor="#6a5af9"
          />
        </div>

        {/* FACULTY REPORT VIEW */}
        {showReportText && (report?.formatted_report_text || report?.soap_compatible_text) && (
          <div className="dashboard-card" style={{ borderLeft: '6px solid #6a5af9' }}>
            <div className="card-header">
              <h2 className="card-title">
                <span>📄</span> Official Faculty Feedback Report
              </h2>
              <button
                className="btn-primary"
                onClick={() => {
                  navigator.clipboard.writeText(report.formatted_report_text || report.soap_compatible_text);
                  setAlert({ type: 'success', message: 'Report copied to clipboard!' });
                }}
                style={{ fontSize: '0.85rem', padding: '6px 14px' }}
              >
                📋 Copy Text
              </button>
            </div>
            <pre
              style={{
                background: '#1a202c',
                color: '#68d391',
                padding: '20px',
                borderRadius: '10px',
                fontFamily: 'Consolas, monospace',
                fontSize: '0.9rem',
                overflowX: 'auto',
                whiteSpace: 'pre-wrap',
                maxHeight: '350px',
              }}
            >
              {report.formatted_report_text || report.soap_compatible_text}
            </pre>
          </div>
        )}

        {/* FEEDBACK LIST */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">
              <span>💬</span> Student Feedback Submissions ({feedbacks.length})
            </h2>
          </div>

          {loading ? (
            <p className="empty-state">Loading student feedback submissions...</p>
          ) : feedbacks.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📭</div>
              <p>No student feedback has been submitted for your course yet.</p>
            </div>
          ) : (
            <div>
              {feedbacks.map((fb, idx) => (
                <div key={fb._id || idx} className="feedback-card">
                  <div className="feedback-meta">
                    <div>
                      <span className="student-tag">👨‍🎓 Student: {fb.student_username}</span>
                      <span style={{ marginLeft: '12px', color: '#718096', fontSize: '0.9rem' }}>
                        Course: <strong>{fb.course_code}</strong>
                      </span>
                    </div>
                    <div className="rating-badge">
                      <StarRating rating={fb.rating} />
                    </div>
                  </div>

                  {fb.answers && fb.answers.length > 0 && (
                    <ul className="feedback-answers-list">
                      {fb.answers.map((ans, aidx) => (
                        <li key={aidx} className="feedback-answer-item">
                          <div className="feedback-question-title">{ans.question}</div>
                          <div className="feedback-answer-text">
                            {/^[1-5](\.0)?$/.test(ans.answer) ? (
                              <span>★ {ans.answer} / 5</span>
                            ) : (
                              ans.answer
                            )}
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}

                  {fb.comments && !fb.answers && (
                    <div className="feedback-answer-item">
                      <div className="feedback-question-title">Comments</div>
                      <div className="feedback-answer-text">{fb.comments}</div>
                    </div>
                  )}

                  <div style={{ fontSize: '0.85rem', color: '#a0aec0', textAlign: 'right' }}>
                    Submitted on: {fb.submitted_at ? new Date(fb.submitted_at).toLocaleString() : 'N/A'}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import Alert from '../components/Alert';
import StarRating from '../components/StarRating';
import { courseService, questionService, feedbackService } from '../services/api';

export default function StudentDashboard({ user, onLogout }) {
  const [courses, setCourses] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [alert, setAlert] = useState(null);

  // Form State
  const [selectedCourse, setSelectedCourse] = useState('');
  const [answers, setAnswers] = useState({});

  useEffect(() => {
    loadData();
  }, [user]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [coursesData, questionsData, historyData] = await Promise.all([
        courseService.getAll(),
        questionService.getAll(),
        feedbackService.getStudentFeedback(user?.username),
      ]);
      setCourses(coursesData || []);
      setQuestions(questionsData || []);
      setHistory(historyData || []);
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Failed to load dashboard data' });
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId, value) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: value,
    }));
  };

  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    if (!selectedCourse) {
      setAlert({ type: 'error', message: 'Please select a course' });
      return;
    }

    // Check that all questions have been answered
    for (const q of questions) {
      const qKey = q._id || q.question_text;
      if (!answers[qKey] || answers[qKey].toString().trim() === '') {
        setAlert({
          type: 'error',
          message: `Please answer question: "${q.question_text || q.question}"`,
        });
        return;
      }
    }

    setSubmitting(true);
    setAlert(null);

    const formattedAnswers = questions.map((q) => {
      const qKey = q._id || q.question_text;
      return {
        question: q.question_text || q.question,
        answer: answers[qKey],
      };
    });

    try {
      await feedbackService.submit({
        course_code: selectedCourse,
        student_username: user.username,
        answers: formattedAnswers,
      });

      setAlert({ type: 'success', message: 'Feedback submitted successfully!' });
      // Reset form
      setSelectedCourse('');
      setAnswers({});
      // Reload history
      const updatedHistory = await feedbackService.getStudentFeedback(user.username);
      setHistory(updatedHistory || []);
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Failed to submit feedback' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="dashboard-page student-dashboard-page">
      <div className="dashboard-container">
        <Navbar title="Student Feedback Dashboard" user={user} onLogout={onLogout} />

        {alert && (
          <Alert
            type={alert.type}
            message={alert.message}
            onClose={() => setAlert(null)}
          />
        )}

        <div className="info-banner">
          <div>
            <h3>Welcome back, {user?.name || user?.username}! 🎓</h3>
            <p>Your honest feedback helps improve academic quality and classroom learning.</p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '0.9rem', opacity: 0.9 }}>Submissions:</span>
            <div style={{ fontSize: '1.6rem', fontWeight: 700 }}>{history.length}</div>
          </div>
        </div>

        {/* FEEDBACK FORM */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">
              <span>✍️</span> Submit Course Feedback
            </h2>
          </div>

          {loading ? (
            <p className="empty-state">Loading courses and questions from database...</p>
          ) : courses.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📚</div>
              <p>No courses available right now. Please check back later or contact admin.</p>
            </div>
          ) : questions.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">❓</div>
              <p>No feedback questions available right now.</p>
            </div>
          ) : (
            <form onSubmit={handleSubmitFeedback}>
              <div className="input-group">
                <label className="input-label" style={{ color: '#2d3748', textShadow: 'none' }}>
                  <strong>Select Course *</strong>
                </label>
                <select
                  className="form-control select-control"
                  value={selectedCourse}
                  onChange={(e) => setSelectedCourse(e.target.value)}
                  required
                >
                  <option value="">-- Choose a Course --</option>
                  {courses.map((c) => (
                    <option key={c.course_code} value={c.course_code}>
                      {c.course_name} ({c.course_code})
                    </option>
                  ))}
                </select>
              </div>

              <div style={{ margin: '24px 0 16px' }}>
                <h3 style={{ fontSize: '1.1rem', color: '#2d3748', marginBottom: '16px' }}>
                  Feedback Questions
                </h3>

                {questions.map((q, index) => {
                  const qKey = q._id || q.question_text;
                  const currentAnswer = answers[qKey] || '';
                  const isRating = q.question_type === 'rating';

                  return (
                    <div
                      key={qKey}
                      style={{
                        background: '#f8fafc',
                        border: '1px solid #e2e8f0',
                        borderRadius: '12px',
                        padding: '16px 20px',
                        marginBottom: '16px',
                      }}
                    >
                      <label style={{ display: 'block', fontWeight: 600, color: '#2d3748', marginBottom: '8px' }}>
                        {index + 1}. {q.question_text || q.question}
                      </label>

                      {isRating ? (
                        <div>
                          <StarRating
                            rating={currentAnswer ? Number(currentAnswer) : 0}
                            interactive={true}
                            onChange={(val) => handleAnswerChange(qKey, val)}
                          />
                        </div>
                      ) : (
                        <textarea
                          className="form-control"
                          rows="2"
                          placeholder="Type your response here..."
                          value={currentAnswer}
                          onChange={(e) => handleAnswerChange(qKey, e.target.value)}
                          required
                        />
                      )}
                    </div>
                  );
                })}
              </div>

              <button
                type="submit"
                className="btn-primary"
                disabled={submitting}
                style={{ width: '100%', padding: '14px', fontSize: '1.05rem' }}
              >
                {submitting ? 'Submitting Feedback...' : '🚀 Submit Feedback'}
              </button>
            </form>
          )}
        </div>

        {/* FEEDBACK HISTORY */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">
              <span>📋</span> Your Feedback History ({history.length})
            </h2>
          </div>

          {history.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📝</div>
              <p>You haven't submitted any feedback yet. Choose a course above to begin!</p>
            </div>
          ) : (
            <div>
              {history.map((fb, idx) => (
                <div key={fb._id || idx} className="feedback-card">
                  <div className="feedback-meta">
                    <div>
                      <strong style={{ fontSize: '1.1rem', color: '#1a202c' }}>
                        {fb.course_name || fb.course_code}
                      </strong>
                      <span style={{ color: '#718096', marginLeft: '8px' }}>({fb.course_code})</span>
                      {fb.faculty_name && (
                        <span style={{ marginLeft: '12px', color: '#4a5568', fontSize: '0.9rem' }}>
                          👨‍🏫 Faculty: <strong>{fb.faculty_name}</strong>
                        </span>
                      )}
                    </div>
                    <div className="rating-badge">
                      <StarRating rating={fb.rating} />
                    </div>
                  </div>

                  {fb.answers && (
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

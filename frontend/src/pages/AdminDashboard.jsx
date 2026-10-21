import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import Alert from '../components/Alert';
import StatCard from '../components/StatCard';
import StarRating from '../components/StarRating';
import {
  courseService,
  questionService,
  feedbackService,
  reportService,
  adminService,
} from '../services/api';

export default function AdminDashboard({ user, onLogout }) {
  const [activeTab, setActiveTab] = useState('feedback');
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState(null);

  // Data states
  const [stats, setStats] = useState({});
  const [courses, setCourses] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [feedbackList, setFeedbackList] = useState([]);
  const [facultyList, setFacultyList] = useState([]);
  const [studentsList, setStudentsList] = useState([]);

  // Filter state
  const [selectedCourseFilter, setSelectedCourseFilter] = useState('all');

  // Form states
  const [newCourse, setNewCourse] = useState({ course_name: '', course_code: '' });
  const [newQuestion, setNewQuestion] = useState({ question_text: '', question_type: 'rating' });
  const [newStudent, setNewStudent] = useState({
    username: '',
    password: '',
    name: '',
    student_email: '',
    roll_number: '',
  });
  const [newFaculty, setNewFaculty] = useState({
    username: '',
    password: '',
    name: '',
    course_name: '',
    course_code: '',
    faculty_email: '',
    department: '',
  });

  // Report state
  const [selectedFacultyForReport, setSelectedFacultyForReport] = useState('');
  const [facultyReport, setFacultyReport] = useState(null);
  const [loadingReport, setLoadingReport] = useState(false);

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [statsData, coursesData, questionsData, feedbackData, facultyData, studentsData] =
        await Promise.all([
          adminService.getStats(),
          courseService.getAll(),
          questionService.getAll(),
          feedbackService.getAll(),
          adminService.getFaculty(),
          adminService.getStudents(),
        ]);
      setStats(statsData || {});
      setCourses(coursesData || []);
      setQuestions(questionsData || []);
      setFeedbackList(feedbackData || []);
      setFacultyList(facultyData || []);
      setStudentsList(studentsData || []);
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Failed to load admin data' });
    } finally {
      setLoading(false);
    }
  };

  // Filter feedback
  const handleFilterChange = async (courseCode) => {
    setSelectedCourseFilter(courseCode);
    try {
      const data = await feedbackService.getAll({
        course_filter: courseCode === 'all' ? undefined : courseCode,
      });
      setFeedbackList(data || []);
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Failed to filter feedback' });
    }
  };

  // Add Course
  const handleAddCourse = async (e) => {
    e.preventDefault();
    if (!newCourse.course_name || !newCourse.course_code) {
      setAlert({ type: 'error', message: 'Please enter course name and course code' });
      return;
    }
    try {
      await courseService.add(newCourse);
      setAlert({ type: 'success', message: `Course '${newCourse.course_name}' added successfully!` });
      setNewCourse({ course_name: '', course_code: '' });
      const [updatedCourses, updatedStats] = await Promise.all([
        courseService.getAll(),
        adminService.getStats(),
      ]);
      setCourses(updatedCourses);
      setStats(updatedStats);
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Failed to add course' });
    }
  };

  // Delete Course
  const handleDeleteCourse = async (courseCode) => {
    if (!window.confirm(`Are you sure you want to delete course ${courseCode}?`)) return;
    try {
      await courseService.delete(courseCode);
      setAlert({ type: 'success', message: `Course '${courseCode}' deleted successfully` });
      const [updatedCourses, updatedStats] = await Promise.all([
        courseService.getAll(),
        adminService.getStats(),
      ]);
      setCourses(updatedCourses);
      setStats(updatedStats);
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Failed to delete course' });
    }
  };

  // Add Question
  const handleAddQuestion = async (e) => {
    e.preventDefault();
    if (!newQuestion.question_text || !newQuestion.question_type) {
      setAlert({ type: 'error', message: 'Please provide question text and question type' });
      return;
    }
    try {
      await questionService.add(newQuestion);
      setAlert({ type: 'success', message: 'Feedback question added successfully!' });
      setNewQuestion({ question_text: '', question_type: 'rating' });
      const [updatedQuestions, updatedStats] = await Promise.all([
        questionService.getAll(),
        adminService.getStats(),
      ]);
      setQuestions(updatedQuestions);
      setStats(updatedStats);
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Failed to add question' });
    }
  };

  // Delete Question
  const handleDeleteQuestion = async (questionId) => {
    if (!window.confirm('Are you sure you want to delete this question?')) return;
    try {
      await questionService.delete(questionId);
      setAlert({ type: 'success', message: 'Question deleted successfully!' });
      const [updatedQuestions, updatedStats] = await Promise.all([
        questionService.getAll(),
        adminService.getStats(),
      ]);
      setQuestions(updatedQuestions);
      setStats(updatedStats);
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Failed to delete question' });
    }
  };

  // Add Student
  const handleAddStudent = async (e) => {
    e.preventDefault();
    if (!newStudent.username || !newStudent.password || !newStudent.name) {
      setAlert({ type: 'error', message: 'Username, password, and name are required' });
      return;
    }
    try {
      await adminService.addStudent(newStudent);
      setAlert({ type: 'success', message: `Student '${newStudent.name}' added successfully!` });
      setNewStudent({
        username: '',
        password: '',
        name: '',
        student_email: '',
        roll_number: '',
      });
      const [updatedStudents, updatedStats] = await Promise.all([
        adminService.getStudents(),
        adminService.getStats(),
      ]);
      setStudentsList(updatedStudents);
      setStats(updatedStats);
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Failed to add student' });
    }
  };

  // Add Faculty
  const handleAddFaculty = async (e) => {
    e.preventDefault();
    if (!newFaculty.username || !newFaculty.password || !newFaculty.name) {
      setAlert({ type: 'error', message: 'Username, password, and faculty name are required' });
      return;
    }
    try {
      await adminService.addFaculty(newFaculty);
      setAlert({ type: 'success', message: `Faculty member '${newFaculty.name}' added successfully!` });
      setNewFaculty({
        username: '',
        password: '',
        name: '',
        course_name: '',
        course_code: '',
        faculty_email: '',
        department: '',
      });
      const [updatedFaculty, updatedStats] = await Promise.all([
        adminService.getFaculty(),
        adminService.getStats(),
      ]);
      setFacultyList(updatedFaculty);
      setStats(updatedStats);
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Failed to add faculty' });
    }
  };

  // Generate Faculty Report
  const handleGenerateReport = async (facultyId) => {
    setSelectedFacultyForReport(facultyId);
    if (!facultyId) {
      setFacultyReport(null);
      return;
    }
    setLoadingReport(true);
    try {
      const data = await reportService.getFacultyReport(facultyId);
      setFacultyReport(data);
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Failed to generate report' });
    } finally {
      setLoadingReport(false);
    }
  };

  return (
    <div className="dashboard-page admin-dashboard-page">
      <div className="dashboard-container">
        <Navbar title="System Administrator Dashboard" user={user} onLogout={onLogout} />

        {alert && (
          <Alert
            type={alert.type}
            message={alert.message}
            onClose={() => setAlert(null)}
          />
        )}

        {/* METRICS / STATS OVERVIEW */}
        <div className="stats-grid">
          <StatCard
            title="Total Submissions"
            value={stats.total_feedbacks ?? 0}
            icon="💬"
            borderColor="#4facfe"
          />
          <StatCard
            title="Average Rating"
            value={
              stats.average_rating ? (
                <span>
                  {stats.average_rating} <small style={{ fontSize: '1rem', color: '#718096' }}>/ 5.0</small>
                </span>
              ) : (
                '0.0'
              )
            }
            icon="⭐"
            borderColor="#ecc94b"
          />
          <StatCard
            title="Active Courses"
            value={stats.total_courses ?? courses.length}
            icon="📚"
            borderColor="#6a5af9"
          />
          <StatCard
            title="Registered Students"
            value={stats.total_students ?? studentsList.length}
            icon="👨‍🎓"
            borderColor="#38a169"
          />
          <StatCard
            title="Faculty Members"
            value={stats.total_faculty ?? facultyList.length}
            icon="👨‍🏫"
            borderColor="#3182ce"
          />
          <StatCard
            title="Feedback Questions"
            value={stats.total_questions ?? questions.length}
            icon="❓"
            borderColor="#d69e2e"
          />
        </div>

        {/* NAVIGATION TABS */}
        <div className="dashboard-card" style={{ padding: '20px 24px 0', marginBottom: '20px' }}>
          <div className="tabs-nav">
            <button
              className={`tab-btn ${activeTab === 'feedback' ? 'active' : ''}`}
              onClick={() => setActiveTab('feedback')}
            >
              📋 All Feedback ({feedbackList.length})
            </button>
            <button
              className={`tab-btn ${activeTab === 'reports' ? 'active' : ''}`}
              onClick={() => setActiveTab('reports')}
            >
              📈 Faculty Reports
            </button>
            <button
              className={`tab-btn ${activeTab === 'questions' ? 'active' : ''}`}
              onClick={() => setActiveTab('questions')}
            >
              ❓ Questions ({questions.length})
            </button>
            <button
              className={`tab-btn ${activeTab === 'courses' ? 'active' : ''}`}
              onClick={() => setActiveTab('courses')}
            >
              📚 Courses ({courses.length})
            </button>
            <button
              className={`tab-btn ${activeTab === 'faculty' ? 'active' : ''}`}
              onClick={() => setActiveTab('faculty')}
            >
              👨‍🏫 Faculty ({facultyList.length})
            </button>
            <button
              className={`tab-btn ${activeTab === 'students' ? 'active' : ''}`}
              onClick={() => setActiveTab('students')}
            >
              👨‍🎓 Students ({studentsList.length})
            </button>
          </div>
        </div>

        {/* TAB 1: ALL FEEDBACK */}
        {activeTab === 'feedback' && (
          <div className="dashboard-card">
            <div className="card-header" style={{ flexWrap: 'wrap', gap: '14px' }}>
              <h2 className="card-title">
                <span>💬</span> All Student Feedback Submissions
              </h2>
              {/* Filter */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <label style={{ fontWeight: 600, color: '#4a5568' }}>Filter by Course:</label>
                <select
                  className="form-control select-control"
                  style={{ width: '240px', padding: '8px 14px' }}
                  value={selectedCourseFilter}
                  onChange={(e) => handleFilterChange(e.target.value)}
                >
                  <option value="all">All Courses</option>
                  {courses.map((c) => (
                    <option key={c.course_code} value={c.course_code}>
                      {c.course_name} ({c.course_code})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {loading ? (
              <p className="empty-state">Loading feedback responses...</p>
            ) : feedbackList.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📭</div>
                <p>No feedback found for the selected filter.</p>
              </div>
            ) : (
              <div className="table-responsive">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Student</th>
                      <th>Course</th>
                      <th>Faculty</th>
                      <th>Rating</th>
                      <th>Answers & Comments</th>
                      <th>Submission Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {feedbackList.map((fb, idx) => (
                      <tr key={fb._id || idx}>
                        <td>
                          <strong>{fb.student_username}</strong>
                        </td>
                        <td>
                          <div>{fb.course_name || 'N/A'}</div>
                          <small style={{ color: '#718096' }}>({fb.course_code})</small>
                        </td>
                        <td>{fb.faculty_name || 'N/A'}</td>
                        <td>
                          <span className="rating-badge">
                            ★ {fb.rating}
                          </span>
                        </td>
                        <td style={{ maxWidth: '400px' }}>
                          {fb.answers && fb.answers.length > 0 ? (
                            <ul style={{ listStyle: 'none', padding: 0 }}>
                              {fb.answers.map((ans, aidx) => (
                                <li key={aidx} style={{ marginBottom: '6px', fontSize: '0.88rem' }}>
                                  <strong style={{ color: '#4a5568' }}>{ans.question}: </strong>
                                  <span>{ans.answer}</span>
                                </li>
                              ))}
                            </ul>
                          ) : fb.comments ? (
                            <span>{fb.comments}</span>
                          ) : (
                            <em style={{ color: '#a0aec0' }}>No comments</em>
                          )}
                        </td>
                        <td style={{ whiteSpace: 'nowrap', fontSize: '0.88rem', color: '#718096' }}>
                          {fb.submitted_at
                            ? new Date(fb.submitted_at).toLocaleString('en-US', {
                                dateStyle: 'short',
                                timeStyle: 'short',
                              })
                            : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: FACULTY REPORTS */}
        {activeTab === 'reports' && (
          <div className="dashboard-card">
            <div className="card-header">
              <h2 className="card-title">
                <span>📈</span> Faculty Feedback Report Generator
              </h2>
            </div>
            <p style={{ color: '#718096', marginBottom: '20px' }}>
              Select a faculty member or course to generate a comprehensive analytical feedback report.
            </p>

            <div style={{ maxWidth: '420px', marginBottom: '24px' }}>
              <label style={{ display: 'block', fontWeight: 600, marginBottom: '8px' }}>
                Select Faculty Member:
              </label>
              <select
                className="form-control select-control"
                value={selectedFacultyForReport}
                onChange={(e) => handleGenerateReport(e.target.value)}
              >
                <option value="">-- Choose Faculty --</option>
                {facultyList.map((f) => (
                  <option key={f.username} value={f.username}>
                    {f.name} ({f.course_name} - {f.course_code})
                  </option>
                ))}
              </select>
            </div>

            {loadingReport ? (
              <p className="empty-state">Generating report from feedback records...</p>
            ) : facultyReport ? (
              <div>
                <div className="stats-grid" style={{ marginBottom: '24px' }}>
                  <StatCard
                    title="Faculty Name"
                    value={facultyReport.faculty?.name || selectedFacultyForReport}
                    icon="👨‍🏫"
                    borderColor="#4facfe"
                  />
                  <StatCard
                    title="Course"
                    value={facultyReport.course?.course_name || facultyReport.course_code || 'N/A'}
                    icon="📖"
                    borderColor="#6a5af9"
                  />
                  <StatCard
                    title="Total Evaluations"
                    value={facultyReport.total_responses}
                    icon="📝"
                    borderColor="#38a169"
                  />
                  <StatCard
                    title="Overall Rating"
                    value={
                      <span>
                        {facultyReport.average_rating} <small style={{ fontSize: '1rem', color: '#718096' }}>/ 5.0</small>
                      </span>
                    }
                    icon="⭐"
                    borderColor="#ecc94b"
                  />
                </div>

                <div style={{ marginBottom: '24px' }}>
                  <h3 style={{ fontSize: '1.1rem', marginBottom: '12px' }}>Rating Distribution</h3>
                  <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                    {[5, 4, 3, 2, 1].map((star) => (
                      <div
                        key={star}
                        style={{
                          background: '#f8fafc',
                          padding: '12px 18px',
                          borderRadius: '10px',
                          border: '1px solid #e2e8f0',
                          minWidth: '130px',
                        }}
                      >
                        <div style={{ fontSize: '0.9rem', color: '#4a5568' }}>{star} Stars:</div>
                        <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#2d3748' }}>
                          {facultyReport.rating_distribution?.[star] ?? 0}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {(facultyReport.formatted_report_text || facultyReport.soap_compatible_text) && (
                  <div>
                    <h3 style={{ fontSize: '1.1rem', marginBottom: '8px' }}>
                      Report Summary Format
                    </h3>
                    <pre
                      style={{
                        background: '#1a202c',
                        color: '#68d391',
                        padding: '18px',
                        borderRadius: '10px',
                        fontSize: '0.88rem',
                        fontFamily: 'Consolas, monospace',
                        whiteSpace: 'pre-wrap',
                      }}
                    >
                      {facultyReport.formatted_report_text || facultyReport.soap_compatible_text}
                    </pre>
                  </div>
                )}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">📊</div>
                <p>Choose a faculty member from the dropdown above to view the report.</p>
              </div>
            )}
          </div>
        )}

        {/* TAB 3: MANAGE QUESTIONS */}
        {activeTab === 'questions' && (
          <div className="dashboard-card">
            <div className="card-header">
              <h2 className="card-title">
                <span>❓</span> Manage Feedback Questions
              </h2>
            </div>

            {/* Add question form */}
            <form onSubmit={handleAddQuestion} style={{ marginBottom: '32px' }}>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '14px', color: '#2d3748' }}>
                Add New Question
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr auto', gap: '14px', alignItems: 'end' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: 600, marginBottom: '6px' }}>
                    Question Text *
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="e.g. How effective was the course material?"
                    value={newQuestion.question_text}
                    onChange={(e) => setNewQuestion({ ...newQuestion, question_text: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: 600, marginBottom: '6px' }}>
                    Question Type *
                  </label>
                  <select
                    className="form-control select-control"
                    value={newQuestion.question_type}
                    onChange={(e) => setNewQuestion({ ...newQuestion, question_type: e.target.value })}
                    required
                  >
                    <option value="rating">Rating (1 - 5 Stars)</option>
                    <option value="text">Text (Open comment)</option>
                  </select>
                </div>
                <div>
                  <button type="submit" className="btn-primary" style={{ padding: '13px 24px' }}>
                    ➕ Add Question
                  </button>
                </div>
              </div>
            </form>

            <h3 style={{ fontSize: '1.1rem', marginBottom: '14px', color: '#2d3748' }}>
              Existing Questions ({questions.length})
            </h3>
            {questions.map((q, idx) => (
              <div
                key={q._id || idx}
                style={{
                  padding: '16px 20px',
                  background: '#f8fafc',
                  border: '1px solid #e2e8f0',
                  borderRadius: '10px',
                  marginBottom: '12px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <div>
                  <strong style={{ fontSize: '1rem', color: '#1a202c' }}>
                    {idx + 1}. {q.question_text || q.question}
                  </strong>
                  <div style={{ marginTop: '4px' }}>
                    <span
                      style={{
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        textTransform: 'uppercase',
                        padding: '2px 8px',
                        borderRadius: '6px',
                        background: q.question_type === 'rating' ? '#feebc8' : '#e2e8f0',
                        color: q.question_type === 'rating' ? '#7b341e' : '#4a5568',
                      }}
                    >
                      Type: {q.question_type}
                    </span>
                  </div>
                </div>
                <button
                  className="btn-danger"
                  onClick={() => handleDeleteQuestion(q._id)}
                >
                  🗑️ Delete
                </button>
              </div>
            ))}
          </div>
        )}

        {/* TAB 4: MANAGE COURSES */}
        {activeTab === 'courses' && (
          <div className="dashboard-card">
            <div className="card-header">
              <h2 className="card-title">
                <span>📚</span> Manage Courses
              </h2>
            </div>

            {/* Add course form */}
            <form onSubmit={handleAddCourse} style={{ marginBottom: '32px' }}>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '14px', color: '#2d3748' }}>
                Add New Course
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr auto', gap: '14px', alignItems: 'end' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: 600, marginBottom: '6px' }}>
                    Course Name *
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="e.g. Advanced Web Technologies"
                    value={newCourse.course_name}
                    onChange={(e) => setNewCourse({ ...newCourse, course_name: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: 600, marginBottom: '6px' }}>
                    Course Code *
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="e.g. CS202"
                    value={newCourse.course_code}
                    onChange={(e) => setNewCourse({ ...newCourse, course_code: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <button type="submit" className="btn-primary" style={{ padding: '13px 24px' }}>
                    ➕ Add Course
                  </button>
                </div>
              </div>
            </form>

            <h3 style={{ fontSize: '1.1rem', marginBottom: '14px', color: '#2d3748' }}>
              Existing Courses ({courses.length})
            </h3>
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Course Code</th>
                    <th>Course Name</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {courses.map((c) => (
                    <tr key={c.course_code}>
                      <td>
                        <strong>{c.course_code}</strong>
                      </td>
                      <td>{c.course_name}</td>
                      <td>
                        <button
                          className="btn-danger"
                          onClick={() => handleDeleteCourse(c.course_code)}
                        >
                          🗑️ Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 5: MANAGE FACULTY */}
        {activeTab === 'faculty' && (
          <div className="dashboard-card">
            <div className="card-header">
              <h2 className="card-title">
                <span>👨‍🏫</span> Manage Faculty
              </h2>
            </div>

            {/* Add Faculty Form */}
            <form onSubmit={handleAddFaculty} style={{ marginBottom: '32px' }}>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '14px', color: '#2d3748' }}>
                Add New Faculty Member
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                    Username *
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="faculty8"
                    value={newFaculty.username}
                    onChange={(e) => setNewFaculty({ ...newFaculty, username: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                    Password *
                  </label>
                  <input
                    type="password"
                    className="form-control"
                    placeholder="••••••"
                    value={newFaculty.password}
                    onChange={(e) => setNewFaculty({ ...newFaculty, password: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                    Faculty Name *
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Dr. John Doe"
                    value={newFaculty.name}
                    onChange={(e) => setNewFaculty({ ...newFaculty, name: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                    Assigned Course Code
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="e.g. AWT103"
                    value={newFaculty.course_code}
                    onChange={(e) => setNewFaculty({ ...newFaculty, course_code: e.target.value })}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                    Course Name
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="e.g. AWT"
                    value={newFaculty.course_name}
                    onChange={(e) => setNewFaculty({ ...newFaculty, course_name: e.target.value })}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                    Email
                  </label>
                  <input
                    type="email"
                    className="form-control"
                    placeholder="faculty@college.edu"
                    value={newFaculty.faculty_email}
                    onChange={(e) => setNewFaculty({ ...newFaculty, faculty_email: e.target.value })}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                    Department
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Computer Applications"
                    value={newFaculty.department}
                    onChange={(e) => setNewFaculty({ ...newFaculty, department: e.target.value })}
                  />
                </div>
              </div>

              <button type="submit" className="btn-primary" style={{ marginTop: '16px' }}>
                ➕ Register Faculty Member
              </button>
            </form>

            <h3 style={{ fontSize: '1.1rem', marginBottom: '14px', color: '#2d3748' }}>
              Faculty Members ({facultyList.length})
            </h3>
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Name</th>
                    <th>Course</th>
                    <th>Course Code</th>
                    <th>Department</th>
                  </tr>
                </thead>
                <tbody>
                  {facultyList.map((f) => (
                    <tr key={f.username}>
                      <td>
                        <strong>{f.username}</strong>
                      </td>
                      <td>{f.name}</td>
                      <td>{f.course_name || 'N/A'}</td>
                      <td>
                        <code>{f.course_code || 'N/A'}</code>
                      </td>
                      <td>{f.department || 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 6: MANAGE STUDENTS */}
        {activeTab === 'students' && (
          <div className="dashboard-card">
            <div className="card-header">
              <h2 className="card-title">
                <span>👨‍🎓</span> Manage Students
              </h2>
            </div>

            {/* Add Student Form */}
            <form onSubmit={handleAddStudent} style={{ marginBottom: '32px' }}>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '14px', color: '#2d3748' }}>
                Add New Student
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                    Username *
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="e.g. student65"
                    value={newStudent.username}
                    onChange={(e) => setNewStudent({ ...newStudent, username: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                    Password *
                  </label>
                  <input
                    type="password"
                    className="form-control"
                    placeholder="••••••"
                    value={newStudent.password}
                    onChange={(e) => setNewStudent({ ...newStudent, password: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                    Student Name *
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Student Name"
                    value={newStudent.name}
                    onChange={(e) => setNewStudent({ ...newStudent, name: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                    Email
                  </label>
                  <input
                    type="email"
                    className="form-control"
                    placeholder="student@example.com"
                    value={newStudent.student_email}
                    onChange={(e) => setNewStudent({ ...newStudent, student_email: e.target.value })}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                    Roll Number
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="21MCA10"
                    value={newStudent.roll_number}
                    onChange={(e) => setNewStudent({ ...newStudent, roll_number: e.target.value })}
                  />
                </div>
              </div>

              <button type="submit" className="btn-primary" style={{ marginTop: '16px' }}>
                ➕ Register Student
              </button>
            </form>

            <h3 style={{ fontSize: '1.1rem', marginBottom: '14px', color: '#2d3748' }}>
              Student Directory ({studentsList.length})
            </h3>
            <div className="table-responsive" style={{ maxHeight: '420px', overflowY: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Name</th>
                    <th>Roll Number</th>
                    <th>Email</th>
                  </tr>
                </thead>
                <tbody>
                  {studentsList.map((s) => (
                    <tr key={s.username}>
                      <td>
                        <strong>{s.username}</strong>
                      </td>
                      <td>{s.name || s.student_name}</td>
                      <td>{s.roll_number || 'N/A'}</td>
                      <td>{s.student_email || s.email || 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

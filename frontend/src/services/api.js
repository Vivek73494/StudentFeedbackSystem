import axios from 'axios';

// Base API configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach bearer token if stored
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('sfs_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for consistent error extraction
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorMsg =
      error.response?.data?.error ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred';
    return Promise.reject(new Error(errorMsg));
  }
);

// ==========================================
// Authentication APIs
// ==========================================
export const authService = {
  login: async (username, password, role) => {
    const response = await api.post('/api/auth/login', { username, password, role });
    if (response.data.token) {
      localStorage.setItem('sfs_token', response.data.token);
      localStorage.setItem('sfs_user', JSON.stringify(response.data.user));
    }
    return response.data;
  },
  logout: async () => {
    try {
      await api.post('/api/auth/logout');
    } finally {
      localStorage.removeItem('sfs_token');
      localStorage.removeItem('sfs_user');
    }
  },
  getMe: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
  registerStudent: async (studentData) => {
    const response = await api.post('/api/auth/register', studentData);
    return response.data;
  },
  getStoredUser: () => {
    try {
      const u = localStorage.getItem('sfs_user');
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  },
};

// ==========================================
// Course APIs
// ==========================================
export const courseService = {
  getAll: async () => {
    const response = await api.get('/api/courses');
    return response.data;
  },
  add: async (courseData) => {
    const response = await api.post('/api/courses', courseData);
    return response.data;
  },
  delete: async (courseCode) => {
    const response = await api.delete(`/api/courses/${encodeURIComponent(courseCode)}`);
    return response.data;
  },
};

// ==========================================
// Question APIs
// ==========================================
export const questionService = {
  getAll: async () => {
    const response = await api.get('/api/feedback/questions');
    return response.data;
  },
  add: async (questionData) => {
    const response = await api.post('/api/feedback/questions', questionData);
    return response.data;
  },
  delete: async (questionId) => {
    const response = await api.delete(`/api/feedback/questions/${encodeURIComponent(questionId)}`);
    return response.data;
  },
};

// ==========================================
// Feedback APIs
// ==========================================
export const feedbackService = {
  submit: async (feedbackPayload) => {
    const response = await api.post('/api/feedback', feedbackPayload);
    return response.data;
  },
  getAll: async (params = {}) => {
    const response = await api.get('/api/feedback', { params });
    return response.data;
  },
  getStudentFeedback: async (studentUsername) => {
    const response = await api.get('/api/student/feedback', {
      params: studentUsername ? { student_username: studentUsername } : {},
    });
    return response.data;
  },
  getFacultyFeedback: async (facultyUsername) => {
    const response = await api.get('/api/faculty/feedback', {
      params: facultyUsername ? { faculty_username: facultyUsername } : {},
    });
    return response.data;
  },
};

// ==========================================
// Faculty Report APIs
// ==========================================
export const reportService = {
  getFacultyReport: async (facultyIdOrCode) => {
    const params = {};
    if (facultyIdOrCode) {
      if (facultyIdOrCode.startsWith('faculty') || !facultyIdOrCode.includes('10')) {
        params.faculty_id = facultyIdOrCode;
      } else {
        params.course_code = facultyIdOrCode;
      }
    }
    const response = await api.get('/api/reports/faculty', { params });
    return response.data;
  },
};

// ==========================================
// Admin APIs
// ==========================================
export const adminService = {
  getStats: async () => {
    const response = await api.get('/api/admin/stats');
    return response.data;
  },
  getFaculty: async () => {
    const response = await api.get('/api/faculty');
    return response.data;
  },
  addFaculty: async (facultyData) => {
    const response = await api.post('/api/faculty', facultyData);
    return response.data;
  },
  getStudents: async () => {
    const response = await api.get('/api/students');
    return response.data;
  },
  addStudent: async (studentData) => {
    const response = await api.post('/api/students', studentData);
    return response.data;
  },
};

export default api;

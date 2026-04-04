import axios from 'axios';

const rawApiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const apiRoot = rawApiUrl.replace(/\/+$|\/api$/g, '').replace(/\/api$/g, '')
export const API_BASE_URL = `${apiRoot}/api`

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth if needed later
api.interceptors.request.use(
  (config) => {
    // Add auth token here if implemented
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const resumeAPI = {
  // Upload and analyze resume
  uploadAndAnalyze: (file, jdText = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (jdText) {
      formData.append('jd_text', jdText);
    }
    return api.post('/upload-analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // Get analysis results
  getAnalysis: (resumeId) => api.get(`/analysis/${resumeId}`),

  // Re-analyze existing resume
  reanalyze: (resumeId) => api.post(`/reanalyze/${resumeId}`),

  // Compare with job description
  compareWithJob: (resumeId, jobData) => api.post(`/compare-job?resume_id=${resumeId}`, jobData),

  // Run benchmarks
  runBenchmarks: () => api.get('/benchmark'),
};

export const jobAPI = {
  compareJD: (resumeId, jobData) => api.post(`/compare-jd?resume_id=${resumeId}`, jobData),
  getRoleRecommendation: (request) => api.post('/role-recommendation', request),
  getAvailableRoles: () => api.get('/available-roles'),
  compareRoles: (request) => api.post('/compare-roles', request),
};

export const chatAPI = {
  chat: (request) => api.post('/chat', request),
  rewriteBullets: (request) => api.post('/rewrite-bullets', request),
};

export const mlAPI = {
  predict: (request) => api.post('/predict', request),
};

export default api;
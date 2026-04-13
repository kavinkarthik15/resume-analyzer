import axios from 'axios';

const rawApiUrl =
  import.meta.env.VITE_API_URL ||
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000'
    : 'https://resume-analyzer-nvqc.onrender.com');

const apiRoot = rawApiUrl
  .replace(/\/+$/, '')
  .replace(/\/api$/, '');

export const API_BASE_URL = apiRoot;

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
  uploadAndAnalyze: (file, payload = null) => {
    const isObjectPayload = payload && typeof payload === 'object' && !Array.isArray(payload)
    const jobDescription = isObjectPayload ? payload.job_description ?? payload.jobDescription ?? null : payload
    const roleData = isObjectPayload ? payload.role_data ?? payload.roleData ?? null : null

    const formData = new FormData();
    formData.append('file', file);
    if (jobDescription) {
      formData.append('job_description', jobDescription);
    }
    if (roleData) {
      formData.append('role_data', JSON.stringify(roleData));
    }
    return api.post('/analyze', formData, {
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

export const jdAPI = {
  generate: (roleData) => api.post('/generate-jd', roleData),
};

export const chatAPI = {
  chat: (request) => api.post('/chat', request),
  rewriteBullets: (request) => api.post('/rewrite-bullets', request),
};

export const mlAPI = {
  predict: (request) => api.post('/predict', request),
};

export const rewriteAPI = {
  rewriteResume: async (payload) => {
    const requestBody =
      payload && typeof payload === 'object' && !Array.isArray(payload)
        ? payload
        : { text: payload };

    try {
      return await api.post('/rewrite', requestBody);
    } catch (error) {
      if (error?.response?.status === 404) {
        return api.post('/api/rewrite', requestBody);
      }
      throw error;
    }
  },
};

export default api;
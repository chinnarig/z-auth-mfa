import axios from 'axios';
import Cookies from 'js-cookie';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = Cookies.get('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = Cookies.get('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token } = response.data;
          Cookies.set('access_token', access_token);

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        Cookies.remove('access_token');
        Cookies.remove('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data: {
    email: string;
    password: string;
    full_name: string;
    company_name: string;
    company_domain: string;
  }) => api.post('/api/auth/register', data),

  login: (email: string, password: string) =>
    api.post('/api/auth/login', { email, password }),

  verifyMFA: (email: string, code: string) =>
    api.post('/api/auth/verify-mfa', { email, code }),

  logout: (refreshToken: string) =>
    api.post('/api/auth/logout', { refresh_token: refreshToken }),

  setupMFA: () => api.post('/api/auth/mfa/setup'),

  enableMFA: (code: string) => api.post('/api/auth/mfa/enable', { code }),

  disableMFA: (password: string, code?: string) =>
    api.post('/api/auth/mfa/disable', { password, code }),

  getBackupCodes: () => api.get('/api/auth/mfa/backup-codes'),

  getCurrentUser: () => api.get('/api/auth/me'),
};

// Users API
export const usersAPI = {
  getProfile: () => api.get('/api/users/me'),
  updateProfile: (data: { full_name?: string; email?: string }) =>
    api.put('/api/users/me', data),
  listUsers: () => api.get('/api/users/'),
};

export default api;

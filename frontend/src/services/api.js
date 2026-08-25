// API service for HTTP requests
import axios from 'axios';

const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: `${apiUrl}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const alertAPI = {
  getAlerts: (params) => apiClient.get('/alerts', { params }),
  getAlert: (id) => apiClient.get(`/alerts/${id}`),
  markAsRead: (id) => apiClient.put(`/alerts/${id}/read`),
  deleteAlert: (id) => apiClient.delete(`/alerts/${id}`),
};

export const cameraAPI = {
  getCameras: () => apiClient.get('/cameras'),
  getCamera: (id) => apiClient.get(`/cameras/${id}`),
  createCamera: (data) => apiClient.post('/cameras', data),
  updateCamera: (id, data) => apiClient.put(`/cameras/${id}`, data),
  getZones: (cameraId) => apiClient.get(`/cameras/${cameraId}/zones`),
  createZone: (cameraId, data) => apiClient.post(`/cameras/${cameraId}/zones`, data),
};

export const analyticsAPI = {
  getDashboard: () => apiClient.get('/analytics/dashboard'),
  getCameraAnalytics: (cameraId, days) =>
    apiClient.get(`/analytics/camera/${cameraId}`, { params: { days } }),
  getTrends: (days) => apiClient.get('/analytics/trends', { params: { days } }),
};

export const adminAPI = {
  getSystemStatus: () => apiClient.get('/admin/system-status'),
  getConfig: () => apiClient.get('/admin/config'),
  updateConfig: (config) => apiClient.post('/admin/config/update', config),
};

export default apiClient;

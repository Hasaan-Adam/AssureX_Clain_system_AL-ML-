import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('assurex_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    const customError = {
      status: error.response ? error.response.status : null,
      message: 'An unexpected error occurred.',
      detail: null,
      raw: error,
    };

    if (error.response) {
      const data = error.response.data;
      if (typeof data === 'string') {
        customError.message = data;
      } else if (data && data.error) {
        if (typeof data.error === 'string') {
          customError.message = data.error;
        } else if (data.error.details && Array.isArray(data.error.details) && data.error.details.length > 0) {
          customError.message = data.error.details.map((d) => {
            const loc = Array.isArray(d.loc) ? d.loc.filter(l => l !== 'body').join('.') : '';
            return loc ? `${loc}: ${d.msg || d.message}` : (d.msg || d.message);
          }).join(', ');
          customError.detail = data.error.details;
        } else if (data.error.message) {
          customError.message = data.error.message;
        } else {
          customError.message = JSON.stringify(data.error);
        }
      } else if (data && data.detail) {
        if (typeof data.detail === 'string') {
          customError.message = data.detail;
          customError.detail = data.detail;
        } else if (Array.isArray(data.detail)) {
          customError.message = data.detail.map((d) => {
            const loc = Array.isArray(d.loc) ? d.loc.filter(l => l !== 'body').join('.') : '';
            return loc ? `${loc}: ${d.msg || d.message}` : (d.msg || d.message);
          }).join(', ');
          customError.detail = data.detail;
        } else {
          customError.message = JSON.stringify(data.detail);
        }
      } else if (data && data.message) {
        customError.message = data.message;
      }

      if (error.response.status === 401) {
        const currentPath = window.location.pathname;
        if (currentPath !== '/login' && currentPath !== '/register' && currentPath !== '/') {
          localStorage.removeItem('assurex_token');
          localStorage.removeItem('assurex_user');
          window.dispatchEvent(new Event('auth:unauthorized'));
        }
      }
    } else if (error.request) {
      customError.message = 'Network error. Backend server is unreachable.';
    } else {
      customError.message = error.message;
    }

    return Promise.reject(customError);
  }
);

export default apiClient;
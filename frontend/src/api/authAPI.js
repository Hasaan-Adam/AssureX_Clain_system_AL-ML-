import apiClient from './client';

export const authAPI = {
  login: async (credentials) => {
    return apiClient.post('/auth/login', credentials);
  },

  register: async (userData) => {
    return apiClient.post('/auth/register', userData);
  },

  getCurrentUser: async () => {
    return apiClient.get('/auth/me');
  },

  updateProfile: async (profileData) => {
    return apiClient.put('/users/me', profileData);
  },

  changePassword: async (passwordData) => {
    const payload = {
      old_password: passwordData.old_password || passwordData.current_password,
      new_password: passwordData.new_password,
    };
    return apiClient.post('/auth/change-password', payload);
  },

  getAllUsers: (params = {}) => apiClient.get('/users', { params }),
  updateUserRole: (id, role) => apiClient.put(`/users/${id}/role`, { role }),
  updateUserStatus: (id, is_active) => apiClient.put(`/users/${id}/status`, { is_active }),

  logout: async () => {
    try {
      await apiClient.post('/auth/logout');
    } catch (e) {
    } finally {
      localStorage.removeItem('assurex_token');
      localStorage.removeItem('assurex_user');
    }
  },
};

export default authAPI;
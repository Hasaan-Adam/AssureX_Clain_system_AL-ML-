import apiClient from './client';

export const dashboardAPI = {
  getUserDashboard: async () => {
    return apiClient.get('/dashboard/user');
  },
  getCustomerDashboard: async () => {
    return apiClient.get('/dashboard/user');
  },

  getAdminDashboard: async () => {
    return apiClient.get('/dashboard/admin');
  },

  getReviewerDashboard: async () => {
    return apiClient.get('/dashboard/reviewer');
  },

};

export default dashboardAPI;
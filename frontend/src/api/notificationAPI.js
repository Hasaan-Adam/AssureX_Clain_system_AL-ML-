import apiClient from './client';
const notificationAPI = {
  getNotifications: (params = {}) => apiClient.get('/notifications', { params }),
  markAsRead: (id) => apiClient.put(`/notifications/${id}/read`),
  markAllRead: () => apiClient.put('/notifications/read-all'),
};
export default notificationAPI;

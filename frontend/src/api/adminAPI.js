import apiClient from './client';
const adminAPI = {
  getSettings: () => apiClient.get('/admin/settings'),
  updateSetting: (key, value) => apiClient.put(`/admin/settings/${key}`, { value }),
  getAuditLogs: (params = {}) => apiClient.get('/admin/audit-logs', { params }),
  getAnomalies: (params = {}) => apiClient.get('/admin/anomalies', { params }),
  getPolicies: () => apiClient.get('/admin/policies'),
  updatePolicy: (filename, payload) => apiClient.put(`/admin/policies/${filename}`, payload),
};
export default adminAPI;

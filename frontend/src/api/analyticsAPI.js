import apiClient from './client';
const analyticsAPI = {
  getAnalyticsTrends: (params = {}) => apiClient.get('/analytics/trends', { params }),
  getOverview: (params = {}) => apiClient.get('/analytics/overview', { params }),
  getFaultAnalysis: (params = {}) => apiClient.get('/analytics/faults', { params }),
  getFraudStats: (params = {}) => apiClient.get('/analytics/fraud', { params }),
  getReliability: (params = {}) => apiClient.get('/analytics/reliability', { params }),
};
export default analyticsAPI;
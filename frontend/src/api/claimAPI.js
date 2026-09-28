import apiClient from './client';

export const claimAPI = {
  getClaims: async (params = {}) => {
    return apiClient.get('/claims', { params });
  },

  getClaimById: async (id) => {
    return apiClient.get(`/claims/${id}`);
  },

  getClaimByNumber: async (claimNumber) => {
    return apiClient.get(`/claims/by-number/${claimNumber}`);
  },

  createClaim: async (claimData) => {
    return apiClient.post('/claims', claimData);
  },

  updateClaim: async (id, claimData) => {
    return apiClient.put(`/claims/${id}`, claimData);
  },

  deleteClaim: async (id) => {
    return apiClient.delete(`/claims/${id}`);
  },

  getClaimStatusTimeline: async (id) => {
    return apiClient.get(`/claims/${id}/timeline`);
  },

  getClaimAuditLogs: async (id) => {
    return apiClient.get(`/claims/${id}/audit-logs`);
  },

  appealClaim: async (id, appealNotes) => {
    return apiClient.post(`/claims/${id}/appeal`, { appeal_notes: appealNotes });
  },
};

export default claimAPI;
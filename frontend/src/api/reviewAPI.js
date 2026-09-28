import apiClient from './client';

export const reviewAPI = {
  getReviewQueue: async (params = {}) => {
    return apiClient.get('/reviews/queue', { params });
  },

  getReviewDetail: async (claimId) => {
    return apiClient.get(`/reviews/${claimId}`);
  },

  submitReviewDecision: async (claimId, reviewData) => {
    return apiClient.post(`/reviews/${claimId}/decision`, {
      decision: reviewData.decision,
      reasoning: reviewData.reasoning || reviewData.justification || 'Reviewer decision recorded',
      notes: reviewData.notes || null,
    });
  },

  addReviewComment: async (claimId, commentData) => {
    return apiClient.post(`/reviews/${claimId}/comments`, commentData);
  },

  overrideDecision: async (claimId, overrideData) => {
    return apiClient.post(`/reviews/${claimId}/decision`, {
      decision: overrideData.decision,
      reasoning: overrideData.justification || overrideData.reasoning || 'Manual override of automated decision',
      notes: overrideData.notes || null,
    });
  },

  getOverrideStats: async () => {
    return apiClient.get('/reviews/stats/overrides');
  },
};

export default reviewAPI;
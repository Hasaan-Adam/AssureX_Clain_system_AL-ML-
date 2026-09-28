import apiClient from './client';

export const predictionAPI = {
  getPredictionsByClaim: async (claimId) => {
    return apiClient.get(`/predictions/claim/${claimId}`);
  },

  runAdjudication: async (claimId) => {
    return apiClient.post(`/predictions/adjudicate/${claimId}`);
  },

  getFeatureImportance: async (claimId) => {
    return apiClient.get(`/predictions/feature-importance/${claimId}`);
  },

  compareModels: async (claimId) => {
    return apiClient.get(`/predictions/compare/${claimId}`);
  },
};

export default predictionAPI;
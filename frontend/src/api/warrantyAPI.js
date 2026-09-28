import apiClient from './client';

export const warrantyAPI = {
  getWarranties: async (params = {}) => {
    return apiClient.get('/warranties', { params });
  },

  getWarrantyById: async (id) => {
    return apiClient.get(`/warranties/${id}`);
  },

  createWarranty: async (warrantyData) => {
    return apiClient.post('/warranties', warrantyData);
  },

  updateWarranty: async (id, warrantyData) => {
    return apiClient.put(`/warranties/${id}`, warrantyData);
  },

  deleteWarranty: async (id) => {
    return apiClient.delete(`/warranties/${id}`);
  },

  verifySerial: async (serialNumber, productId) => {
    return apiClient.post('/warranties/verify-serial', {
      serial_number: serialNumber,
      product_id: productId,
    });
  },

  getExpiringWarranties: async (days = 30) => {
    return apiClient.get('/warranties/expiring', { params: { days } });
  },
};

export default warrantyAPI;
import apiClient from './client';

export const documentAPI = {
  uploadDocument: async (formData) => {
    return apiClient.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  getDocumentsByClaim: async (claimId) => {
    return apiClient.get(`/documents/claim/${claimId}`);
  },

  getDocumentById: async (id) => {
    return apiClient.get(`/documents/${id}`);
  },

  deleteDocument: async (id) => {
    return apiClient.delete(`/documents/${id}`);
  },

  triggerOCR: async (documentId) => {
    return apiClient.post(`/documents/ocr/${documentId}`);
  },
  
  getDocument: async (documentId) => {
    return apiClient.get(`/documents/${documentId}`);
  },

  scanInvoice: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/documents/scan-invoice', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

export default documentAPI;
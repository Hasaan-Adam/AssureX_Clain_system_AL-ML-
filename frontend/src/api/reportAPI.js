import apiClient from './client';

const reportAPI = {
  exportClaimsCSV: (params = {}) => apiClient.get('/reports/export/claims/csv', { params, responseType: 'blob' }),
  exportClaimsExcel: (params = {}) => apiClient.get('/reports/export/claims/excel', { params, responseType: 'blob' }),
  exportReviewsCSV: (params = {}) => apiClient.get('/reports/export/reviews/csv', { params, responseType: 'blob' }),
  exportClaimPDF: (claimId) => apiClient.get(`/reports/claim/${claimId}/pdf`, { responseType: 'blob' }),
  downloadReportPdf: (claimId) => apiClient.get(`/reports/claim/${claimId}/pdf`, { responseType: 'blob' }),
};

export default reportAPI;
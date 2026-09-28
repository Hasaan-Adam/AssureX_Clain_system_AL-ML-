import apiClient from './client';

export const productAPI = {
  getProducts: async (params = {}) => {
    return apiClient.get('/products', { params });
  },

  getProductById: async (id) => {
    return apiClient.get(`/products/${id}`);
  },

  createProduct: async (productData) => {
    return apiClient.post('/products', productData);
  },

  updateProduct: async (id, productData) => {
    return apiClient.put(`/products/${id}`, productData);
  },

  deleteProduct: async (id) => {
    return apiClient.delete(`/products/${id}`);
  },

  getCategories: async () => {
    return apiClient.get('/products/categories');
  },
};

export default productAPI;
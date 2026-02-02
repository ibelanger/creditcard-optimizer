import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Currencies
export const getCurrencies = () => api.get('/currencies');
export const createCurrency = (data) => api.post('/currencies', data);
export const updateCurrency = (id, data) => api.put(`/currencies/${id}`, data);
export const deleteCurrency = (id) => api.delete(`/currencies/${id}`);

// Categories
export const getCategories = () => api.get('/categories');
export const createCategory = (data) => api.post('/categories', data);
export const updateCategory = (id, data) => api.put(`/categories/${id}`, data);
export const deleteCategory = (id) => api.delete(`/categories/${id}`);

// Cards
export const getCards = () => api.get('/cards');
export const getCard = (id) => api.get(`/cards/${id}`);
export const createCard = (data) => api.post('/cards', data);
export const updateCard = (id, data) => api.put(`/cards/${id}`, data);
export const deleteCard = (id) => api.delete(`/cards/${id}`);
export const getCardRewards = (id) => api.get(`/cards/${id}/rewards`);
export const addCardReward = (cardId, data) => api.post(`/cards/${cardId}/rewards`, data);
export const updateCardReward = (cardId, categoryId, data) =>
  api.put(`/cards/${cardId}/rewards/${categoryId}`, data);
export const deleteCardReward = (cardId, categoryId) =>
  api.delete(`/cards/${cardId}/rewards/${categoryId}`);

// Merchants
export const getMerchants = () => api.get('/merchants');
export const searchMerchants = (query) => api.get('/merchants/search', { params: { q: query } });
export const createMerchant = (data) => api.post('/merchants', data);
export const updateMerchant = (id, data) => api.put(`/merchants/${id}`, data);
export const deleteMerchant = (id) => api.delete(`/merchants/${id}`);

// Recommendations
export const getRecommendations = (params) => api.get('/recommend', { params });
export const getSimpleRecommendation = (categoryId) =>
  api.get('/recommend/simple', { params: { category_id: categoryId } });

export default api;

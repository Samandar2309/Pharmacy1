import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// API Services
export const authAPI = {
  register: (data) => api.post('/v2/users/register/', data),
  login: (data) => api.post('/v2/users/login/', data),
  verifyOTP: (data) => api.post('/v2/users/verify/', data),
  getProfile: () => api.get('/v2/users/me/'),
  updateProfile: (data) => api.patch('/v2/users/me/', data),
};

export const productsAPI = {
  getAll: (params) => api.get('/v1/products/products/', { params }),
  getById: (id) => api.get(`/v1/products/products/${id}/`),
  getCategories: () => api.get('/v1/products/categories/'),
  getAlternatives: (id) => api.get(`/v1/products/products/${id}/alternatives/`),
};

export const cartAPI = {
  get: () => api.get('/v3/orders/cart/'),
  add: (data) => api.post('/v3/orders/cart/add/', data),
  remove: (itemId) => api.delete(`/v3/orders/cart/${itemId}/`),
  update: (itemId, data) => api.patch(`/v3/orders/cart/${itemId}/`, data),
};

export const ordersAPI = {
  getAll: () => api.get('/v3/orders/'),
  getById: (id) => api.get(`/v3/orders/${id}/`),
  checkout: (data) => api.post('/v3/orders/checkout/', data),
  cancel: (id) => api.post(`/v3/orders/${id}/cancel/`),
};

export const paymentsAPI = {
  getAll: () => api.get('/v6/payments/'),
  getById: (paymentId) => api.get(`/v6/payments/${paymentId}/`),
  create: (data) => api.post('/v6/payments/create/', data),
};

export const prescriptionsAPI = {
  getAll: () => api.get('/v7/prescriptions/'),
  getById: (id) => api.get(`/v7/prescriptions/${id}/`),
  create: (formData) => api.post('/v7/prescriptions/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
};

export const dashboardAPI = {
  customer: () => api.get('/v8/dashboard/customer/'),
  admin: () => api.get('/v8/dashboard/admin/'),
  operator: () => api.get('/v8/dashboard/operator/'),
  courier: () => api.get('/v8/dashboard/courier/'),
};

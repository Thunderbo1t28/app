import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для добавления токена авторизации
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API для работы с авторизацией
export const authApi = {
  login: (data: { username: string; password: string }) =>
    api.post('/token/', data),
  register: (data: { username: string; email: string; password: string; password2: string }) =>
    api.post('/auth/register/', data),
  getUser: () => api.get('/auth/me/'),
  refreshToken: (refresh: string) => api.post('/token/refresh/', { refresh }),
};

// API для работы с инструментами
export const instrumentsApi = {
  getAll: () => api.get('/instruments/'),
  getById: (id: number) => api.get(`/instruments/${id}/`),
  create: (data: any) => api.post('/instruments/', data),
  update: (id: number, data: any) => api.patch(`/instruments/${id}/`, data),
  delete: (id: number) => api.delete(`/instruments/${id}/`),
};

// API для работы с ордерами
export const ordersApi = {
  getAll: () => api.get('/orders/'),
  instrumentOrders: () => api.get('/orders/instrument_orders/'),
  contractOrders: () => api.get('/orders/contract_orders/'),
  createOrder: (data: any) => api.post('/orders/', data),
  cancelOrder: (orderId: number, type: string) => 
    api.post(`/orders/${orderId}/cancel/`, { type }),
  spawnChildren: () => 
    api.post(`/orders/spawn_children/`, {}),
  generateManualFill: (orderId: number, fillData: {
    fill_price: number;
    fill_quantity: number;
    fill_datetime?: string;
  }) => api.post(`/orders/${orderId}/manual_fill/`, fillData),
};

// API для работы с задачами
export const tasksApi = {
  getLoadHistory: () => api.get('/tasks/load_history/'),
  getInstrumentsStatus: () => api.get('/tasks/instruments_status/'),
  runCommand: (command: string) => api.post('/tasks/run/', { command }),
};

// API для работы с системой
export const systemApi = {
  getStatus: () => api.get('/system/status/'),
  getConfigPrivate: () => api.get('/system/config_private/'),
  getConfigControl: () => api.get('/system/config_control/'),
  updateConfigPrivate: (content: string) => api.post('/system/config_private_update/', { content }),
  updateConfigControl: (content: string) => api.post('/system/config_control_update/', { content }),
  run: () => api.post('/system/run/', {}),
};

// API для работы с позициями контрактов
export const contractPositionsApi = {
  getAll: () => api.get('/contract-positions/'),
};

// API для работы с капиталом
export const arcticCapitalApi = {
  getAll: () => api.get('/arctic-capital/'),
  update: (id: number, data: any) => api.patch(`/arctic-capital/${id}/`, data),
  getOperationHistory: () => api.get('/arctic-capital/operation-history/'),
};

// API для работы с бэктестированием
export const backtestApi = {
  runBacktest: (params: any) => api.post('/backtest/run/', params),
  getResults: () => api.get('/backtest/results/'),
  getResult: (id: number) => api.get(`/backtest/results/${id}/`),
  deleteResult: (id: number) => api.delete(`/backtest/results/${id}/`),
};

// API для работы с оптимальными позициями
export const optimalPositionsApi = {
  getAll: () => api.get('/optimal-positions/')
};

export default api; 
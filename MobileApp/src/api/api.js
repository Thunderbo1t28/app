import { storage } from '../utils/storage';

const API_BASE_URL = 'http://10.0.2.2:8000/api'; // для Android эмулятора
// const API_BASE_URL = 'http://localhost:8000/api'; // для iOS симулятора

export const api = {
  async getHeaders() {
    const token = await storage.getItem('token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
  },

  async get(endpoint) {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers,
      });
      if (!response.ok) {
        throw new Error('Ошибка сети');
      }
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  async post(endpoint, data) {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers,
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Ошибка сервера');
      }
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  async put(endpoint, data) {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error('Ошибка сети');
      }
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  async delete(endpoint) {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'DELETE',
        headers,
      });
      if (!response.ok) {
        throw new Error('Ошибка сети');
      }
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },
}; 
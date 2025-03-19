import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api, { authApi } from '../services/api';

interface User {
  id: number;
  username: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  register: (username: string, email: string, password: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  const fetchUser = useCallback(async () => {
    try {
      const response = await authApi.getUser();
      setUser(response.data);
    } catch (error: any) {
      console.error('Error fetching user:', error);
      if (error.response?.status === 401) {
        // Пробуем обновить токен
        const refresh = localStorage.getItem('refresh_token');
        if (refresh) {
          try {
            const { data } = await authApi.refreshToken(refresh);
            localStorage.setItem('token', data.access);
            api.defaults.headers.common['Authorization'] = `Bearer ${data.access}`;
            // Повторяем запрос пользователя
            const userResponse = await authApi.getUser();
            setUser(userResponse.data);
            return;
          } catch (refreshError) {
            console.error('Error refreshing token:', refreshError);
          }
        }
      }
      logout();
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUser();
    }
  }, [fetchUser]);

  const login = async (username: string, password: string) => {
    try {
      const response = await authApi.login({ username, password });
      const { access, refresh } = response.data;  // JWT возвращает access и refresh токены
      localStorage.setItem('token', access);
      localStorage.setItem('refresh_token', refresh);
      api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      await fetchUser();
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Ошибка входа в систему';
      throw new Error(message);
    }
  };

  const register = async (username: string, email: string, password: string) => {
    try {
      console.log('Отправка данных регистрации:', { username, email, password });
      const response = await authApi.register({ 
        username, 
        email, 
        password,
        password2: password
      });
      console.log('Ответ сервера:', response.data);
      
      // После успешной регистрации выполняем вход
      await login(username, password);
    } catch (error: any) {
      console.error('Ошибка регистрации:', error.response?.data || error.message);
      const message = error.response?.data?.message || 
        error.response?.data?.error ||
        'Ошибка регистрации. Возможно, пользователь с таким именем или email уже существует.';
      throw new Error(message);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        login,
        logout,
        register,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 
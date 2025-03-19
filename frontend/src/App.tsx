import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

import { theme } from './theme';
import { AuthProvider } from './contexts/AuthContext';
import { SnackbarProvider } from './contexts/SnackbarContext';
import ProtectedRoute from './components/ProtectedRoute';
import MainLayout from './layouts/MainLayout';
import Login from './pages/Login';
import Register from './pages/Register';
import Instruments from './pages/Instruments';
import LoadData from './pages/LoadData';
import SystemControl from './pages/SystemControl';
import OrderStack from './pages/OrderStack';
import Dashboard from './pages/Dashboard';

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <SnackbarProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/" element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
                <Route index element={<Navigate to="/instruments" replace />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="instruments" element={<Instruments />} />
                <Route path="load-data" element={<LoadData />} />
                <Route path="system" element={<SystemControl />} />
                <Route path="orders" element={<OrderStack />} />
              </Route>
            </Routes>
          </BrowserRouter>
        </SnackbarProvider>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;

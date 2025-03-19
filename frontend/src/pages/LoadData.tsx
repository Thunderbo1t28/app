import React, { useState, useEffect, useCallback } from 'react';
import {
    Box,
    Typography,
    Button,
    CircularProgress,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Alert,
    Paper,
} from '@mui/material';
import { CloudUpload as CloudUploadIcon } from '@mui/icons-material';
import api, { tasksApi } from '../services/api';
import { useSnackbar } from '../contexts/SnackbarContext';

interface Instrument {
  id: number;
  instrument: string;
  description: string;
  last_download_date: string | null;
  last_contract: string | null;
}

interface LoadHistoryItem {
  id: string;
  status: 'running' | 'success' | 'error';
  message: string;
  details?: string;
  created_at: string;
  completed_at?: string;
}

const LoadData: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [instruments, setInstruments] = useState<Instrument[]>([]);
  const [loadHistory, setLoadHistory] = useState<LoadHistoryItem[]>([]);
  const { showMessage } = useSnackbar();

  const fetchInstrumentsStatus = useCallback(async () => {
    try {
      const response = await api.get('/tasks/instruments_status/');
      setInstruments(response.data.instruments || []);
    } catch (error) {
      showMessage('Ошибка при загрузке статуса инструментов', 'error');
    }
  }, [showMessage]);

  const fetchLoadHistory = useCallback(async () => {
    try {
      const response = await api.get('/tasks/load_history/');
      const data = response.data;
      let historyArray = [];
      if (Array.isArray(data)) {
        historyArray = data;
      } else if (data && Array.isArray(data.history)) {
        historyArray = data.history;
      }
      setLoadHistory(historyArray);
    } catch (error) {
      showMessage('Ошибка при загрузке истории', 'error');
    }
  }, [showMessage]);

  useEffect(() => {
    fetchInstrumentsStatus();
    fetchLoadHistory();
  }, [fetchInstrumentsStatus, fetchLoadHistory]);

  const handleLoadData = async () => {
    try {
      setLoading(true);
      await api.post('/tasks/run/', { command: 'load_to_database' });
      showMessage('Загрузка данных запущена', 'success');
    } catch (error) {
      showMessage('Ошибка при запуске загрузки данных', 'error');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Нет данных';
    return new Date(dateString).toLocaleString();
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Загрузка данных
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Button
          variant="contained"
          startIcon={loading ? <CircularProgress size={20} /> : <CloudUploadIcon />}
          onClick={handleLoadData}
          disabled={loading}
          fullWidth
          sx={{ mb: 3 }}
        >
          {loading ? 'Загрузка...' : 'Загрузить данные'}
        </Button>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Инструмент</TableCell>
                <TableCell>Последний контракт</TableCell>
                <TableCell>Последняя загрузка</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {instruments.map((instrument) => (
                <TableRow key={instrument.id}>
                  <TableCell>{instrument.instrument}</TableCell>
                  <TableCell>{instrument.last_contract || 'Нет данных'}</TableCell>
                  <TableCell>{formatDate(instrument.last_download_date)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2, mb: 3 }}>
        <Button variant="outlined" onClick={fetchInstrumentsStatus}>
          Обновить статус инструментов
        </Button>
        <Button variant="outlined" onClick={fetchLoadHistory}>
          Обновить историю загрузок
        </Button>
      </Box>

      <Typography variant="h6" gutterBottom>
        История загрузок
      </Typography>

      {(Array.isArray(loadHistory) ? loadHistory : []).map((item) => (
        <Alert
          key={item.id}
          severity={item.status === 'success' ? 'success' : item.status === 'error' ? 'error' : 'info'}
          sx={{ mb: 2 }}
        >
          <Typography variant="subtitle2">
            {new Date(item.created_at).toLocaleString()}
          </Typography>
          <Typography>{item.message}</Typography>
          {item.details && (
            <Typography variant="body2" color="textSecondary">
              {item.details}
            </Typography>
          )}
        </Alert>
      ))}
    </Box>
  );
};

export default LoadData; 
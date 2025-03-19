import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import InstrumentTable from '../components/InstrumentTable';
import AddInstrumentDialog from '../components/AddInstrumentDialog';
import EditInstrumentDialog from '../components/EditInstrumentDialog';
import { instrumentsApi } from '../services/api';
import { useSnackbar } from '../contexts/SnackbarContext';

interface Instrument {
  id: number;
  instrument: string;
  description: string;
  point_size: number;
  currency: string;
  asset_class: string;
  slippage: number;
  per_block?: number;
  percentage?: number;
  per_trade?: number;
}

const Instruments: React.FC = () => {
  const [instruments, setInstruments] = useState<Instrument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedInstrument, setSelectedInstrument] = useState<Instrument | null>(null);
  
  const { showMessage } = useSnackbar();

  const fetchInstruments = async () => {
    try {
      setLoading(true);
      const response = await instrumentsApi.getAll();
      setInstruments(response.data);
      setError(null);
    } catch (err) {
      setError('Ошибка при загрузке инструментов');
      showMessage('Ошибка при загрузке инструментов', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInstruments();
  }, []);

  const handleAdd = async (instrument: Instrument) => {
    try {
      await instrumentsApi.create(instrument);
      showMessage('Инструмент успешно добавлен', 'success');
      fetchInstruments();
    } catch (err) {
      showMessage('Ошибка при добавлении инструмента', 'error');
    }
  };

  const handleEdit = (instrument: Instrument) => {
    setSelectedInstrument(instrument);
    setEditDialogOpen(true);
  };

  const handleSave = async (updatedInstrument: Instrument) => {
    try {
      await instrumentsApi.update(updatedInstrument.id, updatedInstrument);
      showMessage('Инструмент успешно обновлен', 'success');
      setEditDialogOpen(false);
      setSelectedInstrument(null);
      fetchInstruments();
    } catch (err) {
      showMessage('Ошибка при обновлении инструмента', 'error');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await instrumentsApi.delete(id);
      showMessage('Инструмент успешно удален', 'success');
      fetchInstruments();
    } catch (err) {
      showMessage('Ошибка при удалении инструмента', 'error');
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Инструменты</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setAddDialogOpen(true)}
        >
          Добавить инструмент
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <InstrumentTable
        instruments={instruments}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />

      <AddInstrumentDialog
        open={addDialogOpen}
        onClose={() => setAddDialogOpen(false)}
        onAdd={handleAdd}
      />

      {selectedInstrument && (
        <EditInstrumentDialog
          open={editDialogOpen}
          onClose={() => {
            setEditDialogOpen(false);
            setSelectedInstrument(null);
          }}
          onSave={handleSave}
          selectedInstrument={selectedInstrument}
        />
      )}
    </Box>
  );
};

export default Instruments; 
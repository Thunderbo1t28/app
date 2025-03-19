import React, { useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  CircularProgress,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  InputAdornment,
} from '@mui/material';
import { Search as SearchIcon, Add as AddIcon } from '@mui/icons-material';
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
}

interface AddInstrumentDialogProps {
  open: boolean;
  onClose: () => void;
  onAdd: (instrument: Instrument) => void;
}

const AddInstrumentDialog: React.FC<AddInstrumentDialogProps> = ({
  open,
  onClose,
  onAdd,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [instruments, setInstruments] = useState<Instrument[]>([]);
  const [filteredInstruments, setFilteredInstruments] = useState<Instrument[]>([]);
  const { showMessage } = useSnackbar();

  const fetchInstruments = useCallback(async () => {
    try {
      setLoading(true);
      const response = await instrumentsApi.getAll();
      setInstruments(response.data);
    } catch (error) {
      showMessage('Ошибка при загрузке инструментов', 'error');
    } finally {
      setLoading(false);
    }
  }, [showMessage]);

  const filterInstruments = useCallback(() => {
    const filtered = instruments.filter(
      (instrument) =>
        instrument.instrument.toLowerCase().includes(searchQuery.toLowerCase()) ||
        instrument.description.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setFilteredInstruments(filtered);
  }, [instruments, searchQuery]);

  useEffect(() => {
    if (open) {
      fetchInstruments();
    }
  }, [open, fetchInstruments]);

  useEffect(() => {
    filterInstruments();
  }, [filterInstruments]);

  const handleAdd = (instrument: Instrument) => {
    onAdd(instrument);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Добавить инструмент</DialogTitle>
      <DialogContent>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Поиск инструмента"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12}>
            {loading ? (
              <CircularProgress />
            ) : filteredInstruments.length > 0 ? (
              <List>
                {filteredInstruments.map((instrument) => (
                  <ListItem key={instrument.id} divider>
                    <ListItemText
                      primary={instrument.instrument}
                      secondary={`${instrument.description} | ${instrument.asset_class} | ${instrument.currency}`}
                    />
                    <ListItemSecondaryAction>
                      <IconButton
                        edge="end"
                        onClick={() => handleAdd(instrument)}
                        color="primary"
                      >
                        <AddIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography color="textSecondary" align="center">
                {searchQuery
                  ? 'Инструменты не найдены'
                  : 'Введите текст для поиска инструментов'}
              </Typography>
            )}
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Отмена</Button>
      </DialogActions>
    </Dialog>
  );
};

export default AddInstrumentDialog; 
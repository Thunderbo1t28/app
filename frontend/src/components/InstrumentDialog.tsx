import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  MenuItem,
  Grid,
} from '@mui/material';

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

interface InstrumentDialogProps {
  open: boolean;
  onClose: () => void;
  onSave: (instrument: Partial<Instrument>) => void;
  selectedInstrument?: Instrument;
}

const ASSET_CLASSES = [
  'stock',
  'bond',
  'future',
  'option',
  'forex',
  'crypto',
];

const CURRENCIES = [
  'USD',
  'EUR',
  'RUB',
  'GBP',
  'JPY',
  'CNY',
];

const InstrumentDialog: React.FC<InstrumentDialogProps> = ({
  open,
  onClose,
  onSave,
  selectedInstrument,
}) => {
  const [formData, setFormData] = useState<Partial<Instrument>>({
    instrument: '',
    description: '',
    point_size: 0,
    currency: 'USD',
    asset_class: 'stock',
    slippage: 0,
    per_block: 0,
    percentage: 0,
    per_trade: 0,
  });

  useEffect(() => {
    if (selectedInstrument) {
      setFormData(selectedInstrument);
    }
  }, [selectedInstrument]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'instrument' || name === 'description' ? value : Number(value),
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>
          {selectedInstrument ? 'Редактировать инструмент' : 'Добавить инструмент'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Символ"
                name="instrument"
                value={formData.instrument}
                onChange={handleChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Описание"
                name="description"
                value={formData.description}
                onChange={handleChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Размер пункта"
                name="point_size"
                type="number"
                value={formData.point_size}
                onChange={handleChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Валюта"
                name="currency"
                value={formData.currency}
                onChange={handleChange}
                required
              >
                {CURRENCIES.map((currency) => (
                  <MenuItem key={currency} value={currency}>
                    {currency}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Класс актива"
                name="asset_class"
                value={formData.asset_class}
                onChange={handleChange}
                required
              >
                {ASSET_CLASSES.map((assetClass) => (
                  <MenuItem key={assetClass} value={assetClass}>
                    {assetClass}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Проскальзывание"
                name="slippage"
                type="number"
                value={formData.slippage}
                onChange={handleChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="За блок"
                name="per_block"
                type="number"
                value={formData.per_block}
                onChange={handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Процент"
                name="percentage"
                type="number"
                value={formData.percentage}
                onChange={handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="За сделку"
                name="per_trade"
                type="number"
                value={formData.per_trade}
                onChange={handleChange}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Отмена</Button>
          <Button type="submit" variant="contained">
            Сохранить
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default InstrumentDialog; 
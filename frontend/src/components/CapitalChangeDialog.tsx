import React, { useState } from 'react';
import { 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  TextField, 
  Button, 
  FormControl, 
  FormLabel, 
  RadioGroup, 
  FormControlLabel, 
  Radio, 
  Checkbox 
} from '@mui/material';

interface CapitalChangeDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (amount: string, type: string, strategies: string[]) => void;
  strategies: string[];
}

const CapitalChangeDialog: React.FC<CapitalChangeDialogProps> = ({ open, onClose, onSubmit, strategies }) => {
  const [amount, setAmount] = useState('');
  const [type, setType] = useState('deposit');
  const [selectedStrategies, setSelectedStrategies] = useState<string[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(amount, type, selectedStrategies);
    onClose();
  };

  const handleStrategyChange = (strategy: string) => {
    const index = selectedStrategies.indexOf(strategy);
    if (index === -1) {
      setSelectedStrategies([...selectedStrategies, strategy]);
    } else {
      setSelectedStrategies(selectedStrategies.filter((s) => s !== strategy));
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Изменение капитала</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          <TextField
            label="Сумма"
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            fullWidth
            margin="normal"
          />
          <FormControl component="fieldset" margin="normal">
            <FormLabel component="legend">Тип операции</FormLabel>
            <RadioGroup
              row
              value={type}
              onChange={(e) => setType(e.target.value)}
            >
              <FormControlLabel value="deposit" control={<Radio />} label="Пополнение" />
              <FormControlLabel value="withdraw" control={<Radio />} label="Вывод" />
            </RadioGroup>
          </FormControl>
          <FormControl component="fieldset" margin="normal">
            <FormLabel component="legend">Стратегии</FormLabel>
            {strategies.map((strategy) => (
              <FormControlLabel
                key={strategy}
                control={
                  <Checkbox
                    checked={selectedStrategies.includes(strategy)}
                    onChange={() => handleStrategyChange(strategy)}
                  />
                }
                label={strategy}
              />
            ))}
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Отмена</Button>
          <Button type="submit" variant="contained" color="primary">
            Сохранить
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default CapitalChangeDialog;
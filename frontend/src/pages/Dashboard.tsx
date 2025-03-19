import React, { useEffect, useState } from 'react';
import { arcticCapitalApi } from '../services/api';
import { TextField, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
import { Line } from 'react-chartjs-2';
import { Chart, registerables } from 'chart.js';
import { reverse } from 'dns';
import CapitalChangeDialog from '../components/CapitalChangeDialog';




Chart.register(...registerables);

interface ArcticCapitalRecord {
  id: number;
  ident: string;
  data: {
    index: string;
    '0': number;
  }[];
}

interface GlobalCapitalRecord {
  id: number;
  ident: string;
  data: {
    index: string;
    Actual: number;
    Accumulated: number;
    Broker: number;
    Max: number;
  }[];
}

const Dashboard: React.FC = () => {
  const [records, setRecords] = useState<(ArcticCapitalRecord | GlobalCapitalRecord)[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [amount, setAmount] = useState('');
  const [type, setType] = useState('deposit');
  const [strategy, setStrategy] = useState('');

  const [historicalAmount, setHistoricalAmount] = useState('');
  const [historicalType, setHistoricalType] = useState('deposit');
  const [historicalStrategy, setHistoricalStrategy] = useState('');
  const [historicalDate, setHistoricalDate] = useState('');

  const [typeError, setTypeError] = useState('');
  const [strategyError, setStrategyError] = useState('');
  const [operationHistory, setOperationHistory] = useState<any[]>([]);

  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const handleDialogOpen = () => {
    setIsDialogOpen(true);
  };
  
  const handleDialogClose = () => {
    setIsDialogOpen(false);
  };
  
  useEffect(() => {
    fetchRecords();
    fetchOperationHistory();
  }, []);

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const response = await arcticCapitalApi.getAll();
      setRecords(response.data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Произошла неизвестная ошибка');
      }
    }
    setLoading(false);
  };

  const fetchOperationHistory = async () => {
    try {
      const response = await arcticCapitalApi.getAll();
      setOperationHistory(response.data);
    } catch (err) {
      console.error('Failed to fetch operation history:', err);
    }
  };
  
  const handleCapitalChange = async (amount: string, type: string, strategy: string[]) => {
    strategy.forEach(async (ident) => {
      const record = records.find((r) => r.ident === ident);
  
      if (!record) {
        console.error(`Запись для стратегии ${ident} не найдена`);
        return;
      }
  
      if (!record.data || record.data.length === 0 || !('0' in record.data[0])) {
        console.error(`Неверный формат данных для записи ${record.id}`);
        return;
      }
  
      const arcticData = record.data[record.data.length - 1] as { index: string; '0': number };
      const newAmount = type === 'deposit'
        ? arcticData['0'] + Number(amount)
        : arcticData['0'] - Number(amount);
      
      const currentDate = new Date().toISOString().slice(0, 19).replace('T', ' ');
      const newRecord = {
        ...record,
        data: [
          ...record.data,
          {
            index: currentDate,
            '0': newAmount,
          },
        ],
      };
  
      try {
        await arcticCapitalApi.update(record.id, newRecord);
      } catch (error) {
        console.error(`Ошибка при обновлении записи ${record.id}:`, error);
      }
    });
  
    fetchRecords();
  };

  const globalCapitalRecord = records.find((r) => r.ident === '_global_capital') as GlobalCapitalRecord;
  console.log('Global Capital Record:', globalCapitalRecord);

  const capitalRecords = records.filter((r) => r.ident !== '_global_capital') as ArcticCapitalRecord[];

  const chartData = {
    labels: capitalRecords.map((record) => record.data[0].index),
    datasets: capitalRecords.map((record) => ({
      label: record.ident,
      data: record.data.map((d) => d['0']),
      fill: false,
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.1,
    })),
  };

  const handleTypeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedType = event.target.value;
    if (selectedType === 'deposit' || selectedType === 'withdraw') {
      setType(selectedType);
      setTypeError('');
    } else {
      setTypeError('Invalid operation type');
    }
  };

  const handleStrategyChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedStrategy = event.target.value;
    if (capitalRecords.some((record) => record.ident === selectedStrategy)) {
      setStrategy(selectedStrategy);
      setStrategyError('');
    } else {
      setStrategyError('Invalid strategy');
    }
  };

  return (
    <div>
      <h2>Арктический капитал</h2>
      {loading && <div>Загрузка...</div>}
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Стратегия</TableCell>
              <TableCell align="right">Текущий капитал</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {capitalRecords.map((record) => (
              <TableRow key={record.id}>
                <TableCell component="th" scope="row">
                  {record.ident}
                </TableCell>
                <TableCell align="right">{record.data[record.data.length - 1]['0']}</TableCell>
              </TableRow>
            ))}
            
          </TableBody>
        </Table>
      </TableContainer>
      <h3></h3>
      <Button variant="contained" color="primary" onClick={handleDialogOpen}>
        Изменить капитал
      </Button>
      <CapitalChangeDialog
        open={isDialogOpen}
        onClose={handleDialogClose}
        onSubmit={handleCapitalChange}
        strategies={capitalRecords.map((record) => record.ident)}
      />

      {/* История операций */}
      <h3>История операций</h3>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Дата</TableCell>
              <TableCell>Капитал</TableCell>
              <TableCell>Стратегия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {capitalRecords.map((record) => (
              record.data
                .slice()
                .sort((a: any, b: any) => new Date(b.index).getTime() - new Date(a.index).getTime())
                .map((dataItem: any, index: number) => (
                  <TableRow key={`${record.id}-${index}`}>
                    <TableCell>{new Date(dataItem.index).toLocaleString()}</TableCell>
                    <TableCell>{dataItem['0']}</TableCell>
                    <TableCell>{record.ident}</TableCell>
                  </TableRow>
                ))
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      
      <h3>График изменений капитала</h3>
      <div style={{ height: '400px' }}>
        <Line data={chartData} />
      </div>
    </div>
  );
};

export default Dashboard; 
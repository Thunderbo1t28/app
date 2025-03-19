import React, { useState, useEffect } from 'react';
import { ordersApi, optimalPositionsApi } from '../services/api';
import { Tabs, Tab, Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField } from '@mui/material';

interface Order {
  order_id: number;
  order_type: string;
  active: string;
  instrument: string;
  trade: number[];
  fill: number[];
  filled_price: number | null;
  reference_price: number | null;
  generated_datetime: string | null;
}



const OrderStack: React.FC = () => {
  const [instrumentOrders, setInstrumentOrders] = useState<Order[]>([]);
  const [contractOrders, setContractOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [optimalPositions, setOptimalPositions] = useState<any[]>([]);
  const [optimalLoading, setOptimalLoading] = useState<boolean>(false);
  const [optimalError, setOptimalError] = useState<string>('');
  const [activeTab, setActiveTab] = useState(0);
  const [manualFillOrderId, setManualFillOrderId] = useState<number | null>(null);
  const [manualFillPrice, setManualFillPrice] = useState<string>('');
  const [manualFillQuantity, setManualFillQuantity] = useState<string>('');
  const [manualFillOpen, setManualFillOpen] = useState(false);

  // Функция для рендеринга ячейки, если значение является объектом или массивом
  const renderCell = (value: any) => {
    if (Array.isArray(value)) {
      return value.join(', ');
    } else if (typeof value === 'object' && value !== null) {
      return JSON.stringify(value);
    }
    return value !== null ? String(value) : '-';
  };

  // Функция для получения списка ордеров через GET запрос
  const fetchOrders = async () => {
    try {
      setLoading(true);
      setError('');
      const [instrumentResponse, contractResponse] = await Promise.all([
        ordersApi.instrumentOrders(),
        ordersApi.contractOrders(),
      ]);
      setInstrumentOrders(instrumentResponse.data);
      setContractOrders(contractResponse.data);
    } catch (err) {
      setError('Ошибка загрузки ордеров');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Функция для получения оптимальных позиций
  const fetchOptimalPositions = async () => {
    try {
      setOptimalLoading(true);
      setOptimalError('');
      const response = await optimalPositionsApi.getAll();
      let data = response.data;
      // Если сервер вернул массив с одной записью и в этом объекте есть поле data как массив,
      // используем этот внутренний массив для отображения оптимальных позиций
      if (Array.isArray(data) && data.length === 1 && data[0].data && Array.isArray(data[0].data)) {
        data = data[0].data;
      }
      // Если данные содержат поле date, оставляем только запись с самой поздней датой
      if (Array.isArray(data) && data.length > 0 && data[0].date) {
        const latestRecord = data.reduce((latest, record) => {
          return new Date(record.date) > new Date(latest.date) ? record : latest;
        }, data[0]);
        data = [latestRecord];
      }
      setOptimalPositions(data);
    } catch (err) {
      setOptimalError('Ошибка загрузки оптимальных позиций');
      console.error(err);
    } finally {
      setOptimalLoading(false);
    }
  };

  // Функция для обновления данных
  const refreshData = async () => {
    await Promise.all([fetchOrders(), fetchOptimalPositions()]);
  };

  useEffect(() => {
    refreshData();
  }, []);

  const handleTabChange = (event: React.ChangeEvent<{}>, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleManualFillClick = (orderId: number) => {
    setManualFillOrderId(orderId);
    setManualFillOpen(true);
  };

  const handleManualFillClose = () => {
    setManualFillOpen(false);
  };

  const handleManualFillSubmit = () => {
    if (manualFillOrderId !== null) {
      ordersApi.generateManualFill(manualFillOrderId, {
        fill_price: parseFloat(manualFillPrice),
        fill_quantity: parseFloat(manualFillQuantity),
        fill_datetime: new Date().toISOString(),
      })
        .then(() => {
          setManualFillOpen(false);
          fetchOrders();
        })
        .catch((err) => {
          console.error('Ошибка при ручном исполнении ордера:', err);
        });
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Order Stack</h1>
      {loading && <p>Загрузка...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      <Tabs value={activeTab} onChange={handleTabChange}>
        <Tab label="Инструментальные ордера" />
        <Tab label="Контрактные ордера" />
        <Tab label="Оптимальные позиции" />
      </Tabs>

      {activeTab === 0 && (
        <section>
          <h2>Инструментальные ордера</h2>
          <button 
            onClick={() => {
              ordersApi.spawnChildren()
                .then(() => {
                  fetchOrders();
                })
                .catch((err) => {
                  console.error('Ошибка при порождении дочерних ордеров:', err);
                });
            }}
          >
            Spawn Children
          </button>
          {instrumentOrders.length === 0 ? (
            <p>Нет ордеров</p>
          ) : (
            <table border={1} cellPadding={5} cellSpacing={0} style={{ width: '100%', marginBottom: '20px' }}>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Тип</th>
                  <th>Статус</th>
                  <th>Инструмент</th>
                  <th>Количество</th>
                  <th>Заполнено</th>
                  <th>Цена</th>
                  <th>Дата создания</th>
                  <th>Ссылочная цена</th>
                </tr>
              </thead>
              <tbody>
                {instrumentOrders.map((order) => (
                  <tr key={order.order_id}>
                    <td>{order.order_id}</td>
                    <td>{order.order_type}</td>
                    <td>{order.active}</td>
                    <td>{order.instrument}</td>
                    <td>{order.trade}</td>
                    <td>{order.fill}</td>
                    <td>{order.filled_price !== null ? order.filled_price : '-'}</td>
                    <td>{order.generated_datetime || '-'}</td>
                    <td>{order.reference_price !== null ? order.reference_price : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}

      {activeTab === 1 && (
        <section>
          <h2>Контрактные ордера</h2>
          {contractOrders.length === 0 ? (
            <p>Нет ордеров</p>
          ) : (
            <table border={1} cellPadding={5} cellSpacing={0} style={{ width: '100%', marginBottom: '20px' }}>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Тип</th>
                  <th>Статус</th>
                  <th>Инструмент</th>
                  <th>Количество</th>
                  <th>Заполнено</th>
                  <th>Цена</th>
                  <th>Дата создания</th>
                  <th>Ссылочная цена</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {contractOrders.map((order) => (
                  <tr key={order.order_id}>
                    <td>{order.order_id}</td>
                    <td>{order.order_type}</td>
                    <td>{order.active}</td>
                    <td>{order.instrument}</td>
                    <td>{order.trade}</td>
                    <td>{order.fill}</td>
                    <td>{order.filled_price !== null ? order.filled_price : '-'}</td>
                    <td>{order.generated_datetime || '-'}</td>
                    <td>{order.reference_price !== null ? order.reference_price : '-'}</td>
                    <td>
                      <Button 
                        variant="contained"
                        color="primary"
                        size="small"
                        onClick={() => handleManualFillClick(order.order_id)}
                      >
                        Manual Fill
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}

      {activeTab === 2 && (
        <section>
          <h2>Оптимальные позиции</h2>
          {optimalLoading && <p>Загрузка оптимальных позиций...</p>}
          {optimalError && <p style={{ color: 'red' }}>{optimalError}</p>}
          {optimalPositions.length === 0 ? (
            <p>Нет оптимальных позиций</p>
          ) : (
            <table border={1} cellPadding={5} cellSpacing={0} style={{ width: '100%', marginBottom: '20px' }}>
              <thead>
                <tr>
                  {Object.keys(optimalPositions[0]).map((key) => (
                    <th key={key}>{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {optimalPositions.map((position, index) => (
                  <tr key={index}>
                    {Object.entries(position).map(([key, value], idx) => (
                      <td key={idx}>
                        {key === 'data' && Array.isArray(value) ? (
                          (() => {
                            const field = value[0].date ? 'date' : (value[0].index ? 'index' : null);
                            if (field) {
                              const latestItem = value.reduce((latest, item) => new Date(item[field]) > new Date(latest[field]) ? item : latest, value[0]);
                              return (
                                <ul style={{ paddingLeft: '20px', margin: 0 }}>
                                  <li>
                                    <ul style={{ paddingLeft: '20px', margin: 0 }}>
                                      {Object.entries(latestItem).map(([k, v]) => (
                                        <li key={k}>{`${k}: ${v}`}</li>
                                      ))}
                                    </ul>
                                  </li>
                                </ul>
                              );
                            }
                            return null;
                          })()
                        ) : (
                          renderCell(value)
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}

      <Dialog open={manualFillOpen} onClose={handleManualFillClose}>
        <DialogTitle>Ручное исполнение ордера</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Цена"
            type="float"
            fullWidth
            value={manualFillPrice}
            onChange={(e) => setManualFillPrice(e.target.value)}
          />
          <TextField
            margin="dense"
            label="Количество"
            type="float"
            fullWidth
            value={manualFillQuantity}
            onChange={(e) => setManualFillQuantity(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleManualFillClose} color="primary">
            Отмена
          </Button>
          <Button onClick={handleManualFillSubmit} color="primary">
            Исполнить
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default OrderStack; 
import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';

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

interface InstrumentTableProps {
  instruments: Instrument[];
  onEdit: (instrument: Instrument) => void;
  onDelete: (id: number) => void;
}

const InstrumentTable: React.FC<InstrumentTableProps> = ({
  instruments,
  onEdit,
  onDelete,
}) => {
  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Инструмент</TableCell>
            <TableCell>Описание</TableCell>
            <TableCell>Размер пункта</TableCell>
            <TableCell>Валюта</TableCell>
            <TableCell>Класс актива</TableCell>
            <TableCell>Проскальзывание</TableCell>
            <TableCell>За блок</TableCell>
            <TableCell>Процент</TableCell>
            <TableCell>За сделку</TableCell>
            <TableCell>Действия</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {instruments.map((instrument) => (
            <TableRow key={instrument.id}>
              <TableCell>{instrument.instrument}</TableCell>
              <TableCell>{instrument.description}</TableCell>
              <TableCell>{instrument.point_size}</TableCell>
              <TableCell>{instrument.currency}</TableCell>
              <TableCell>{instrument.asset_class}</TableCell>
              <TableCell>{instrument.slippage}</TableCell>
              <TableCell>{instrument.per_block || '-'}</TableCell>
              <TableCell>{instrument.percentage || '-'}</TableCell>
              <TableCell>{instrument.per_trade || '-'}</TableCell>
              <TableCell>
                <Tooltip title="Редактировать">
                  <IconButton onClick={() => onEdit(instrument)}>
                    <EditIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Удалить">
                  <IconButton onClick={() => onDelete(instrument.id)}>
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default InstrumentTable; 
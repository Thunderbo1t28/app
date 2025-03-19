import React from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Button,
    IconButton,
    Tooltip,
    Box
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn';
import RefreshIcon from '@mui/icons-material/Refresh';

interface Order {
    id: number;
    symbol: string;
    side: string;
    quantity: number;
    order_type: string;
    price?: number;
    status: string;
    created_at: string;
}

interface OrderTableProps {
    orders: Order[];
    onEdit?: (order: Order) => void;
    onDelete?: (orderId: number) => void;
    onManualFill?: (orderId: number) => void;
    onRefresh?: () => void;
    isLoading?: boolean;
}

export default function OrderTable({ 
    orders, 
    onEdit, 
    onDelete, 
    onManualFill, 
    onRefresh,
    isLoading = false 
}: OrderTableProps) {
    return (
        <>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
                <Button
                    variant="contained"
                    startIcon={<RefreshIcon />}
                    onClick={onRefresh}
                    disabled={isLoading}
                >
                    {isLoading ? 'Обновление...' : 'Обновить ордера'}
                </Button>
            </Box>
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>ID</TableCell>
                            <TableCell>Символ</TableCell>
                            <TableCell>Сторона</TableCell>
                            <TableCell>Количество</TableCell>
                            <TableCell>Тип</TableCell>
                            <TableCell>Цена</TableCell>
                            <TableCell>Статус</TableCell>
                            <TableCell>Создан</TableCell>
                            <TableCell>Действия</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {orders.map((order) => (
                            <TableRow key={order.id}>
                                <TableCell>{order.id}</TableCell>
                                <TableCell>{order.symbol}</TableCell>
                                <TableCell>{order.side}</TableCell>
                                <TableCell>{order.quantity}</TableCell>
                                <TableCell>{order.order_type}</TableCell>
                                <TableCell>{order.price || 'N/A'}</TableCell>
                                <TableCell>{order.status}</TableCell>
                                <TableCell>{new Date(order.created_at).toLocaleString()}</TableCell>
                                <TableCell>
                                    {onEdit && (
                                        <Tooltip title="Редактировать">
                                            <IconButton onClick={() => onEdit(order)} size="small">
                                                <EditIcon />
                                            </IconButton>
                                        </Tooltip>
                                    )}
                                    {onDelete && (
                                        <Tooltip title="Удалить">
                                            <IconButton onClick={() => onDelete(order.id)} size="small">
                                                <DeleteIcon />
                                            </IconButton>
                                        </Tooltip>
                                    )}
                                    {onManualFill && order.status === 'new' && (
                                        <Tooltip title="Ручное заполнение">
                                            <IconButton onClick={() => onManualFill(order.id)} size="small">
                                                <AssignmentTurnedInIcon />
                                            </IconButton>
                                        </Tooltip>
                                    )}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </>
    );
} 
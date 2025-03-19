import React, { useState, useEffect, useCallback } from 'react';
import {
    Box,
    Typography,
    Button,
    CircularProgress,
    Tabs,
    Tab,
    Paper,
    TextField,
    Alert,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    List,
    ListItem,
    ListItemText,
    Divider,
} from '@mui/material';
import {
    PlayArrow as PlayArrowIcon,
    Stop as StopIcon,
    Save as SaveIcon,
    CheckCircle as CheckCircleIcon,
    Error as ErrorIcon,
    Warning as WarningIcon,
    Refresh as RefreshIcon,
    History as HistoryIcon,
} from '@mui/icons-material';
import { useSnackbar } from '../contexts/SnackbarContext';
import api, { systemApi } from '../services/api';

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

interface SystemStatus {
    status: 'running' | 'stopped' | 'error';
    lastRun: string | null;
    error?: string;
}

interface SystemLog {
    timestamp: string;
    level: 'info' | 'warning' | 'error';
    message: string;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
    return (
        <div role="tabpanel" hidden={value !== index}>
            {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
        </div>
    );
};

const SystemControl: React.FC = () => {
    const [value, setValue] = useState(0);
    const [loading, setLoading] = useState(false);
    const [showLogs, setShowLogs] = useState(false);
    const [configPrivate, setConfigPrivate] = useState('');
    const [configControl, setConfigControl] = useState('');
    const [systemStatus, setSystemStatus] = useState<SystemStatus>({
        status: 'stopped',
        lastRun: null,
    });
    const [logs, setLogs] = useState<SystemLog[]>([]);
    const { showMessage } = useSnackbar();

    const loadSystemStatus = useCallback(async () => {
        try {
            const response = await systemApi.getStatus();
            console.log('Статус системы:', response.data);
            setSystemStatus(response.data);
        } catch (error) {
            showMessage('Ошибка при загрузке статуса системы', 'error');
        }
    }, [showMessage]);

    const loadConfigs = useCallback(async () => {
        try {
            const [privateConfig, controlConfig] = await Promise.all([
                systemApi.getConfigPrivate(),
                systemApi.getConfigControl(),
            ]);
            setConfigPrivate(privateConfig.data.content);
            setConfigControl(controlConfig.data.content);
        } catch (error) {
            showMessage('Ошибка при загрузке конфигурации', 'error');
        }
    }, [showMessage]);

    useEffect(() => {
        loadSystemStatus();
        loadConfigs();
    }, [loadSystemStatus, loadConfigs]);

    const handleChange = (event: React.SyntheticEvent, newValue: number) => {
        setValue(newValue);
    };

    const saveConfigs = async () => {
        try {
            setLoading(true);
            await Promise.all([
                systemApi.updateConfigPrivate(configPrivate),
                systemApi.updateConfigControl(configControl),
            ]);
            showMessage('Конфигурация успешно сохранена', 'success');
        } catch (error) {
            showMessage('Ошибка при сохранении конфигурации', 'error');
        } finally {
            setLoading(false);
        }
    };

    const runSystems = async () => {
        try {
            setLoading(true);
            await systemApi.run();
            showMessage('Система запущена', 'success');
            loadSystemStatus();
        } catch (error) {
            showMessage('Ошибка при запуске системы', 'error');
        } finally {
            setLoading(false);
        }
    };

    // Автоматическое обновление статуса системы каждые 5 секунд
    useEffect(() => {
        const timer = setInterval(() => {
            loadSystemStatus();
        }, 5000);
        return () => clearInterval(timer);
    }, [loadSystemStatus]);

    const getStatusIcon = () => {
        switch (systemStatus.status) {
            case 'running':
                return <CircularProgress size={20} />;
            case 'stopped':
                return <CheckCircleIcon color="success" />;
            case 'error':
                return <ErrorIcon color="error" />;
            default:
                return <WarningIcon />;
        }
    };

    const getStatusText = () => {
        switch (systemStatus.status) {
            case 'running':
                return 'Работает';
            case 'stopped':
                return 'Остановлена';
            case 'error':
                return 'Ошибка';
            default:
                return 'Неизвестно';
        }
    };

    return (
        <Box>
            <Paper sx={{ mb: 3 }}>
                <Box sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {getStatusIcon()}
                            <Typography variant="h6">
                                Статус системы: {getStatusText()}
                            </Typography>
                            <Typography variant="caption" sx={{ ml: 2 }}>
                                {JSON.stringify(systemStatus)}
                            </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                            <IconButton onClick={loadSystemStatus} size="small">
                                <RefreshIcon />
                            </IconButton>
                        </Box>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 2 }}>
                        <Button
                            variant="contained"
                            startIcon={<PlayArrowIcon />}
                            onClick={runSystems}
                            disabled={loading || systemStatus.status === 'running'}
                        >
                            Запустить
                        </Button>
                        <Button
                            variant="outlined"
                            startIcon={<HistoryIcon />}
                            onClick={() => setShowLogs(true)}
                        >
                            Логи
                        </Button>
                    </Box>
                </Box>
            </Paper>

            <Paper>
                <Tabs value={value} onChange={handleChange}>
                    <Tab label="Приватная конфигурация" />
                    <Tab label="Контрольная конфигурация" />
                </Tabs>

                <TabPanel value={value} index={0}>
                    <TextField
                        fullWidth
                        multiline
                        rows={20}
                        value={configPrivate}
                        onChange={(e) => setConfigPrivate(e.target.value)}
                    />
                </TabPanel>

                <TabPanel value={value} index={1}>
                    <TextField
                        fullWidth
                        multiline
                        rows={20}
                        value={configControl}
                        onChange={(e) => setConfigControl(e.target.value)}
                    />
                </TabPanel>

                <Box sx={{ p: 2, display: 'flex', justifyContent: 'flex-end' }}>
                    <Button
                        variant="contained"
                        startIcon={<SaveIcon />}
                        onClick={saveConfigs}
                        disabled={loading}
                    >
                        Сохранить
                    </Button>
                </Box>
            </Paper>

            <Dialog
                open={showLogs}
                onClose={() => setShowLogs(false)}
                maxWidth="md"
                fullWidth
            >
                <DialogTitle>Системные логи</DialogTitle>
                <DialogContent>
                    <List>
                        {logs.map((log, index) => (
                            <React.Fragment key={index}>
                                <ListItem>
                                    <ListItemText
                                        primary={log.message}
                                        secondary={new Date(log.timestamp).toLocaleString()}
                                    />
                                </ListItem>
                                {index < logs.length - 1 && <Divider />}
                            </React.Fragment>
                        ))}
                    </List>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setShowLogs(false)}>Закрыть</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default SystemControl;
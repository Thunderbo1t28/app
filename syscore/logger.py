import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

class SystemLogger:
    """Базовый класс для логирования в системе."""
    
    def __init__(self, name: str, log_level: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.log_level = log_level or os.getenv('LOG_LEVEL', 'INFO')
        self.setup_logger()
    
    def setup_logger(self):
        """Настройка логгера."""
        self.logger.setLevel(self.log_level)
        
        # Создаем форматтер
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Добавляем обработчик для файла
        log_file = os.getenv('LOG_FILE', 'django_debug.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Добавляем обработчик для консоли
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs):
        """Логирование отладочной информации."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Логирование информационных сообщений."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Логирование предупреждений."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Логирование ошибок."""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Логирование критических ошибок."""
        self.logger.critical(message, extra=kwargs) 
from typing import Any, Dict, List, Optional
from django.core.cache import cache
from django.db import transaction
from .logger import SystemLogger
from .exceptions import SystematicTradingError

class BaseService:
    """Базовый класс для всех сервисов в системе."""
    
    def __init__(self):
        self.logger = SystemLogger(self.__class__.__name__)
    
    def handle_error(self, error: Exception, message: str) -> None:
        """Обработка ошибок с логированием."""
        self.logger.error(f"{message}: {str(error)}")
        if isinstance(error, SystematicTradingError):
            raise error
        raise SystematicTradingError(message, {"original_error": str(error)})
    
    @staticmethod
    def cache_key(prefix: str, *args) -> str:
        """Генерация ключа для кэша."""
        return f"{prefix}:{'_'.join(str(arg) for arg in args)}"
    
    def get_cached(self, key: str, timeout: int = 300) -> Optional[Any]:
        """Получение данных из кэша."""
        return cache.get(key, timeout)
    
    def set_cached(self, key: str, value: Any, timeout: int = 300) -> None:
        """Сохранение данных в кэш."""
        cache.set(key, value, timeout)
    
    @staticmethod
    def atomic_transaction(func):
        """Декоратор для атомарных транзакций."""
        def wrapper(*args, **kwargs):
            with transaction.atomic():
                return func(*args, **kwargs)
        return wrapper 
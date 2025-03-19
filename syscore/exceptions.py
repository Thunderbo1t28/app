"""
Custom exceptions
"""

from typing import Any, Dict, Optional

class SystematicTradingError(Exception):
    """Базовый класс для всех исключений в проекте."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(SystematicTradingError):
    """Ошибка валидации данных."""
    pass

class TradingError(SystematicTradingError):
    """Ошибка в процессе торговли."""
    pass

class DataError(SystematicTradingError):
    """Ошибка при работе с данными."""
    pass

class ConfigurationError(SystematicTradingError):
    """Ошибка конфигурации."""
    pass

class BrokerError(SystematicTradingError):
    """Ошибка при взаимодействии с брокером."""
    pass

class DatabaseError(SystematicTradingError):
    """Ошибка при работе с базой данных."""
    pass

class missingInstrument(Exception):
    pass


class missingContract(Exception):
    pass


class missingData(Exception):
    pass


class missingFile(Exception):
    pass


class marketClosed(Exception):
    pass


class fillExceedsTrade(Exception):
    pass


class existingData(Exception):
    pass


class orderCannotBeModified(Exception):
    pass


class ContractNotFound(Exception):
    pass

class OrderNotFoundError(Exception):
    """Исключение, возникающее когда ордер не найден"""
    pass

class InvalidOrderDataError(Exception):
    """Исключение, возникающее при неверных данных ордера"""
    pass

class OrderProcessingError(Exception):
    """Исключение, возникающее при ошибке обработки ордера"""
    pass

class SystemNotReadyError(Exception):
    """Исключение, возникающее когда система не готова к работе"""
    pass

class AuthenticationError(Exception):
    """Исключение, возникающее при ошибке аутентификации"""
    pass

class PermissionDeniedError(Exception):
    """Исключение, возникающее при отсутствии прав доступа"""
    pass 
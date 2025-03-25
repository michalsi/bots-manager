class AppException(Exception):
    """Base exception for application errors"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DatabaseError(AppException):
    """Database related errors"""
    pass


class BybitAPIError(AppException):
    """Bybit API related errors"""
    pass

"""Custom application exception hierarchy for centralized API error handling."""

from typing import Any


class AppException(Exception):
    """Base application exception with HTTP status code and machine-readable error code."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = 500,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class NotFoundException(AppException):
    """Raised when a requested resource is not found (HTTP 404)."""

    def __init__(self, message: str = "Resource not found", details: Any = None) -> None:
        super().__init__(message=message, code="NOT_FOUND", status_code=404, details=details)


class ValidationException(AppException):
    """Raised when input validation fails (HTTP 422)."""

    def __init__(self, message: str = "Validation failed", details: Any = None) -> None:
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=422, details=details)


class ConflictException(AppException):
    """Raised when a state conflict or duplicate idempotency key occurs (HTTP 409)."""

    def __init__(self, message: str = "Conflict detected", details: Any = None) -> None:
        super().__init__(message=message, code="CONFLICT", status_code=409, details=details)


class UnauthorizedException(AppException):
    """Raised when authentication is required or invalid (HTTP 401)."""

    def __init__(self, message: str = "Unauthorized", details: Any = None) -> None:
        super().__init__(message=message, code="UNAUTHORIZED", status_code=401, details=details)


class ForbiddenException(AppException):
    """Raised when the authenticated entity lacks permissions (HTTP 403)."""

    def __init__(self, message: str = "Access forbidden", details: Any = None) -> None:
        super().__init__(message=message, code="FORBIDDEN", status_code=403, details=details)


class ServiceUnavailableException(AppException):
    """Raised when an external service or internal subsystem is unavailable (HTTP 503)."""

    def __init__(self, message: str = "Service unavailable", details: Any = None) -> None:
        super().__init__(message=message, code="SERVICE_UNAVAILABLE", status_code=503, details=details)


class DatabaseException(AppException):
    """Raised when a database query or connection failure occurs (HTTP 503)."""

    def __init__(self, message: str = "Database service unavailable", details: Any = None) -> None:
        super().__init__(message=message, code="DATABASE_UNAVAILABLE", status_code=503, details=details)

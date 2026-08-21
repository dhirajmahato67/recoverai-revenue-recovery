"""Structured logging configuration for RecoverAI backend."""

import contextvars
import json
import logging
import sys
from typing import Any
from app.core.config import get_settings

# Context variable for request correlation across async tasks
request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")

# Sensitive key names that should never have their values logged
SENSITIVE_KEYS = {
    "password",
    "secret",
    "token",
    "api_key",
    "authorization",
    "key_secret",
    "card_number",
    "cvv",
    "pin",
    "access_token",
    "refresh_token",
}


def mask_sensitive_data(data: Any) -> Any:
    """Recursively sanitize sensitive key-value pairs from dictionary structures."""
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if any(sensitive in str(k).lower() for sensitive in SENSITIVE_KEYS):
                sanitized[k] = "********"
            else:
                sanitized[k] = mask_sensitive_data(v)
        return sanitized
    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    return data


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects for production log aggregators."""

    def format(self, record: logging.LogRecord) -> str:
        settings = get_settings()
        log_obj: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "service": settings.APP_NAME,
            "environment": settings.APP_ENV,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_ctx.get() or getattr(record, "request_id", ""),
        }

        # Include additional attributes if passed in extra
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_obj.update(mask_sensitive_data(record.extra_data))

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


class DevelopmentFormatter(logging.Formatter):
    """Human-readable formatter with timestamp, level, logger, request ID, and message."""

    def format(self, record: logging.LogRecord) -> str:
        req_id = request_id_ctx.get() or getattr(record, "request_id", "")
        req_part = f"[{req_id[:8]}] " if req_id else ""
        time_str = self.formatTime(record, "%H:%M:%S")
        msg = record.getMessage()
        exc = f"\n{self.formatException(record.exc_info)}" if record.exc_info else ""
        return f"{time_str} | {record.levelname:<7} | {req_part}{record.name}: {msg}{exc}"


def setup_logging() -> None:
    """Initialize root and application loggers according to environment settings."""
    settings = get_settings()
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    if settings.is_production:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(DevelopmentFormatter())

    root_logger.addHandler(handler)

    # Quiet overly chatty third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named application logger."""
    return logging.getLogger(name)

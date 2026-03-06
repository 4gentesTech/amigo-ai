"""Structured logging handler with data sanitization."""

import json
import logging
import sys
from datetime import datetime
from typing import Any

from .config import settings


class LoggingHandler:
    """Logging handler with automatic PII sanitization."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.log_level))

        # Handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, settings.log_level))

        # Formatter
        if settings.log_format == "json":
            handler.setFormatter(JSONFormatter())
        else:
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )

        self.logger.addHandler(handler)

    def _sanitize_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Remove sensitive fields before logging."""
        sensitive_fields = ["content", "message", "response", "current_message"]
        sanitized = data.copy()

        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = "[REDACTED]"

        return sanitized

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info with sanitized data."""
        sanitized = self._sanitize_data(kwargs)
        self.logger.info(message, extra=sanitized)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error with sanitized data."""
        sanitized = self._sanitize_data(kwargs)
        self.logger.error(message, extra=sanitized)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning with sanitized data."""
        sanitized = self._sanitize_data(kwargs)
        self.logger.warning(message, extra=sanitized)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug with sanitized data."""
        sanitized = self._sanitize_data(kwargs)
        self.logger.debug(message, extra=sanitized)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logs."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields
        if hasattr(record, "session_id"):
            log_data["session_id"] = record.session_id
        if hasattr(record, "risk_score"):
            log_data["risk_score"] = record.risk_score
        if hasattr(record, "model"):
            log_data["model"] = record.model

        return json.dumps(log_data)


# Factory
def get_logger(name: str) -> LoggingHandler:
    """Create logging handler instance."""
    return LoggingHandler(name)

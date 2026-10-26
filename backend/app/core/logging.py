"""Structured application logging configuration.

Logs include: timestamp, level, logger name, request_id, user_id,
organization_id, endpoint, duration, status.

Never log passwords, JWT tokens, API keys, or sensitive document contents.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from app.core.config import settings

_RESERVED_ATTRS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "message",
    "asctime",
}


class JsonFormatter(logging.Formatter):
    """Minimal structured JSON formatter."""

    def format(self, record: logging.LogRecord) -> str:
        base: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key in ("request_id", "user_id", "organization_id", "endpoint",
                    "duration_ms", "status"):
            value = getattr(record, key, None)
            if value is not None:
                base[key] = value

        if record.exc_info:
            base["exception"] = self.formatException(record.exc_info)

        extras = {
            k: v for k, v in record.__dict__.items()
            if k not in _RESERVED_ATTRS and not k.startswith("_")
        }
        if extras:
            base["extra"] = extras

        return json.dumps(base, default=str)


def configure_logging() -> None:
    """Configure root logging with a structured JSON handler."""
    root = logging.getLogger()
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    if settings.is_production:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
            )
        )

    root.addHandler(handler)
    root.setLevel(settings.LOG_LEVEL.upper())

    # Quiet noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger."""
    return logging.getLogger(name)
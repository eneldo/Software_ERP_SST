from __future__ import annotations

import logging
import logging.config
from pathlib import Path
from typing import Any

from app.config import settings


class RequestContextFilter(logging.Filter):
    """Ensure structured context fields exist in every log record."""

    DEFAULTS = {
        "request_id": "-",
        "user_id": "-",
        "empresa_id": "-",
        "route": "-",
    }

    def filter(self, record: logging.LogRecord) -> bool:
        for field, default in self.DEFAULTS.items():
            if not hasattr(record, field):
                setattr(record, field, default)
        return True


def setup_logging() -> None:
    """Configure console and rotating-file logs with stable key/value fields."""

    log_dir = Path(settings.LOG_DIR).resolve()
    log_dir.mkdir(parents=True, exist_ok=True)

    level = str(settings.LOG_LEVEL or "INFO").upper()
    app_log = log_dir / "erp_sst_app.log"
    error_log = log_dir / "erp_sst_errors.log"
    structured_format = (
        "%(asctime)s | %(levelname)s | %(name)s | "
        "request_id=%(request_id)s user_id=%(user_id)s empresa_id=%(empresa_id)s route=%(route)s | "
        "%(message)s"
    )

    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {"request_context": {"()": RequestContextFilter}},
        "formatters": {
            "standard": {
                "format": structured_format,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "access": {
                "format": structured_format,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "standard",
                "filters": ["request_context"],
            },
            "app_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": level,
                "formatter": "standard",
                "filters": ["request_context"],
                "filename": str(app_log),
                "maxBytes": int(settings.LOG_MAX_BYTES),
                "backupCount": int(settings.LOG_BACKUP_COUNT),
                "encoding": "utf-8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "standard",
                "filters": ["request_context"],
                "filename": str(error_log),
                "maxBytes": int(settings.LOG_MAX_BYTES),
                "backupCount": int(settings.LOG_BACKUP_COUNT),
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "app": {"handlers": ["console", "app_file", "error_file"], "level": level, "propagate": False},
            "uvicorn.error": {"handlers": ["console", "app_file", "error_file"], "level": level, "propagate": False},
            "uvicorn.access": {"handlers": ["console", "app_file"], "level": "INFO", "propagate": False},
            "sqlalchemy.engine": {"handlers": ["app_file"], "level": settings.SQLALCHEMY_LOG_LEVEL, "propagate": False},
        },
        "root": {"handlers": ["console", "app_file", "error_file"], "level": level},
    }

    logging.config.dictConfig(config)
    logging.getLogger("app").info("Logging Enterprise inicializado")


def get_logger(name: str = "app") -> logging.Logger:
    return logging.getLogger(name)

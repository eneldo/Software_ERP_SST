# ============================================================
# LOGGING CONFIG - ERP SST PRO ENTERPRISE
# FASE 36.8 — Logging Enterprise y Manejo de Errores
# Archivo: backend/app/core/logging_config.py
# ============================================================

from __future__ import annotations

import logging
import logging.config
from pathlib import Path
from typing import Any

from app.config import settings


class RequestIdFilter(logging.Filter):
    """Garantiza que el campo request_id exista en todos los registros."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


def setup_logging() -> None:
    """Configura logging estándar para consola y archivo rotativo.

    No requiere dependencias externas. En desarrollo escribe consola y archivo.
    En producción permite mantener auditoría técnica sin imprimir trazas sensibles.
    """

    log_dir = Path(settings.LOG_DIR).resolve()
    log_dir.mkdir(parents=True, exist_ok=True)

    level = str(settings.LOG_LEVEL or "INFO").upper()
    app_log = log_dir / "erp_sst_app.log"
    error_log = log_dir / "erp_sst_errors.log"

    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {"request_id": {"()": RequestIdFilter}},
        "formatters": {
            "standard": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | request_id=%(request_id)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "access": {
                "format": "%(asctime)s | %(levelname)s | access | request_id=%(request_id)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "standard",
                "filters": ["request_id"],
            },
            "app_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": level,
                "formatter": "standard",
                "filters": ["request_id"],
                "filename": str(app_log),
                "maxBytes": int(settings.LOG_MAX_BYTES),
                "backupCount": int(settings.LOG_BACKUP_COUNT),
                "encoding": "utf-8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "standard",
                "filters": ["request_id"],
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

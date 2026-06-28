# ============================================================
# CONFIGURACIÓN GENERAL DEL ERP SST PRO
# FASE 36.2 — Limpieza y Seguridad Base Backend
# ============================================================

from pathlib import Path
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


def _split_csv(value: str | list[str] | tuple[str, ...]) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(",") if item.strip()]


class Settings(BaseSettings):
    APP_NAME: str = "ERP SST PRO"
    APP_VERSION: str = "2.7.8-hardening-36.8"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Seguridad Enterprise FASE 36.6
    TRUSTED_HOSTS: list[str] = ["localhost", "127.0.0.1"]
    SECURITY_HEADERS_ENABLED: bool = True
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 120
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    MAX_UPLOAD_SIZE_MB: int = 15
    ALLOWED_UPLOAD_EXTENSIONS: list[str] = [
        ".pdf", ".png", ".jpg", ".jpeg", ".webp", ".xlsx", ".xls", ".doc", ".docx", ".csv"
    ]


    UPLOAD_DIR: str = str(BASE_DIR / "app" / "uploads")
    UPLOAD_SUBDIRS: list[str] = [
        "logos",
        "firmas",
        "documentos",
        "evidencias",
        "actas",
        "capacitaciones",
        "examenes-medicos",
        "certificados",
        "auditorias",
        "inspecciones",
        "reportes",
        "medidas-correctivas",
    ]

    # En producción debe ser false y las tablas deben manejarse con migraciones SQL/Alembic.

    # Logging Enterprise FASE 36.8
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = str(BASE_DIR / "logs")
    LOG_MAX_BYTES: int = 5 * 1024 * 1024
    LOG_BACKUP_COUNT: int = 10
    SQLALCHEMY_LOG_LEVEL: str = "WARNING"

    AUTO_CREATE_TABLES: bool = False

    # En producción se recomienda ocultar documentación pública.
    DOCS_URL: str | None = "/docs"
    REDOC_URL: str | None = "/redoc"
    OPENAPI_URL: str | None = "/openapi.json"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        return _split_csv(value)

    @field_validator("UPLOAD_SUBDIRS", mode="before")
    @classmethod
    def parse_upload_subdirs(cls, value: Any) -> list[str]:
        return _split_csv(value)

    @field_validator("TRUSTED_HOSTS", mode="before")
    @classmethod
    def parse_trusted_hosts(cls, value: Any) -> list[str]:
        return _split_csv(value)

    @field_validator("ALLOWED_UPLOAD_EXTENSIONS", mode="before")
    @classmethod
    def parse_upload_extensions(cls, value: Any) -> list[str]:
        return [item.lower() for item in _split_csv(value)]

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if not value or len(value.strip()) < 32:
            raise ValueError("SECRET_KEY debe tener mínimo 32 caracteres.")
        return value.strip()

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

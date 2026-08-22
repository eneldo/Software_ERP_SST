from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


def _split_csv(value: str | list[str] | tuple[str, ...]) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(",") if item.strip()]


class Settings(BaseSettings):
    APP_NAME: str = "ERP SST PRO"
    APP_VERSION: str = "2.7.9-hardening-36.14"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_COOKIE_NAME: str = "erp_sst_refresh"
    REFRESH_COOKIE_SECURE: bool = False
    REFRESH_COOKIE_SAMESITE: str = "lax"
    REFRESH_COOKIE_PATH: str = "/auth"

    ACCESS_COOKIE_NAME: str = "erp_sst_access"
    ACCESS_COOKIE_SECURE: bool = False
    ACCESS_COOKIE_SAMESITE: str = "lax"
    ACCESS_COOKIE_PATH: str = "/"

    CORS_ORIGINS: Annotated[list[str], NoDecode] = Field(
        default=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        validation_alias=AliasChoices("CORS_ORIGINS", "BACKEND_CORS_ORIGINS"),
    )

    TRUSTED_HOSTS: Annotated[list[str], NoDecode] = ["localhost", "127.0.0.1"]
    SECURITY_HEADERS_ENABLED: bool = True
    HTTPS_REDIRECT_ENABLED: bool = False
    HSTS_MAX_AGE_SECONDS: int = 31536000
    HSTS_INCLUDE_SUBDOMAINS: bool = True
    HSTS_PRELOAD: bool = False

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_BACKEND: str = "memory"
    RATE_LIMIT_REDIS_URL: str | None = None
    RATE_LIMIT_REDIS_PREFIX: str = "erp_sst:rate_limit"
    RATE_LIMIT_REQUESTS: int = 120
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    RATE_LIMIT_LOGIN_REQUESTS: int = 5
    RATE_LIMIT_LOGIN_WINDOW_SECONDS: int = 60
    RATE_LIMIT_PUBLIC_REPORT_REQUESTS: int = 10
    RATE_LIMIT_PUBLIC_REPORT_WINDOW_SECONDS: int = 3600
    RATE_LIMIT_UPLOAD_REQUESTS: int = 20
    RATE_LIMIT_UPLOAD_WINDOW_SECONDS: int = 300

    MAX_UPLOAD_SIZE_MB: int = 15
    ALLOWED_UPLOAD_EXTENSIONS: Annotated[list[str], NoDecode] = [
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".xlsx",
        ".xls",
        ".doc",
        ".docx",
        ".csv",
    ]

    UPLOAD_DIR: str = str(BASE_DIR / "app" / "uploads")
    UPLOAD_SUBDIRS: Annotated[list[str], NoDecode] = [
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

    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = str(BASE_DIR / "logs")
    LOG_MAX_BYTES: int = 5 * 1024 * 1024
    LOG_BACKUP_COUNT: int = 10
    SQLALCHEMY_LOG_LEVEL: str = "WARNING"

    AUTO_CREATE_TABLES: bool = False

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

    @field_validator("DOCS_URL", "REDOC_URL", "OPENAPI_URL", mode="before")
    @classmethod
    def parse_optional_url(cls, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        if not text or text.lower() in {"none", "null", "false", "off", "0"}:
            return None
        return text

    @field_validator("RATE_LIMIT_BACKEND")
    @classmethod
    def validate_rate_limit_backend(cls, value: str) -> str:
        backend = str(value or "memory").strip().lower()
        if backend not in {"memory", "redis"}:
            raise ValueError("RATE_LIMIT_BACKEND debe ser memory o redis.")
        return backend

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if not value or len(value.strip()) < 32:
            raise ValueError("SECRET_KEY debe tener minimo 32 caracteres.")
        return value.strip()

    @model_validator(mode="after")
    def validate_production_hardening(self):
        if self.ENVIRONMENT.strip().lower() != "production":
            return self

        self.DOCS_URL = None
        self.REDOC_URL = None
        self.OPENAPI_URL = None

        if self.AUTO_CREATE_TABLES:
            raise ValueError("AUTO_CREATE_TABLES debe ser false en produccion. Use migraciones Alembic.")

        if self.ACCESS_TOKEN_EXPIRE_MINUTES > 30:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES debe ser 30 o menos en produccion.")

        if self.REFRESH_TOKEN_EXPIRE_DAYS > 30:
            raise ValueError("REFRESH_TOKEN_EXPIRE_DAYS debe ser 30 o menos en produccion.")

        if not self.REFRESH_COOKIE_SECURE:
            raise ValueError("REFRESH_COOKIE_SECURE debe ser true en produccion.")

        forbidden_secret_fragments = {"cambiar", "change", "secret", "password", "example", "test"}
        secret_lower = self.SECRET_KEY.lower()
        if len(self.SECRET_KEY) < 64 or any(fragment in secret_lower for fragment in forbidden_secret_fragments):
            raise ValueError("SECRET_KEY de produccion debe ser real, aleatoria y de minimo 64 caracteres.")

        if any(origin == "*" for origin in self.CORS_ORIGINS):
            raise ValueError("CORS_ORIGINS no puede contener '*' en produccion.")

        localhost_markers = ("localhost", "127.0.0.1", "0.0.0.0")
        if any(any(marker in origin for marker in localhost_markers) for origin in self.CORS_ORIGINS):
            raise ValueError("CORS_ORIGINS de produccion no debe usar localhost ni IPs locales.")

        if any(host == "*" for host in self.TRUSTED_HOSTS):
            raise ValueError("TRUSTED_HOSTS no puede contener '*' en produccion.")

        if not self.TRUSTED_HOSTS or any(host in localhost_markers for host in self.TRUSTED_HOSTS):
            raise ValueError("TRUSTED_HOSTS de produccion debe listar dominios reales.")

        if not self.SECURITY_HEADERS_ENABLED:
            raise ValueError("SECURITY_HEADERS_ENABLED debe estar activo en produccion.")

        if self.RATE_LIMIT_ENABLED:
            if self.RATE_LIMIT_BACKEND != "redis":
                raise ValueError("RATE_LIMIT_BACKEND debe ser redis en produccion.")
            if not self.RATE_LIMIT_REDIS_URL:
                raise ValueError("RATE_LIMIT_REDIS_URL es obligatorio en produccion.")

        return self

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

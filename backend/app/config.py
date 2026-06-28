# ============================================================
# CONFIGURACIÓN GENERAL DEL ERP SST PRO
# ============================================================

from pathlib import Path

from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    # URL de conexión a PostgreSQL tomada desde backend/.env
    DATABASE_URL: str

    # Seguridad JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"
        extra = "ignore"


# Objeto global de configuración usado por toda la aplicación
settings = Settings()

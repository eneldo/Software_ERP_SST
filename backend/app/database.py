# ============================================================
# CONEXIÓN A BASE DE DATOS POSTGRESQL
# ERP SST PRO
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


# Motor principal de conexión a PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)


# Sesión local para consultas a la base de datos
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Base principal para todos los modelos SQLAlchemy
Base = declarative_base()


# Dependencia para usar la base de datos en FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

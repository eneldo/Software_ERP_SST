from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class LoginIntento(Base):
    __tablename__ = "login_intentos"

    id = Column(Integer, primary_key=True, index=True)

    correo = Column(String(255), nullable=False)
    ip = Column(String(80), nullable=True)

    exitoso = Column(Boolean, default=False)
    motivo = Column(String(255), nullable=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
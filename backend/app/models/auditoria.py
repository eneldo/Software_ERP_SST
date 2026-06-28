from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Auditoria(Base):
    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(Integer, nullable=True)
    empresa_id = Column(Integer, nullable=True)

    metodo = Column(String(20), nullable=False)
    ruta = Column(String(255), nullable=False)
    accion = Column(String(100), nullable=True)

    ip = Column(String(80), nullable=True)
    user_agent = Column(Text, nullable=True)

    status_code = Column(Integer, nullable=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
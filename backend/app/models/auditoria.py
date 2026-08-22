from sqlalchemy import Column, ForeignKey, Index, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Auditoria(Base):
    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="SET NULL"), nullable=True, index=True)

    metodo = Column(String(20), nullable=False)
    ruta = Column(String(255), nullable=False)
    accion = Column(String(100), nullable=True)

    ip = Column(String(80), nullable=True)
    user_agent = Column(Text, nullable=True)

    status_code = Column(Integer, nullable=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    empresa = relationship("Empresa", foreign_keys=[empresa_id])

    __table_args__ = (
        Index("ix_auditoria_empresa_fecha", "empresa_id", "fecha_creacion"),
    )
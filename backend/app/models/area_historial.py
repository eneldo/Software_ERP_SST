# ============================================================
# MODELO HISTÓRICO SST POR ÁREA - ERP SST PRO
# Archivo: backend/app/models/area_historial.py
# FASE 1.1.3.4 — Histórico SST por Área
# ============================================================

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class AreaHistorialSST(Base):
    """
    Registra eventos SST asociados a un área organizacional.

    Ejemplos de eventos:
    - Inspección SST
    - Cambio de responsable
    - Actualización de nivel de riesgo
    - Hallazgo / observación
    - Plan de mejora
    - Capacitación / inducción
    - Auditoría interna
    """

    __tablename__ = "area_historial_sst"

    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(
        Integer,
        ForeignKey("areas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    tipo_evento = Column(String(80), nullable=False, index=True)
    titulo = Column(String(180), nullable=False)
    descripcion = Column(Text, nullable=True)

    impacto_sst = Column(String(50), nullable=True, index=True)
    estado_resultante = Column(String(50), nullable=True, index=True)
    responsable = Column(String(180), nullable=True)
    evidencia_url = Column(String(500), nullable=True)

    fecha_evento = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    area = relationship("Area")

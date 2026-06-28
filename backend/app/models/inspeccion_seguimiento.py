# ============================================================
# MODELO SEGUIMIENTOS / PLANES DE ACCIÓN - INSPECCIONES SST
# FASE 1.1.8.6 — PLANES DE ACCIÓN Y SEGUIMIENTO ENTERPRISE
# Archivo: backend/app/models/inspeccion_seguimiento.py
# ============================================================

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class InspeccionHallazgoSeguimientoSST(Base):
    __tablename__ = "inspecciones_hallazgos_seguimientos_sst"

    id = Column(Integer, primary_key=True, index=True)
    hallazgo_id = Column(Integer, ForeignKey("inspecciones_hallazgos_sst.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)

    # FASE 1.1.8.6 — Gestión Enterprise del seguimiento
    tipo_accion = Column(String(80), nullable=True, default="CORRECTIVA", index=True)
    responsable = Column(String(255), nullable=True)
    fecha_seguimiento = Column(Date, nullable=True, index=True)
    fecha_proximo_seguimiento = Column(Date, nullable=True, index=True)
    estado = Column(String(40), nullable=True, default="EN_PROCESO", index=True)
    resultado = Column(String(80), nullable=True, default="EN_EJECUCION", index=True)
    comentario = Column(Text, nullable=False)
    porcentaje_avance = Column(Integer, nullable=True, default=0)
    requiere_evidencia = Column(Boolean, nullable=True, default=True)
    observaciones = Column(Text, nullable=True)

    fecha_registro = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    activo = Column(Boolean, nullable=True, default=True, index=True)

    hallazgo = relationship("InspeccionHallazgoSST")
    usuario = relationship("Usuario")

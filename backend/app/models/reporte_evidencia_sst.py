# ============================================================
# MODELO EVIDENCIAS INTELIGENTES REPORTES SST - ERP SST PRO
# FASE 1.1.25.6
# Archivo: backend/app/models/reporte_evidencia_sst.py
# ============================================================

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, BigInteger, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ReporteEvidenciaSST(Base):
    __tablename__ = "reportes_inseguridad_evidencias"

    id = Column(Integer, primary_key=True, index=True)
    reporte_id = Column(Integer, ForeignKey("reportes_inseguridad_sst.id", ondelete="CASCADE"), nullable=False, index=True)

    tipo_archivo = Column(String(30), nullable=False, default="OTRO", index=True)  # IMAGEN, VIDEO, PDF, AUDIO, OTRO
    archivo_nombre = Column(String(255), nullable=True)
    archivo_url = Column(Text, nullable=False)
    archivo_original_url = Column(Text, nullable=True)
    archivo_thumbnail_url = Column(Text, nullable=True)
    mime_type = Column(String(120), nullable=True)

    peso_original_bytes = Column(BigInteger, nullable=True)
    peso_optimizado_bytes = Column(BigInteger, nullable=True)
    extension = Column(String(20), nullable=True)

    categoria_ia = Column(String(80), nullable=True, index=True)
    descripcion_ia = Column(Text, nullable=True)
    origen = Column(String(80), nullable=False, default="REPORTE_ANONIMO_SST", index=True)

    activo = Column(Boolean, nullable=False, default=True, index=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    reporte = relationship("ReporteInseguridadSST", back_populates="evidencias")

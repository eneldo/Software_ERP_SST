# ============================================================
# MODELO MATRIZ LEGAL SST
# FASE 2.4 - MATRIZ LEGAL SST PRO
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class MatrizLegalSST(Base):
    __tablename__ = "matriz_legal_sst"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    archivo_id = Column(Integer, ForeignKey("archivos_sst.id", ondelete="SET NULL"), nullable=True)

    codigo = Column(String(80), nullable=False, default="ML-SST-001")
    norma = Column(String(255), nullable=False)
    tipo_norma = Column(String(120), nullable=True)
    numero_norma = Column(String(80), nullable=True)
    anio = Column(String(10), nullable=True)

    articulo = Column(String(120), nullable=True)
    requisito_legal = Column(Text, nullable=False)
    tema = Column(String(180), nullable=True)

    entidad_emisora = Column(String(255), nullable=True)
    aplicabilidad = Column(String(80), default="APLICA")  # APLICA / NO_APLICA
    estado_cumplimiento = Column(String(80), default="PENDIENTE")  # CUMPLE / PENDIENTE / NO_CUMPLE
    estado_norma = Column(String(80), default="VIGENTE")  # VIGENTE / DEROGADA / MODIFICADA

    responsable = Column(String(255), nullable=True)
    fecha_revision = Column(Date, nullable=True)
    fecha_vencimiento = Column(Date, nullable=True)

    evidencia = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    empresa = relationship("Empresa")
    usuario = relationship("Usuario")
    archivo = relationship("ArchivoSST")
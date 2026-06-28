# ============================================================
# MODELO MATRIZ DE PELIGROS SST - FASE 2.5.3
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class MatrizPeligrosSST(Base):
    __tablename__ = "matriz_peligros_sst"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    archivo_id = Column(Integer, ForeignKey("archivos_sst.id", ondelete="SET NULL"), nullable=True)

    codigo = Column(String(80), default="MP-SST-001", nullable=False)

    proceso = Column(String(180), nullable=False)
    actividad = Column(String(255), nullable=False)
    tarea = Column(String(255), nullable=True)

    peligro = Column(Text, nullable=False)
    clasificacion_peligro = Column(String(120), nullable=False)

    efectos_posibles = Column(Text, nullable=True)

    controles_fuente = Column(Text, nullable=True)
    controles_medio = Column(Text, nullable=True)
    controles_individuo = Column(Text, nullable=True)

    probabilidad = Column(Integer, default=1)
    consecuencia = Column(Integer, default=1)
    nivel_riesgo = Column(Integer, default=1)

    interpretacion_riesgo = Column(String(80), default="BAJO")
    aceptabilidad = Column(String(120), default="ACEPTABLE")

    medidas_intervencion = Column(Text, nullable=True)
    responsable = Column(String(255), nullable=True)

    fecha_revision = Column(Date, nullable=True)
    fecha_vencimiento = Column(Date, nullable=True)

    estado = Column(String(80), default="PENDIENTE")
    evidencia = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    empresa = relationship("Empresa")
    usuario = relationship("Usuario")
    archivo = relationship("ArchivoSST")
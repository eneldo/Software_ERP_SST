# ============================================================
# MODELOS
# AUDITORÍA SST INTELIGENTE
# FASE 1.7
# ERP SST PRO
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class AuditoriaSST(Base):
    __tablename__ = "auditorias_sst"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)

    codigo = Column(String(80), nullable=False, unique=True, index=True)
    nombre = Column(String(255), nullable=False)

    tipo_auditoria = Column(String(80), default="INTERNA")
    estado = Column(String(50), default="PROGRAMADA")

    objetivo = Column(Text, nullable=True)
    alcance = Column(Text, nullable=True)
    criterio = Column(Text, nullable=True)

    auditor_lider = Column(String(255), nullable=True)
    equipo_auditor = Column(Text, nullable=True)

    fecha_programada = Column(Date, nullable=True)
    fecha_inicio = Column(Date, nullable=True)
    fecha_cierre = Column(Date, nullable=True)

    total_hallazgos = Column(Integer, default=0)
    no_conformidades = Column(Integer, default=0)
    observaciones = Column(Integer, default=0)
    oportunidades_mejora = Column(Integer, default=0)

    porcentaje_cierre = Column(Integer, default=0)

    conclusiones = Column(Text, nullable=True)
    recomendaciones = Column(Text, nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    empresa = relationship("Empresa")
    usuario = relationship("Usuario")
    hallazgos = relationship("AuditoriaHallazgoSST", back_populates="auditoria", cascade="all, delete-orphan")


class AuditoriaHallazgoSST(Base):
    __tablename__ = "auditorias_hallazgos_sst"

    id = Column(Integer, primary_key=True, index=True)

    auditoria_id = Column(Integer, ForeignKey("auditorias_sst.id", ondelete="CASCADE"), nullable=False, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)

    codigo = Column(String(80), nullable=False, index=True)

    tipo_hallazgo = Column(String(80), default="OBSERVACION")
    requisito = Column(Text, nullable=True)
    descripcion = Column(Text, nullable=False)

    evidencia = Column(Text, nullable=True)
    causa = Column(Text, nullable=True)
    accion_recomendada = Column(Text, nullable=True)

    responsable = Column(String(255), nullable=True)
    fecha_compromiso = Column(Date, nullable=True)

    estado = Column(String(50), default="ABIERTO")

    plan_mejoramiento_id = Column(Integer, ForeignKey("planes_mejoramiento_sst.id", ondelete="SET NULL"), nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    auditoria = relationship("AuditoriaSST", back_populates="hallazgos")
    empresa = relationship("Empresa")
    usuario = relationship("Usuario")
    plan_mejoramiento = relationship("PlanMejoramientoSST")

# ============================================================
# MODELO EVALUACIÓN INICIAL SST
# FASE 2.3.2A - HARDENING EVIDENCIAS
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class EvaluacionInicialSST(Base):
    __tablename__ = "evaluaciones_iniciales_sst"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    codigo = Column(String(80), nullable=False, default="EVAL-SST-001")
    nombre = Column(String(255), nullable=False, default="Evaluación Inicial SG-SST")
    fecha_evaluacion = Column(Date, nullable=True)
    responsable = Column(String(255), nullable=True)

    total_items = Column(Integer, default=0)
    items_cumplen = Column(Integer, default=0)
    items_no_cumplen = Column(Integer, default=0)
    items_no_aplican = Column(Integer, default=0)

    porcentaje_cumplimiento = Column(Integer, default=0)
    nivel = Column(String(50), default="CRITICO")

    estado = Column(String(50), default="BORRADOR")
    observaciones_generales = Column(Text, nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    empresa = relationship("Empresa")
    usuario = relationship("Usuario")
    items = relationship(
        "EvaluacionInicialItemSST",
        back_populates="evaluacion",
        cascade="all, delete-orphan",
        order_by="EvaluacionInicialItemSST.id",
    )


class EvaluacionInicialItemSST(Base):
    __tablename__ = "evaluacion_inicial_items_sst"

    id = Column(Integer, primary_key=True, index=True)

    evaluacion_id = Column(
        Integer,
        ForeignKey("evaluaciones_iniciales_sst.id", ondelete="CASCADE"),
        nullable=False,
    )

    archivo_id = Column(
        Integer,
        ForeignKey("archivos_sst.id", ondelete="SET NULL"),
        nullable=True,
    )

    estandar = Column(String(255), nullable=False)
    numeral = Column(String(80), nullable=True)
    criterio = Column(Text, nullable=False)

    respuesta = Column(String(30), default="NO_CUMPLE")
    puntaje = Column(Integer, default=0)

    evidencia = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)
    responsable = Column(String(255), nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    evaluacion = relationship("EvaluacionInicialSST", back_populates="items")
    archivo = relationship("ArchivoSST")

# ============================================================
# MODELO
# PLAN DE MEJORAMIENTO SST
# FASE 1.5.0
# ============================================================

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class PlanMejoramientoSST(Base):
    __tablename__ = "planes_mejoramiento_sst"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
    )

    evaluacion_id = Column(
        Integer,
        ForeignKey(
            "evaluaciones_iniciales_sst.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    item_evaluacion_id = Column(
        Integer,
        ForeignKey(
            "evaluacion_inicial_items_sst.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    codigo = Column(
        String(80),
        nullable=False,
        unique=True,
        index=True,
    )

    titulo = Column(
        String(255),
        nullable=False,
    )

    descripcion = Column(
        Text,
        nullable=True,
    )

    causa = Column(
        Text,
        nullable=True,
    )

    accion_correctiva = Column(
        Text,
        nullable=False,
    )

    responsable = Column(
        String(255),
        nullable=True,
    )

    prioridad = Column(
        String(30),
        default="MEDIA",
    )

    estado = Column(
        String(30),
        default="PENDIENTE",
    )

    fecha_apertura = Column(
        Date,
        nullable=True,
    )

    fecha_compromiso = Column(
        Date,
        nullable=True,
    )

    fecha_cierre = Column(
        Date,
        nullable=True,
    )

    porcentaje_avance = Column(
        Integer,
        default=0,
    )

    evidencia = Column(
        Text,
        nullable=True,
    )

    observaciones = Column(
        Text,
        nullable=True,
    )

    activo = Column(
        Boolean,
        default=True,
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    fecha_actualizacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # =====================================================
    # RELACIONES
    # =====================================================

    empresa = relationship("Empresa")

    usuario = relationship("Usuario")

    evaluacion = relationship(
        "EvaluacionInicialSST",
        foreign_keys=[evaluacion_id],
    )

    item_evaluacion = relationship(
        "EvaluacionInicialItemSST",
        foreign_keys=[item_evaluacion_id],
    )
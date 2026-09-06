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

    origen_hallazgo = Column(
        String(40),
        default="OTRO",
        index=True,
    )

    origen_id = Column(
        Integer,
        nullable=True,
        index=True,
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

    responsable_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
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

    verificado_por = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
    )

    fecha_verificacion = Column(
        Date,
        nullable=True,
    )

    resultado_verificacion = Column(
        String(30),
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

    usuario = relationship("Usuario", foreign_keys=[usuario_id])

    responsable_usuario = relationship("Usuario", foreign_keys=[responsable_id])

    verificador = relationship("Usuario", foreign_keys=[verificado_por])

    evaluacion = relationship(
        "EvaluacionInicialSST",
        foreign_keys=[evaluacion_id],
    )

    item_evaluacion = relationship(
        "EvaluacionInicialItemSST",
        foreign_keys=[item_evaluacion_id],
    )
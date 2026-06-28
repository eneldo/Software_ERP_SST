# ============================================================
# MODELO
# EVIDENCIAS PLAN DE MEJORAMIENTO SST
# FASE 1.5.7
# ERP SST PRO
# ============================================================

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class PlanMejoramientoEvidenciaSST(Base):
    __tablename__ = "planes_mejoramiento_evidencias_sst"

    id = Column(Integer, primary_key=True, index=True)

    plan_id = Column(
        Integer,
        ForeignKey("planes_mejoramiento_sst.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

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
        index=True,
    )

    archivo_id = Column(
        Integer,
        ForeignKey("archivos_sst.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    tipo_evidencia = Column(
        String(80),
        default="CIERRE",
    )

    descripcion = Column(
        Text,
        nullable=True,
    )

    url = Column(
        Text,
        nullable=True,
    )

    nombre_original = Column(
        String(500),
        nullable=True,
    )

    extension = Column(
        String(20),
        nullable=True,
    )

    mime_type = Column(
        String(150),
        nullable=True,
    )

    tamano_bytes = Column(
        Integer,
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

    plan = relationship("PlanMejoramientoSST")

    empresa = relationship("Empresa")

    usuario = relationship("Usuario")

    archivo = relationship("ArchivoSST")
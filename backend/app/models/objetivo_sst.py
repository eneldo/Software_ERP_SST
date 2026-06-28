# ============================================================
# MODELO OBJETIVOS SST
# FASE 2.2 - PLANEAR SG-SST PRO
# ============================================================

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
    Boolean,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class ObjetivoSST(Base):
    __tablename__ = "objetivos_sst"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
    )

    objetivo = Column(String(500), nullable=False)

    meta = Column(String(255), nullable=False)

    indicador = Column(String(255), nullable=False)

    responsable = Column(String(255), nullable=True)

    fecha_inicio = Column(Date, nullable=True)

    fecha_fin = Column(Date, nullable=True)

    cumplimiento = Column(Integer, default=0)

    estado = Column(
        String(50),
        default="PLANIFICADO"
    )

    observaciones = Column(Text, nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    empresa = relationship("Empresa")
# ============================================================
# MODELO POLÍTICA SST
# FASE 2.1 - PLANEAR SG-SST PRO
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class PoliticaSST(Base):
    __tablename__ = "politicas_sst"
    __table_args__ = (
        UniqueConstraint("empresa_id", "tipo_politica", "version", name="uq_politica_empresa_tipo_version"),
    )

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)

    tipo_politica = Column(String(50), nullable=False, default="POLITICA_SST", index=True)
    # Tipos: POLITICA_SST, CONVIVENCIA, ALCOHOL_TABACO, PREVENCION_INCENDIOS, PROTECCION_DATOS

    titulo = Column(String(255), nullable=False)
    contenido = Column(Text, nullable=False)

    version = Column(String(30), default="1.0")
    estado = Column(String(50), default="BORRADOR")  # BORRADOR, APROBADA, OBSOLETA

    responsable_sst = Column(String(255), nullable=True)
    representante_legal = Column(String(255), nullable=True)

    fecha_aprobacion = Column(Date, nullable=True)
    fecha_vigencia = Column(Date, nullable=True)

    observaciones = Column(Text, nullable=True)

    divulgada_copasst = Column(Boolean, default=False)
    tiene_acta_divulgacion = Column(Boolean, default=False)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    empresa = relationship("Empresa")
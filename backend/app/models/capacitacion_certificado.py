# ============================================================
# MODELO: CERTIFICADOS DE CAPACITACIÓN SST
# FASE 2.7.4 - HARDENING ENTERPRISE CAPACITACIONES SST
# ============================================================

from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class CapacitacionCertificado(Base):
    __tablename__ = "capacitacion_certificados"

    id = Column(Integer, primary_key=True, index=True)

    capacitacion_id = Column(
        Integer,
        ForeignKey("capacitaciones_sst.id", ondelete="CASCADE"),
        nullable=False,
    )

    asistente_id = Column(
        Integer,
        ForeignKey("capacitaciones_sst_asistentes.id", ondelete="CASCADE"),
        nullable=False,
    )

    archivo_pdf = Column(Text, nullable=True)
    fecha_generacion = Column(DateTime(timezone=True), server_default=func.now())
    activo = Column(Boolean, default=True)

    capacitacion = relationship("CapacitacionSST")
    asistente = relationship("CapacitacionAsistenteSST")

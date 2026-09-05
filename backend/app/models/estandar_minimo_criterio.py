# ============================================================
# MODELO
# CRITERIOS PARAMETRIZABLES ESTÁNDARES MÍNIMOS SG-SST
# Resolución 0312 de 2019 - Anexo técnico
# ============================================================

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class EstandarMinimoCriterio(Base):
    __tablename__ = "estandares_minimos_criterios"

    id = Column(Integer, primary_key=True, index=True)

    tipo_estandares = Column(String(10), nullable=False, index=True)
    estandar = Column(String(180), nullable=False)
    numeral = Column(String(30), nullable=False, index=True)
    criterio = Column(Text, nullable=False)
    puntaje = Column(Integer, nullable=False, default=1)
    version_norma = Column(String(30), nullable=False, default="0312-2019")
    activo = Column(Boolean, nullable=False, default=True, index=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

# ============================================================
# MODELO EXAMEN MÉDICO SST - ERP SST PRO
# FASE 1.1.6.1 — EXÁMENES MÉDICOS SST BASE
# Archivo: backend/app/models/examen_medico.py
# ============================================================

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ExamenMedico(Base):
    __tablename__ = "examenes_medicos"

    id = Column(Integer, primary_key=True, index=True)

    empleado_id = Column(
        Integer,
        ForeignKey("empleados.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    tipo_examen = Column(String(50), nullable=False, index=True)
    fecha_examen = Column(Date, nullable=False, index=True)
    fecha_vencimiento = Column(Date, nullable=True, index=True)

    concepto = Column(String(50), nullable=False, index=True)
    restricciones = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)

    estado = Column(String(30), default="VIGENTE", index=True)
    activo = Column(Boolean, default=True, index=True)

    medico_ocupacional = Column(String(255), nullable=True)
    entidad_salud = Column(String(255), nullable=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    empleado = relationship("Empleado")

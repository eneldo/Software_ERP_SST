# ============================================================
# MODELOS CAPACITACIONES SST
# FASE 2.7.1 - HACER / CAPACITACIONES SST PRO ENTERPRISE
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class CapacitacionSST(Base):
    __tablename__ = "capacitaciones_sst"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    archivo_id = Column(Integer, ForeignKey("archivos_sst.id", ondelete="SET NULL"), nullable=True)

    codigo = Column(String(80), nullable=False, default="CAP-SST-001")
    nombre = Column(String(255), nullable=False)
    tema = Column(String(255), nullable=False)
    objetivo = Column(Text, nullable=True)

    tipo = Column(String(80), default="INTERNA")
    modalidad = Column(String(80), default="PRESENCIAL")

    capacitador = Column(String(255), nullable=True)
    responsable = Column(String(255), nullable=True)

    fecha_programada = Column(Date, nullable=True)
    fecha_ejecucion = Column(Date, nullable=True)

    duracion_horas = Column(Numeric(8, 2), default=0)
    lugar = Column(String(255), nullable=True)

    poblacion_objetivo = Column(Text, nullable=True)
    total_asistentes = Column(Integer, default=0)

    estado = Column(String(80), default="PROGRAMADA")
    cumplimiento = Column(Integer, default=0)

    evidencia = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    empresa = relationship("Empresa")
    usuario = relationship("Usuario")
    archivo = relationship("ArchivoSST")
    asistentes = relationship(
        "CapacitacionAsistenteSST",
        back_populates="capacitacion",
        cascade="all, delete-orphan",
    )


class CapacitacionAsistenteSST(Base):
    __tablename__ = "capacitaciones_sst_asistentes"

    id = Column(Integer, primary_key=True, index=True)

    capacitacion_id = Column(
        Integer,
        ForeignKey("capacitaciones_sst.id", ondelete="CASCADE"),
        nullable=False,
    )

    empleado_id = Column(Integer, ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True)

    nombres = Column(String(255), nullable=False)
    documento = Column(String(80), nullable=True)
    cargo = Column(String(255), nullable=True)
    area = Column(String(255), nullable=True)

    asistio = Column(Boolean, default=True)
    evaluacion = Column(Numeric(5, 2), nullable=True)
    certificado_generado = Column(Boolean, default=False)

    firma_url = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    capacitacion = relationship("CapacitacionSST", back_populates="asistentes")

    __table_args__ = (
        UniqueConstraint("capacitacion_id", "empleado_id", name="uq_cap_asistente_empleado"),
    )
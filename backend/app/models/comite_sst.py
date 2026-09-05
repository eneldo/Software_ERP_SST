# ============================================================
# MODELO COMITÉS SST - COPASST / VIGÍA SST
# FASE auditoría - H-008
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class ComiteSST(Base):
    __tablename__ = "comites_sst"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    tipo_comite = Column(String(50), nullable=False, index=True)  # COPASST / VIGIA_SST / CONVIVENCIA
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)

    fecha_constitucion = Column(Date, nullable=True)
    fecha_fin_periodo = Column(Date, nullable=True)
    vigente = Column(Boolean, default=True, index=True)

    observaciones = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    empresa = relationship("Empresa")
    usuario = relationship("Usuario")
    integrantes = relationship("ComiteIntegranteSST", back_populates="comite", cascade="all, delete-orphan")
    reuniones = relationship("ComiteReunionSST", back_populates="comite", cascade="all, delete-orphan")


class ComiteIntegranteSST(Base):
    __tablename__ = "comites_integrantes_sst"

    id = Column(Integer, primary_key=True, index=True)
    comite_id = Column(Integer, ForeignKey("comites_sst.id", ondelete="CASCADE"), nullable=False, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True)

    nombre = Column(String(255), nullable=False)
    documento = Column(String(80), nullable=True)
    cargo = Column(String(255), nullable=True)
    rol_comite = Column(String(100), nullable=False)  # PRESIDENTE / SECRETARIO / INTEGRANTE / SUPLENTE
    representa = Column(String(100), nullable=True)  # EMPLEADOS / DIRECCION / CONTRATISTAS
    fecha_eleccion = Column(Date, nullable=True)
    fecha_fin_cargo = Column(Date, nullable=True)

    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    comite = relationship("ComiteSST", back_populates="integrantes")
    empresa = relationship("Empresa")
    empleado = relationship("Empleado")


class ComiteReunionSST(Base):
    __tablename__ = "comites_reuniones_sst"

    id = Column(Integer, primary_key=True, index=True)
    comite_id = Column(Integer, ForeignKey("comites_sst.id", ondelete="CASCADE"), nullable=False, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    numero_reunion = Column(Integer, nullable=False)
    fecha_reunion = Column(Date, nullable=False, index=True)
    hora_inicio = Column(String(20), nullable=True)
    hora_fin = Column(String(20), nullable=True)
    lugar = Column(String(255), nullable=True)

    tema = Column(Text, nullable=True)
    acuerdos = Column(Text, nullable=True)
    compromisos = Column(Text, nullable=True)

    total_asistentes = Column(Integer, default=0)
    asistentes_ids = Column(Text, nullable=True)  # JSON array de IDs de empleados

    acta_url = Column(String(500), nullable=True)
    acta_archivo_id = Column(Integer, ForeignKey("archivos_sst.id", ondelete="SET NULL"), nullable=True)

    estado = Column(String(50), default="PROGRAMADA", index=True)  # PROGRAMADA / REALIZADA / CANCELADA

    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    comite = relationship("ComiteSST", back_populates="reuniones")
    empresa = relationship("Empresa")
    usuario = relationship("Usuario")

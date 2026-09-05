# ============================================================
# MODELO EMERGENCIAS SST
# FASE auditoría - H-009
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class BrigadaEmergencia(Base):
    __tablename__ = "brigadas_emergencia"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    nombre = Column(String(255), nullable=False)
    tipo_brigada = Column(String(100), nullable=False, index=True)  # INCENDIO / PRIMEROS_AUXILIOS / EVACUACION / RESCATE
    descripcion = Column(Text, nullable=True)
    fecha_conformacion = Column(Date, nullable=True)

    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    empresa = relationship("Empresa")
    usuario = relationship("Usuario")
    integrantes = relationship("BrigadaIntegranteSST", back_populates="brigada", cascade="all, delete-orphan")


class BrigadaIntegranteSST(Base):
    __tablename__ = "brigadas_integrantes_sst"

    id = Column(Integer, primary_key=True, index=True)
    brigada_id = Column(Integer, ForeignKey("brigadas_emergencia.id", ondelete="CASCADE"), nullable=False, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True)

    nombre = Column(String(255), nullable=False)
    documento = Column(String(80), nullable=True)
    cargo = Column(String(255), nullable=True)
    rol_brigada = Column(String(100), nullable=False)  # LIDER / MIEMBRO / SUPLENTE
    telefono = Column(String(80), nullable=True)

    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    brigada = relationship("BrigadaEmergencia", back_populates="integrantes")
    empresa = relationship("Empresa")
    empleado = relationship("Empleado")


class SimulacroEmergencia(Base):
    __tablename__ = "simulacros_emergencia"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    codigo = Column(String(80), nullable=False, index=True)
    nombre = Column(String(255), nullable=False)
    tipo_emergencia = Column(String(100), nullable=False, index=True)  # INCENDIO / SISMO / EVACUACION / DERRAME / OTRO
    fecha_programada = Column(Date, nullable=False, index=True)
    fecha_ejecutada = Column(Date, nullable=True)
    hora_inicio = Column(String(20), nullable=True)
    hora_fin = Column(String(20), nullable=True)
    lugar = Column(String(255), nullable=True)

    total_participantes = Column(Integer, default=0)
    tiempo_respuesta_minutos = Column(Integer, nullable=True)
    observaciones = Column(Text, nullable=True)

    resultado = Column(String(100), nullable=True)  # SATISFACTORIO / MEJORABLE / NO_SATISFACTORIO
    recomendaciones = Column(Text, nullable=True)
    plan_mejora = Column(Text, nullable=True)

    estado = Column(String(50), default="PROGRAMADO", index=True)  # PROGRAMADO / EJECUTADO / CANCELADO

    evidencia_url = Column(String(500), nullable=True)
    archivo_id = Column(Integer, ForeignKey("archivos_sst.id", ondelete="SET NULL"), nullable=True)

    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    empresa = relationship("Empresa")
    usuario = relationship("Usuario")


class AmenazaEmergencia(Base):
    __tablename__ = "amenazas_emergencia"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    nombre = Column(String(255), nullable=False)
    tipo_amenaza = Column(String(100), nullable=False, index=True)  # NATURAL / TECNOLOGICA / SOCIOPolitICA
    descripcion = Column(Text, nullable=True)
    probabilidad = Column(String(50), nullable=True)  # BAJA / MEDIA / ALTA
    impacto = Column(String(50), nullable=True)  # BAJO / MEDIO / ALTO
    nivel_riesgo = Column(String(50), nullable=True)  # BAJO / MEDIO / ALTO / CRITICO

    medidas_prevencion = Column(Text, nullable=True)
    medidas_control = Column(Text, nullable=True)

    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    empresa = relationship("Empresa")
    usuario = relationship("Usuario")


class InspeccionEmergencia(Base):
    __tablename__ = "inspecciones_emergencia"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    codigo = Column(String(80), nullable=False, index=True)
    nombre = Column(String(255), nullable=False)
    tipo_inspeccion = Column(String(100), nullable=False, index=True)  # EQUIPOS_EMERGENCIA / RUTAS_EVACUACION / SEÑALIZACION / BRIGADAS
    fecha_inspeccion = Column(Date, nullable=False, index=True)
    lugar = Column(String(255), nullable=True)

    estado_equipo = Column(String(50), nullable=True)  # BUENO / REGULAR / MALO
    observaciones = Column(Text, nullable=True)
    hallazgos = Column(Text, nullable=True)
    acciones_correctivas = Column(Text, nullable=True)

    estado = Column(String(50), default="REALIZADA", index=True)

    evidencia_url = Column(String(500), nullable=True)
    archivo_id = Column(Integer, ForeignKey("archivos_sst.id", ondelete="SET NULL"), nullable=True)

    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    empresa = relationship("Empresa")
    usuario = relationship("Usuario")

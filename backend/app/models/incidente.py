# ============================================================
# MODELOS INCIDENTES Y ACCIDENTES SST ENTERPRISE
# FASE 1.1.8.8.3 — INVESTIGACIÓN Y ÁRBOL DE CAUSAS
# Archivo: backend/app/models/incidente.py
# ============================================================

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class IncidenteAccidenteSST(Base):
    __tablename__ = "incidentes_accidentes_sst"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="SET NULL"), nullable=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id", ondelete="SET NULL"), nullable=True, index=True)
    cargo_id = Column(Integer, ForeignKey("cargos.id", ondelete="SET NULL"), nullable=True, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)

    codigo = Column(String(80), nullable=False, index=True)
    tipo_evento = Column(String(40), nullable=False, default="INCIDENTE", index=True)
    clasificacion = Column(String(60), nullable=False, default="INCIDENTE", index=True)
    titulo = Column(String(255), nullable=False, index=True)
    descripcion = Column(Text, nullable=False)
    lugar = Column(String(255), nullable=True)

    fecha_evento = Column(Date, nullable=False, index=True)
    hora_evento = Column(String(20), nullable=True)
    fecha_reporte = Column(Date, nullable=True, index=True)

    estado = Column(String(40), nullable=False, default="REPORTADO", index=True)
    severidad = Column(String(40), nullable=False, default="BAJA", index=True)
    consecuencia = Column(String(120), nullable=True)
    dias_incapacidad = Column(Integer, nullable=True, default=0)
    requiere_investigacion = Column(Boolean, nullable=True, default=True, index=True)
    requiere_capa = Column(Boolean, nullable=True, default=False, index=True)
    capa_id = Column(Integer, ForeignKey("capas_sst.id", ondelete="SET NULL"), nullable=True, index=True)

    acto_inseguro = Column(Text, nullable=True)
    condicion_insegura = Column(Text, nullable=True)
    causa_inmediata = Column(Text, nullable=True)
    causa_basica = Column(Text, nullable=True)
    causa_raiz = Column(Text, nullable=True)
    accion_inmediata = Column(Text, nullable=True)

    # FASE 1.1.8.8.3 — Investigación y Árbol de Causas
    equipo_investigador = Column(Text, nullable=True)
    investigador_lider = Column(String(255), nullable=True)
    fecha_investigacion = Column(Date, nullable=True, index=True)
    metodologia_investigacion = Column(String(80), nullable=True, default="5_PORQUES")
    estado_investigacion = Column(String(60), nullable=True, default="PENDIENTE", index=True)
    descripcion_hechos = Column(Text, nullable=True)
    agente_material = Column(String(255), nullable=True)
    mecanismo_evento = Column(String(255), nullable=True)
    tipo_contacto = Column(String(255), nullable=True)
    porque_1 = Column(Text, nullable=True)
    porque_2 = Column(Text, nullable=True)
    porque_3 = Column(Text, nullable=True)
    porque_4 = Column(Text, nullable=True)
    porque_5 = Column(Text, nullable=True)
    factores_personales = Column(Text, nullable=True)
    factores_trabajo = Column(Text, nullable=True)
    factores_organizacionales = Column(Text, nullable=True)
    causas_directas = Column(Text, nullable=True)
    causas_indirectas = Column(Text, nullable=True)
    arbol_causas = Column(Text, nullable=True)
    controles_existentes = Column(Text, nullable=True)
    controles_recomendados = Column(Text, nullable=True)
    plan_investigacion = Column(Text, nullable=True)
    conclusion_investigacion = Column(Text, nullable=True)
    recomendaciones_investigacion = Column(Text, nullable=True)
    investigacion_cerrada = Column(Boolean, nullable=True, default=False, index=True)
    fecha_cierre_investigacion = Column(DateTime(timezone=True), nullable=True)

    observaciones = Column(Text, nullable=True)
    trazabilidad = Column(Text, nullable=True)

    activo = Column(Boolean, nullable=True, default=True, index=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    empresa = relationship("Empresa")
    sede = relationship("Sede")
    area = relationship("Area")
    cargo = relationship("Cargo")
    empleado = relationship("Empleado")
    usuario = relationship("Usuario")
    lesionados = relationship("IncidenteLesionadoSST", back_populates="incidente", cascade="all, delete-orphan")
    testigos = relationship("IncidenteTestigoSST", back_populates="incidente", cascade="all, delete-orphan")


class IncidenteLesionadoSST(Base):
    __tablename__ = "incidentes_lesionados_sst"

    id = Column(Integer, primary_key=True, index=True)
    incidente_id = Column(Integer, ForeignKey("incidentes_accidentes_sst.id", ondelete="CASCADE"), nullable=False, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True, index=True)

    nombre = Column(String(255), nullable=False, index=True)
    documento = Column(String(80), nullable=True, index=True)
    cargo = Column(String(255), nullable=True)
    parte_cuerpo_afectada = Column(String(180), nullable=True)
    tipo_lesion = Column(String(180), nullable=True)
    gravedad = Column(String(40), nullable=True, default="LEVE", index=True)
    dias_incapacidad = Column(Integer, nullable=True, default=0)
    atencion_medica = Column(Boolean, nullable=True, default=False)
    descripcion_lesion = Column(Text, nullable=True)
    activo = Column(Boolean, nullable=True, default=True, index=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    incidente = relationship("IncidenteAccidenteSST", back_populates="lesionados")
    empresa = relationship("Empresa")
    empleado = relationship("Empleado")


class IncidenteTestigoSST(Base):
    __tablename__ = "incidentes_testigos_sst"

    id = Column(Integer, primary_key=True, index=True)
    incidente_id = Column(Integer, ForeignKey("incidentes_accidentes_sst.id", ondelete="CASCADE"), nullable=False, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)

    nombre = Column(String(255), nullable=False, index=True)
    documento = Column(String(80), nullable=True, index=True)
    cargo = Column(String(255), nullable=True)
    telefono = Column(String(80), nullable=True)
    correo = Column(String(255), nullable=True)
    declaracion = Column(Text, nullable=True)
    firma = Column(Text, nullable=True)
    firma_fecha = Column(DateTime(timezone=True), nullable=True)
    activo = Column(Boolean, nullable=True, default=True, index=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    incidente = relationship("IncidenteAccidenteSST", back_populates="testigos")
    empresa = relationship("Empresa")

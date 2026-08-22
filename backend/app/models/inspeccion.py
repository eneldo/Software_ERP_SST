# ============================================================
# MODELOS INSPECCIONES SST ENTERPRISE - ERP SST PRO
# FASE 1.1.8 — INSPECCIONES SST ENTERPRISE
# Archivo: backend/app/models/inspeccion.py
# ============================================================

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class InspeccionSST(Base):
    __tablename__ = "inspecciones_sst"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="SET NULL"), nullable=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id", ondelete="SET NULL"), nullable=True, index=True)
    cargo_id = Column(Integer, ForeignKey("cargos.id", ondelete="SET NULL"), nullable=True, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)

    codigo = Column(String(80), nullable=False, index=True)
    tipo_inspeccion = Column(String(80), nullable=False, default="GENERAL", index=True)
    titulo = Column(String(255), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    lugar = Column(String(255), nullable=True)
    responsable = Column(String(255), nullable=True)

    fecha_programada = Column(Date, nullable=True, index=True)
    fecha_inspeccion = Column(Date, nullable=False, index=True)

    estado = Column(String(40), nullable=True, default="PROGRAMADA", index=True)
    resultado = Column(String(40), nullable=True, default="PENDIENTE", index=True)
    nivel_riesgo = Column(String(40), nullable=True, default="BAJO", index=True)
    cumplimiento = Column(Numeric(5, 2), nullable=True, default=0)
    observaciones = Column(Text, nullable=True)

    # FASE 1.1.8.4 — Workflow y firmas digitales de inspección
    firma_inspector = Column(Text, nullable=True)
    firma_inspector_nombre = Column(String(255), nullable=True)
    firma_inspector_fecha = Column(DateTime(timezone=True), nullable=True)
    firma_responsable_area = Column(Text, nullable=True)
    firma_responsable_area_nombre = Column(String(255), nullable=True)
    firma_responsable_area_fecha = Column(DateTime(timezone=True), nullable=True)
    firma_sst = Column(Text, nullable=True)
    firma_sst_nombre = Column(String(255), nullable=True)
    firma_sst_fecha = Column(DateTime(timezone=True), nullable=True)
    cierre_digital = Column(Boolean, nullable=True, default=False, index=True)
    cierre_digital_fecha = Column(DateTime(timezone=True), nullable=True)
    cierre_digital_usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)
    trazabilidad = Column(Text, nullable=True)

    activo = Column(Boolean, nullable=True, default=True, index=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    empresa = relationship("Empresa", lazy="select")
    sede = relationship("Sede", lazy="select")
    area = relationship("Area", lazy="select")
    cargo = relationship("Cargo", lazy="select")
    empleado = relationship("Empleado", lazy="select")
    usuario = relationship("Usuario", foreign_keys=[usuario_id], lazy="select")
    usuario_cierre = relationship("Usuario", foreign_keys=[cierre_digital_usuario_id], lazy="select")
    hallazgos = relationship("InspeccionHallazgoSST", back_populates="inspeccion", cascade="all, delete-orphan", lazy="select")


class InspeccionHallazgoSST(Base):
    __tablename__ = "inspecciones_hallazgos_sst"

    id = Column(Integer, primary_key=True, index=True)
    inspeccion_id = Column(Integer, ForeignKey("inspecciones_sst.id", ondelete="CASCADE"), nullable=False, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)

    descripcion = Column(Text, nullable=False)
    tipo_hallazgo = Column(String(80), nullable=True, default="CONDICION_INSEGURA", index=True)
    nivel_riesgo = Column(String(40), nullable=True, default="MEDIO", index=True)
    accion_recomendada = Column(Text, nullable=True)
    responsable = Column(String(255), nullable=True)
    fecha_compromiso = Column(Date, nullable=True, index=True)
    fecha_cierre = Column(Date, nullable=True)
    estado = Column(String(40), nullable=True, default="ABIERTO", index=True)
    observaciones = Column(Text, nullable=True)
    activo = Column(Boolean, nullable=True, default=True, index=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    inspeccion = relationship("InspeccionSST", back_populates="hallazgos")
    empresa = relationship("Empresa")

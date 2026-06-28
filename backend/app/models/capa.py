# ============================================================
# MODELOS CAPA SST ENTERPRISE - ERP SST PRO
# FASE 1.1.8.7 — Centro de Acciones Correctivas, Preventivas y de Mejora
# Archivo: backend/app/models/capa.py
# ============================================================

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class CapaSST(Base):
    __tablename__ = "capas_sst"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="SET NULL"), nullable=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id", ondelete="SET NULL"), nullable=True, index=True)
    cargo_id = Column(Integer, ForeignKey("cargos.id", ondelete="SET NULL"), nullable=True, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)

    inspeccion_id = Column(Integer, ForeignKey("inspecciones_sst.id", ondelete="SET NULL"), nullable=True, index=True)
    hallazgo_id = Column(Integer, ForeignKey("inspecciones_hallazgos_sst.id", ondelete="SET NULL"), nullable=True, index=True)

    codigo = Column(String(80), nullable=False, index=True)
    titulo = Column(String(255), nullable=False, index=True)
    descripcion = Column(Text, nullable=False)
    tipo_accion = Column(String(60), nullable=False, default="CORRECTIVA", index=True)
    origen = Column(String(80), nullable=False, default="INSPECCION_SST", index=True)
    prioridad = Column(String(40), nullable=False, default="MEDIA", index=True)
    estado = Column(String(50), nullable=False, default="ABIERTA", index=True)

    responsable = Column(String(255), nullable=True)
    fecha_apertura = Column(Date, nullable=True, index=True)
    fecha_compromiso = Column(Date, nullable=True, index=True)
    fecha_cierre = Column(Date, nullable=True, index=True)
    avance = Column(Numeric(5, 2), nullable=False, default=0)

    # Análisis causa raíz
    causa_raiz = Column(Text, nullable=True)
    porque_1 = Column(Text, nullable=True)
    porque_2 = Column(Text, nullable=True)
    porque_3 = Column(Text, nullable=True)
    porque_4 = Column(Text, nullable=True)
    porque_5 = Column(Text, nullable=True)
    ishikawa_metodo = Column(Text, nullable=True)
    ishikawa_mano_obra = Column(Text, nullable=True)
    ishikawa_maquinaria = Column(Text, nullable=True)
    ishikawa_materiales = Column(Text, nullable=True)
    ishikawa_medio_ambiente = Column(Text, nullable=True)
    ishikawa_medicion = Column(Text, nullable=True)

    accion_inmediata = Column(Text, nullable=True)
    accion_correctiva = Column(Text, nullable=True)
    accion_preventiva = Column(Text, nullable=True)
    verificacion_eficacia = Column(Text, nullable=True)
    efectiva = Column(Boolean, nullable=True)
    observaciones = Column(Text, nullable=True)
    trazabilidad = Column(Text, nullable=True)
    activo = Column(Boolean, nullable=False, default=True, index=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    empresa = relationship("Empresa")
    sede = relationship("Sede")
    area = relationship("Area")
    cargo = relationship("Cargo")
    empleado = relationship("Empleado")
    usuario = relationship("Usuario")
    inspeccion = relationship("InspeccionSST")
    hallazgo = relationship("InspeccionHallazgoSST")
    seguimientos = relationship("CapaSeguimientoSST", back_populates="capa", cascade="all, delete-orphan")


class CapaSeguimientoSST(Base):
    __tablename__ = "capas_seguimientos_sst"

    id = Column(Integer, primary_key=True, index=True)
    capa_id = Column(Integer, ForeignKey("capas_sst.id", ondelete="CASCADE"), nullable=False, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)

    fecha_seguimiento = Column(Date, nullable=False, index=True)
    responsable = Column(String(255), nullable=True)
    avance = Column(Numeric(5, 2), nullable=False, default=0)
    resultado = Column(String(80), nullable=True, default="EN_SEGUIMIENTO", index=True)
    comentario = Column(Text, nullable=False)
    proximo_seguimiento = Column(Date, nullable=True, index=True)
    activo = Column(Boolean, nullable=False, default=True, index=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    capa = relationship("CapaSST", back_populates="seguimientos")
    empresa = relationship("Empresa")
    usuario = relationship("Usuario")

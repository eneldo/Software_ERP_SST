# ============================================================
# MODELO REPORTE INSEGURIDAD SST - ERP SST PRO
# FASE 1.1.25.6 — Evidencias Inteligentes Reportes SST
# Archivo: backend/app/models/reporte_inseguridad.py
# ============================================================

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ReporteInseguridadSST(Base):
    __tablename__ = "reportes_inseguridad_sst"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="SET NULL"), nullable=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id", ondelete="SET NULL"), nullable=True, index=True)
    cargo_id = Column(Integer, ForeignKey("cargos.id", ondelete="SET NULL"), nullable=True, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)

    codigo = Column(String(80), nullable=False, index=True)
    tipo_reporte = Column(String(60), nullable=False, default="CONDICION_INSEGURA", index=True)
    prioridad = Column(String(30), nullable=False, default="MEDIA", index=True)
    estado = Column(String(40), nullable=False, default="REPORTADO", index=True)

    titulo = Column(String(255), nullable=False, index=True)
    descripcion = Column(Text, nullable=False)
    ubicacion = Column(String(255), nullable=True)

    responsable_asignado = Column(String(255), nullable=True)
    accion_inmediata = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)
    trazabilidad = Column(Text, nullable=True)

    # Compatibilidad con fases anteriores: evidencia principal/legado
    archivo_url = Column(String(500), nullable=True)
    archivo_nombre = Column(String(255), nullable=True)
    archivo_mime_type = Column(String(120), nullable=True)
    archivo_tamano_bytes = Column(Integer, nullable=True)

    origen = Column(String(80), nullable=False, default="PORTAL_EMPLEADO", index=True)
    genera_notificacion = Column(Boolean, nullable=False, default=True)
    convertido_a_inspeccion = Column(Boolean, nullable=False, default=False)
    inspeccion_id = Column(Integer, ForeignKey("inspecciones_sst.id", ondelete="SET NULL"), nullable=True, index=True)
    capa_id = Column(Integer, ForeignKey("capas_sst.id", ondelete="SET NULL"), nullable=True, index=True)
    incidente_id = Column(Integer, ForeignKey("incidentes_accidentes_sst.id", ondelete="SET NULL"), nullable=True, index=True)

    activo = Column(Boolean, nullable=False, default=True, index=True)

    fecha_reporte = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    fecha_cierre = Column(DateTime(timezone=True), nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    empresa = relationship("Empresa")
    sede = relationship("Sede")
    area = relationship("Area")
    cargo = relationship("Cargo")
    empleado = relationship("Empleado")
    usuario = relationship("Usuario")
    evidencias = relationship(
        "ReporteEvidenciaSST",
        back_populates="reporte",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ReporteEvidenciaSST.fecha_creacion.desc()",
    )

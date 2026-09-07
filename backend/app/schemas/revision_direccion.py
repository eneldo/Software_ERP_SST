# ============================================================
# USO DEL ARCHIVO:
# Schemas Pydantic para el módulo Revisión por la Dirección SST.
#
# Incluye:
# - Crear / actualizar revisión
# - Respuesta completa con compromisos
# - Dashboard ejecutivo
# - Campos para doble firma electrónica
#
# Ubicación:
# backend/app/schemas/revision_direccion.py
#
# FASE 1.8.4.1 — Firma Gerente + Doble Firma Electrónica
# ============================================================

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import ConfigDict,  BaseModel


class RevisionDireccionCompromisoCreate(BaseModel):
    compromiso: str
    responsable: Optional[str] = None
    fecha_compromiso: Optional[date] = None
    prioridad: Optional[str] = "MEDIA"
    observaciones: Optional[str] = None


class RevisionDireccionCompromisoUpdate(BaseModel):
    compromiso: Optional[str] = None
    responsable: Optional[str] = None
    fecha_compromiso: Optional[date] = None
    fecha_cierre: Optional[date] = None
    prioridad: Optional[str] = None
    estado: Optional[str] = None
    observaciones: Optional[str] = None


class RevisionDireccionCompromisoResponse(BaseModel):
    id: int
    revision_id: int
    empresa_id: int

    compromiso: str
    responsable: Optional[str] = None
    fecha_compromiso: Optional[date] = None
    fecha_cierre: Optional[date] = None

    prioridad: str
    estado: str

    observaciones: Optional[str] = None
    activo: bool

    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RevisionDireccionCreate(BaseModel):
    empresa_id: int
    titulo: str
    fecha_revision: date

    gerente_usuario_id: Optional[int] = None
    responsable_sst_usuario_id: Optional[int] = None

    periodo_evaluado: Optional[str] = None
    gerente: Optional[str] = None
    responsable_sst: Optional[str] = None
    participantes: Optional[str] = None

    objetivo: Optional[str] = None
    alcance: Optional[str] = None
    agenda: Optional[str] = None

    resumen_auditorias: Optional[str] = None
    resumen_indicadores: Optional[str] = None
    resumen_planes_mejora: Optional[str] = None
    resumen_accidentes: Optional[str] = None
    resumen_capacitaciones: Optional[str] = None
    resumen_cumplimiento_legal: Optional[str] = None

    conclusiones: Optional[str] = None
    decisiones: Optional[str] = None
    recomendaciones: Optional[str] = None


class RevisionDireccionUpdate(BaseModel):
    titulo: Optional[str] = None
    fecha_revision: Optional[date] = None

    gerente_usuario_id: Optional[int] = None
    responsable_sst_usuario_id: Optional[int] = None

    periodo_evaluado: Optional[str] = None
    gerente: Optional[str] = None
    responsable_sst: Optional[str] = None
    participantes: Optional[str] = None

    objetivo: Optional[str] = None
    alcance: Optional[str] = None
    agenda: Optional[str] = None

    resumen_auditorias: Optional[str] = None
    resumen_indicadores: Optional[str] = None
    resumen_planes_mejora: Optional[str] = None
    resumen_accidentes: Optional[str] = None
    resumen_capacitaciones: Optional[str] = None
    resumen_cumplimiento_legal: Optional[str] = None

    conclusiones: Optional[str] = None
    decisiones: Optional[str] = None
    recomendaciones: Optional[str] = None

    estado: Optional[str] = None


class RevisionDireccionResponse(BaseModel):
    id: int
    empresa_id: int
    usuario_id: Optional[int] = None

    gerente_usuario_id: Optional[int] = None
    responsable_sst_usuario_id: Optional[int] = None

    codigo: str
    titulo: str
    fecha_revision: date
    periodo_evaluado: Optional[str] = None

    gerente: Optional[str] = None
    responsable_sst: Optional[str] = None
    participantes: Optional[str] = None

    objetivo: Optional[str] = None
    alcance: Optional[str] = None
    agenda: Optional[str] = None

    resumen_auditorias: Optional[str] = None
    resumen_indicadores: Optional[str] = None
    resumen_planes_mejora: Optional[str] = None
    resumen_accidentes: Optional[str] = None
    resumen_capacitaciones: Optional[str] = None
    resumen_cumplimiento_legal: Optional[str] = None

    conclusiones: Optional[str] = None
    decisiones: Optional[str] = None
    recomendaciones: Optional[str] = None

    total_compromisos: int
    compromisos_pendientes: int
    compromisos_cerrados: int
    porcentaje_cumplimiento: Decimal

    estado: str
    activo: bool
    
    bloqueado: bool = False

    fecha_bloqueo: Optional[datetime] = None

    bloqueado_por_usuario_id: Optional[int] = None

    fecha_aprobacion: Optional[datetime] = None

    aprobado_por_usuario_id: Optional[int] = None

    motivo_bloqueo: Optional[str] = None

    version_documental: Optional[str] = None

    hash_final_sha256: Optional[str] = None

    codigo_validacion_final: Optional[str] = None

    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    compromisos: List[RevisionDireccionCompromisoResponse] = []

    model_config = ConfigDict(from_attributes=True)


class RevisionDireccionDashboardResponse(BaseModel):
    total_revisiones: int
    borradores: int
    aprobadas: int
    cerradas: int

    total_compromisos: int
    compromisos_pendientes: int
    compromisos_cerrados: int
    porcentaje_cumplimiento_global: float
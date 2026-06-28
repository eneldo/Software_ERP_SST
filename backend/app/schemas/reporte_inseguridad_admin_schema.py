# ============================================================
# SCHEMAS GESTIÓN ADMINISTRATIVA REPORTES ANÓNIMOS SST
# ERP SST PRO
# FASE 1.1.25.6 — Evidencias Inteligentes Reportes SST
# Archivo: backend/app/schemas/reporte_inseguridad_admin_schema.py
# ============================================================

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.schemas.reporte_evidencia_schema import ReporteEvidenciaResponse

ESTADOS_REPORTE = {"REPORTADO", "ASIGNADO", "EN_PROCESO", "CERRADO", "ANULADO"}
PRIORIDADES_REPORTE = {"BAJA", "MEDIA", "ALTA", "CRITICA", "CRÍTICA"}
TIPOS_REPORTE = {"ACTO_INSEGURO", "CONDICION_INSEGURA", "INCIDENTE", "ACCIDENTE", "SUGERENCIA"}


def _upper_clean(value, default=None):
    if value is None:
        return default
    value = str(value).strip().upper()
    return value if value else default


class ReporteInseguridadAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: int
    codigo: str
    empresa_id: int
    sede_id: Optional[int] = None
    area_id: Optional[int] = None
    cargo_id: Optional[int] = None
    empleado_id: Optional[int] = None
    usuario_id: Optional[int] = None

    empresa_nombre: Optional[str] = None
    sede_nombre: Optional[str] = None
    area_nombre: Optional[str] = None
    cargo_nombre: Optional[str] = None
    empleado_nombre: Optional[str] = None

    tipo_reporte: str
    prioridad: str
    estado: str
    titulo: str
    descripcion: str
    ubicacion: Optional[str] = None
    responsable_asignado: Optional[str] = None
    accion_inmediata: Optional[str] = None
    observaciones: Optional[str] = None
    trazabilidad: Optional[str] = None

    archivo_url: Optional[str] = None
    archivo_nombre: Optional[str] = None
    archivo_mime_type: Optional[str] = None
    archivo_tamano_bytes: Optional[int] = None
    evidencias: list[ReporteEvidenciaResponse] = []
    total_evidencias: int = 0

    origen: Optional[str] = None
    genera_notificacion: bool = True
    convertido_a_inspeccion: bool = False
    inspeccion_id: Optional[int] = None
    capa_id: Optional[int] = None
    incidente_id: Optional[int] = None
    activo: bool = True

    fecha_reporte: Optional[datetime] = None
    fecha_cierre: Optional[datetime] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None


class ReporteInseguridadAdminUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    area_id: Optional[int] = Field(default=None, gt=0)
    prioridad: Optional[str] = Field(default=None, max_length=30)
    estado: Optional[str] = Field(default=None, max_length=40)
    responsable_asignado: Optional[str] = Field(default=None, max_length=255)
    accion_inmediata: Optional[str] = None
    observaciones: Optional[str] = None
    trazabilidad: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("prioridad")
    @classmethod
    def validar_prioridad(cls, value):
        if value is None:
            return value
        value = _upper_clean(value, "MEDIA")
        if value not in PRIORIDADES_REPORTE:
            raise ValueError("Prioridad no válida")
        return "CRITICA" if value == "CRÍTICA" else value

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value):
        if value is None:
            return value
        value = _upper_clean(value, "REPORTADO")
        if value not in ESTADOS_REPORTE:
            raise ValueError("Estado no válido")
        return value


class ReporteAsignacionRequest(BaseModel):
    responsable_asignado: Optional[str] = Field(default=None, max_length=255)
    responsable_empleado_id: Optional[int] = Field(default=None, gt=0)
    observaciones: Optional[str] = None


class ReporteCierreRequest(BaseModel):
    observaciones: Optional[str] = None
    accion_cierre: Optional[str] = None


class ReportesAnonimosDashboardResponse(BaseModel):
    total: int
    reportados: int
    asignados: int
    en_proceso: int
    cerrados: int
    anulados: int
    criticos: int
    altos: int
    medios: int
    bajos: int
    con_evidencia: int
    sin_evidencia: int = 0
    total_evidencias: int = 0
    evidencias_imagen: int = 0
    evidencias_video: int = 0
    evidencias_pdf: int = 0
    ahorro_evidencias_mb: float = 0
    pendientes: int
    sin_asignar: int = 0
    gestionados_inspeccion: int = 0
    gestionados_capa: int = 0
    por_tipo: dict[str, int]
    por_prioridad: dict[str, int]
    por_estado: dict[str, int]
    por_area: dict[str, int]
    por_responsable: dict[str, int] = {}
    por_categoria_ia: dict[str, int] = {}
    recomendaciones: list[str]


class ConvertirReporteResponse(BaseModel):
    ok: bool = True
    mensaje: str
    reporte_id: int
    destino_id: Optional[int] = None
    hallazgo_id: Optional[int] = None
    capa_id: Optional[int] = None


class ResponsableSSTResponse(BaseModel):
    id: int
    nombre: str
    documento: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    empresa_id: Optional[int] = None
    sede_id: Optional[int] = None
    area_id: Optional[int] = None
    cargo_id: Optional[int] = None
    empresa_nombre: Optional[str] = None
    sede_nombre: Optional[str] = None
    area_nombre: Optional[str] = None
    cargo_nombre: Optional[str] = None


class WorkflowReporteRequest(BaseModel):
    responsable: Optional[str] = None
    fecha_compromiso_dias: int = Field(default=15, ge=1, le=365)
    observaciones: Optional[str] = None


class MisCasosQueryResponse(BaseModel):
    total: int
    casos: list[ReporteInseguridadAdminResponse]

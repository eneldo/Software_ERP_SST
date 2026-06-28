# ============================================================
# SCHEMAS REPORTE INSEGURIDAD SST - ERP SST PRO
# FASE 1.1.25.6 — Evidencias Inteligentes Reportes SST
# Archivo: backend/app/schemas/reporte_inseguridad_schema.py
# ============================================================

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.schemas.reporte_evidencia_schema import ReporteEvidenciaResponse

TIPOS_REPORTE = {"ACTO_INSEGURO", "CONDICION_INSEGURA", "INCIDENTE", "ACCIDENTE", "SUGERENCIA"}
PRIORIDADES_REPORTE = {"BAJA", "MEDIA", "ALTA", "CRITICA"}
ESTADOS_REPORTE = {"REPORTADO", "ASIGNADO", "EN_PROCESO", "CERRADO", "ANULADO"}


def _upper_clean(value, default=None):
    if value is None:
        return default
    value = str(value).strip().upper()
    return value if value else default


class ReporteInseguridadBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    empresa_id: Optional[int] = Field(default=None, gt=0)
    sede_id: Optional[int] = Field(default=None, gt=0)
    area_id: Optional[int] = Field(default=None, gt=0)
    cargo_id: Optional[int] = Field(default=None, gt=0)
    empleado_id: Optional[int] = Field(default=None, gt=0)

    codigo: Optional[str] = Field(default=None, max_length=80)
    tipo_reporte: str = Field(default="CONDICION_INSEGURA", max_length=60)
    prioridad: str = Field(default="MEDIA", max_length=30)
    estado: str = Field(default="REPORTADO", max_length=40)

    titulo: str = Field(..., min_length=3, max_length=255)
    descripcion: str = Field(..., min_length=5, max_length=700)
    ubicacion: Optional[str] = Field(default=None, max_length=255)
    responsable_asignado: Optional[str] = Field(default=None, max_length=255)
    accion_inmediata: Optional[str] = None
    observaciones: Optional[str] = None
    origen: str = Field(default="PORTAL_EMPLEADO", max_length=80)
    genera_notificacion: bool = True
    activo: bool = True

    @field_validator("tipo_reporte")
    @classmethod
    def validar_tipo(cls, value):
        value = _upper_clean(value, "CONDICION_INSEGURA")
        if value not in TIPOS_REPORTE:
            raise ValueError("Tipo de reporte SST no válido")
        return value

    @field_validator("prioridad")
    @classmethod
    def validar_prioridad(cls, value):
        value = _upper_clean(value, "MEDIA")
        if value not in PRIORIDADES_REPORTE:
            raise ValueError("Prioridad de reporte SST no válida")
        return value

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value):
        value = _upper_clean(value, "REPORTADO")
        if value not in ESTADOS_REPORTE:
            raise ValueError("Estado de reporte SST no válido")
        return value


class ReporteInseguridadCreate(ReporteInseguridadBase):
    pass


class ReporteInseguridadUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    sede_id: Optional[int] = Field(default=None, gt=0)
    area_id: Optional[int] = Field(default=None, gt=0)
    cargo_id: Optional[int] = Field(default=None, gt=0)
    empleado_id: Optional[int] = Field(default=None, gt=0)
    tipo_reporte: Optional[str] = Field(default=None, max_length=60)
    prioridad: Optional[str] = Field(default=None, max_length=30)
    estado: Optional[str] = Field(default=None, max_length=40)
    titulo: Optional[str] = Field(default=None, min_length=3, max_length=255)
    descripcion: Optional[str] = Field(default=None, min_length=5, max_length=700)
    ubicacion: Optional[str] = Field(default=None, max_length=255)
    responsable_asignado: Optional[str] = Field(default=None, max_length=255)
    accion_inmediata: Optional[str] = None
    observaciones: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("tipo_reporte")
    @classmethod
    def validar_tipo(cls, value):
        if value is None:
            return value
        value = _upper_clean(value)
        if value not in TIPOS_REPORTE:
            raise ValueError("Tipo de reporte SST no válido")
        return value

    @field_validator("prioridad")
    @classmethod
    def validar_prioridad(cls, value):
        if value is None:
            return value
        value = _upper_clean(value)
        if value not in PRIORIDADES_REPORTE:
            raise ValueError("Prioridad de reporte SST no válida")
        return value

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value):
        if value is None:
            return value
        value = _upper_clean(value)
        if value not in ESTADOS_REPORTE:
            raise ValueError("Estado de reporte SST no válido")
        return value


class ReporteInseguridadEstadoUpdate(BaseModel):
    estado: str = Field(..., max_length=40)
    responsable_asignado: Optional[str] = Field(default=None, max_length=255)
    observaciones: Optional[str] = None

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value):
        value = _upper_clean(value)
        if value not in ESTADOS_REPORTE:
            raise ValueError("Estado de reporte SST no válido")
        return value


class ReporteInseguridadResponse(ReporteInseguridadBase):
    id: int
    usuario_id: Optional[int] = None
    empresa_id: int
    codigo: str

    archivo_url: Optional[str] = None
    archivo_nombre: Optional[str] = None
    archivo_mime_type: Optional[str] = None
    archivo_tamano_bytes: Optional[int] = None
    evidencias: list[ReporteEvidenciaResponse] = []
    total_evidencias: int = 0

    convertido_a_inspeccion: bool = False
    inspeccion_id: Optional[int] = None
    capa_id: Optional[int] = None
    incidente_id: Optional[int] = None

    fecha_reporte: Optional[datetime] = None
    fecha_cierre: Optional[datetime] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    empresa_nombre: Optional[str] = None
    sede_nombre: Optional[str] = None
    area_nombre: Optional[str] = None
    cargo_nombre: Optional[str] = None
    empleado_nombre: Optional[str] = None
    empleado_documento: Optional[str] = None
    empleado_correo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class PortalEmpleadoDashboardResponse(BaseModel):
    empleado: dict
    kpis: dict
    reportes_recientes: list[ReporteInseguridadResponse]
    alertas: list[str]


class PortalEmpleadoResumenResponse(BaseModel):
    capacitaciones: list[dict]
    epp: list[dict]
    examenes: list[dict]
    reportes: list[ReporteInseguridadResponse]

# ============================================================
# SCHEMAS SEGUIMIENTOS / PLANES DE ACCIÓN - INSPECCIONES SST
# FASE 1.1.8.6 — PLANES DE ACCIÓN Y SEGUIMIENTO ENTERPRISE
# Archivo: backend/app/schemas/inspeccion_seguimiento_schema.py
# ============================================================

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


ESTADOS_SEGUIMIENTO = {"PENDIENTE", "EN_PROCESO", "VERIFICACION", "CERRADO", "VENCIDO", "ANULADO"}
RESULTADOS_SEGUIMIENTO = {"EN_EJECUCION", "EFECTIVO", "NO_EFECTIVO", "REQUIERE_REPROGRAMACION", "CERRADO"}
TIPOS_ACCION = {"CORRECTIVA", "PREVENTIVA", "MEJORA", "INMEDIATA", "VERIFICACION"}


def _upper_clean(value, default=None):
    if value is None:
        return default
    value = str(value).strip().upper()
    return value if value else default


class SeguimientoHallazgoBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    hallazgo_id: int = Field(..., gt=0)
    tipo_accion: str = "CORRECTIVA"
    responsable: Optional[str] = Field(default=None, max_length=255)
    fecha_seguimiento: Optional[date] = None
    fecha_proximo_seguimiento: Optional[date] = None
    estado: str = "EN_PROCESO"
    resultado: str = "EN_EJECUCION"
    comentario: str = Field(..., min_length=3)
    porcentaje_avance: int = Field(default=0, ge=0, le=100)
    requiere_evidencia: bool = True
    observaciones: Optional[str] = None
    activo: bool = True

    @field_validator("tipo_accion", "estado", "resultado")
    @classmethod
    def upper_values(cls, value):
        return _upper_clean(value)

    @field_validator("tipo_accion")
    @classmethod
    def validar_tipo_accion(cls, value):
        value = _upper_clean(value, "CORRECTIVA")
        if value not in TIPOS_ACCION:
            raise ValueError("Tipo de acción no válido")
        return value

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value):
        value = _upper_clean(value, "EN_PROCESO")
        if value not in ESTADOS_SEGUIMIENTO:
            raise ValueError("Estado de seguimiento no válido")
        return value

    @field_validator("resultado")
    @classmethod
    def validar_resultado(cls, value):
        value = _upper_clean(value, "EN_EJECUCION")
        if value not in RESULTADOS_SEGUIMIENTO:
            raise ValueError("Resultado de seguimiento no válido")
        return value


class SeguimientoHallazgoCreate(SeguimientoHallazgoBase):
    pass


class SeguimientoHallazgoUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    tipo_accion: Optional[str] = None
    responsable: Optional[str] = Field(default=None, max_length=255)
    fecha_seguimiento: Optional[date] = None
    fecha_proximo_seguimiento: Optional[date] = None
    estado: Optional[str] = None
    resultado: Optional[str] = None
    comentario: Optional[str] = Field(default=None, min_length=3)
    porcentaje_avance: Optional[int] = Field(default=None, ge=0, le=100)
    requiere_evidencia: Optional[bool] = None
    observaciones: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("tipo_accion", "estado", "resultado")
    @classmethod
    def upper_values(cls, value):
        return _upper_clean(value) if value is not None else value


class SeguimientoHallazgoResponse(BaseModel):
    id: int
    hallazgo_id: int
    usuario_id: Optional[int] = None
    tipo_accion: str = "CORRECTIVA"
    responsable: Optional[str] = None
    fecha_seguimiento: Optional[date] = None
    fecha_proximo_seguimiento: Optional[date] = None
    estado: str = "EN_PROCESO"
    resultado: str = "EN_EJECUCION"
    comentario: str
    porcentaje_avance: int = 0
    requiere_evidencia: bool = True
    observaciones: Optional[str] = None
    fecha_registro: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    activo: bool = True
    total_evidencias: int = 0

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class CierreHallazgoRequest(BaseModel):
    observacion: Optional[str] = None
    forzar_cierre: bool = False


class SeguimientoDashboardResponse(BaseModel):
    kpis: dict
    alertas: dict
    recomendaciones: list[str]

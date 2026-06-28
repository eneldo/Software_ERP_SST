# ============================================================
# SCHEMAS REPORTE ANÓNIMO SST PÚBLICO - ERP SST PRO
# FASE 1.1.25.3 — Versión simplificada sin Empresa/Sede en Frontend
# Archivo: backend/app/schemas/reporte_anonimo_sst_schema.py
# ============================================================

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

TIPOS_REPORTE = {"ACTO_INSEGURO", "CONDICION_INSEGURA", "INCIDENTE", "ACCIDENTE", "SUGERENCIA"}
PRIORIDADES = {"BAJA", "MEDIA", "ALTA", "CRITICA"}


def _upper_clean(value, default=None):
    if value is None:
        return default
    value = str(value).strip().upper()
    return value if value else default


class ReporteAnonimoSSTCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    area_id: Optional[int] = Field(default=None, gt=0)
    tipo: str = Field(default="CONDICION_INSEGURA")
    prioridad: str = Field(default="MEDIA")
    ubicacion: str = Field(..., min_length=3, max_length=255)
    titulo: str = Field(..., min_length=3, max_length=255)
    descripcion: str = Field(..., min_length=10)
    accion_inmediata: Optional[str] = None
    observaciones: Optional[str] = None
    nombre_reportante: Optional[str] = Field(default=None, max_length=255)
    telefono_reportante: Optional[str] = Field(default=None, max_length=80)
    correo_reportante: Optional[str] = Field(default=None, max_length=255)

    @field_validator("tipo")
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
        if value not in PRIORIDADES:
            raise ValueError("Prioridad no válida")
        return value


class ReporteAnonimoSSTResponse(BaseModel):
    id: int
    codigo: str
    empresa_id: int
    sede_id: Optional[int] = None
    area_id: Optional[int] = None
    empleado_id: Optional[int] = None
    tipo: str
    prioridad: str
    estado: str
    titulo: str
    descripcion: str
    ubicacion: Optional[str] = None
    accion_inmediata: Optional[str] = None
    observaciones: Optional[str] = None
    anonimo: bool = True
    nombre_reportante: Optional[str] = None
    telefono_reportante: Optional[str] = None
    correo_reportante: Optional[str] = None
    archivo_url: Optional[str] = None
    fecha_reporte: Optional[datetime] = None
    fecha_creacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class ReporteAnonimoSSTPublicResponse(BaseModel):
    ok: bool = True
    mensaje: str
    codigo: str
    reporte_id: int

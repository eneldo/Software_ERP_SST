# ============================================================
# SCHEMAS EXAMEN MÉDICO SST - ERP SST PRO
# FASE 1.1.6.1 — EXÁMENES MÉDICOS SST BASE
# Archivo: backend/app/schemas/examen_medico_schema.py
# ============================================================

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

import json


TIPOS_EXAMEN = {
    "INGRESO",
    "PERIODICO",
    "RETIRO",
    "POST_INCAPACIDAD",
    "RETORNO_LABORAL",
}

CONCEPTOS_MEDICOS = {
    "APTO",
    "APTO_CON_RESTRICCIONES",
    "NO_APTO",
}

ESTADOS_EXAMEN = {
    "VIGENTE",
    "PROXIMO_VENCER",
    "VENCIDO",
}


def _upper_clean(value):
    if value is None:
        return value
    return str(value).strip().upper()


class ExamenMedicoBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    empleado_id: int = Field(..., gt=0)
    tipo_examen: str = Field(..., max_length=50)
    fecha_examen: date
    fecha_vencimiento: Optional[date] = None
    concepto: str = Field(..., max_length=50)
    restricciones: Optional[str] = None
    observaciones: Optional[str] = None
    estado: Optional[str] = "VIGENTE"
    activo: bool = True
    medico_ocupacional: Optional[str] = Field(default=None, max_length=255)
    entidad_salud: Optional[str] = Field(default=None, max_length=255)
    examenes_aplicados: Optional[list[dict]] = None

    @field_validator("tipo_examen")
    @classmethod
    def validar_tipo_examen(cls, value):
        value = _upper_clean(value)
        if value not in TIPOS_EXAMEN:
            raise ValueError("Tipo de examen no válido")
        return value

    @field_validator("concepto")
    @classmethod
    def validar_concepto(cls, value):
        value = _upper_clean(value)
        if value not in CONCEPTOS_MEDICOS:
            raise ValueError("Concepto médico no válido")
        return value

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value):
        value = _upper_clean(value) or "VIGENTE"
        if value not in ESTADOS_EXAMEN:
            raise ValueError("Estado de examen no válido")
        return value


class ExamenMedicoCreate(ExamenMedicoBase):
    pass


class ExamenMedicoUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    empleado_id: Optional[int] = Field(default=None, gt=0)
    tipo_examen: Optional[str] = Field(default=None, max_length=50)
    fecha_examen: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    concepto: Optional[str] = Field(default=None, max_length=50)
    restricciones: Optional[str] = None
    observaciones: Optional[str] = None
    estado: Optional[str] = Field(default=None, max_length=30)
    activo: Optional[bool] = None
    medico_ocupacional: Optional[str] = Field(default=None, max_length=255)
    entidad_salud: Optional[str] = Field(default=None, max_length=255)
    examenes_aplicados: Optional[list[dict]] = None

    @field_validator("tipo_examen")
    @classmethod
    def validar_tipo_examen(cls, value):
        if value is None:
            return value
        value = _upper_clean(value)
        if value not in TIPOS_EXAMEN:
            raise ValueError("Tipo de examen no válido")
        return value

    @field_validator("concepto")
    @classmethod
    def validar_concepto(cls, value):
        if value is None:
            return value
        value = _upper_clean(value)
        if value not in CONCEPTOS_MEDICOS:
            raise ValueError("Concepto médico no válido")
        return value

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value):
        if value is None:
            return value
        value = _upper_clean(value)
        if value not in ESTADOS_EXAMEN:
            raise ValueError("Estado de examen no válido")
        return value


class ExamenMedicoResponse(ExamenMedicoBase):
    id: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    empleado_documento: Optional[str] = None
    empleado_nombre: Optional[str] = None
    empleado_correo: Optional[str] = None
    empresa_id: Optional[int] = None
    sede_id: Optional[int] = None
    area_id: Optional[int] = None
    cargo_id: Optional[int] = None
    empresa_nombre: Optional[str] = None
    sede_nombre: Optional[str] = None
    area_nombre: Optional[str] = None
    cargo_nombre: Optional[str] = None

    dias_vencimiento: Optional[int] = None

    @field_validator("examenes_aplicados", mode="before")
    @classmethod
    def parse_examenes_aplicados(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return None
        return value

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class ExamenMedicoDashboardResponse(BaseModel):
    kpis: dict
    charts: dict
    alertas: dict
    recomendaciones: list[str]

# ============================================================
# SCHEMAS CARGO - ERP SST PRO
# FASE 1.1.4.3 — EXPORTACIÓN PDF / EXCEL
# Archivo: backend/app/schemas/cargo_schema.py
# Mantiene campos oficiales y alias legacy del frontend.
# ============================================================

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.epp_schema import EPPCatalogoResponse


class CargoBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    empresa_id: int
    sede_id: Optional[int] = None
    area_id: Optional[int] = None

    nombre: str = Field(..., min_length=2, max_length=180)
    codigo_cargo: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_cargo: Optional[str] = "OPERATIVO"
    proceso_asociado: Optional[str] = None

    nivel_riesgo: Optional[str] = "MEDIO"
    exposicion: Optional[str] = None
    requiere_epp: bool = False
    epp_requerido: Optional[str] = None
    examenes_medicos: Optional[str] = None
    requiere_vigilancia_medica: bool = False
    capacitaciones_requeridas: Optional[str] = None
    perfil_sst: Optional[str] = None
    competencias: Optional[str] = None

    numero_empleados: int = 0
    activo: bool = True

    # Alias compatibles con versiones previas del frontend.
    codigo: Optional[str] = None
    tipo: Optional[str] = None
    proceso: Optional[str] = None
    empleados_asociados: Optional[int] = None
    requiere_examen_medico: Optional[bool] = None
    requiere_capacitacion: Optional[bool] = None
    funciones: Optional[str] = None
    riesgos_asociados: Optional[str] = None
    observaciones: Optional[str] = None


class CargoCreate(CargoBase):
    pass


class CargoUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    empresa_id: Optional[int] = None
    sede_id: Optional[int] = None
    area_id: Optional[int] = None

    nombre: Optional[str] = None
    codigo_cargo: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_cargo: Optional[str] = None
    proceso_asociado: Optional[str] = None

    nivel_riesgo: Optional[str] = None
    exposicion: Optional[str] = None
    requiere_epp: Optional[bool] = None
    epp_requerido: Optional[str] = None
    examenes_medicos: Optional[str] = None
    requiere_vigilancia_medica: Optional[bool] = None
    capacitaciones_requeridas: Optional[str] = None
    perfil_sst: Optional[str] = None
    competencias: Optional[str] = None

    numero_empleados: Optional[int] = None
    activo: Optional[bool] = None

    # Alias legacy frontend.
    codigo: Optional[str] = None
    tipo: Optional[str] = None
    proceso: Optional[str] = None
    empleados_asociados: Optional[int] = None
    requiere_examen_medico: Optional[bool] = None
    requiere_capacitacion: Optional[bool] = None
    funciones: Optional[str] = None
    riesgos_asociados: Optional[str] = None
    observaciones: Optional[str] = None


class CargoResponse(CargoBase):
    id: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    empresa_nombre: Optional[str] = None
    sede_nombre: Optional[str] = None
    area_nombre: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class CargoEPPAsignacionUpdate(BaseModel):
    epp_ids: list[int] = Field(default_factory=list)

    @field_validator("epp_ids")
    @classmethod
    def validar_epp_ids(cls, values: list[int]) -> list[int]:
        if any(value <= 0 for value in values):
            raise ValueError("Los identificadores de EPP deben ser positivos")
        return list(dict.fromkeys(values))


class CargoEPPAsignacionResponse(BaseModel):
    cargo_id: int
    empresa_id: int
    epp_ids: list[int] = Field(default_factory=list)
    epps: list[EPPCatalogoResponse] = Field(default_factory=list)


class CargoDashboardResponse(BaseModel):
    total_cargos: int = 0
    activos: int = 0
    inactivos: int = 0
    alto_critico: int = 0
    riesgo_alto_critico: int = 0
    requieren_epp: int = 0
    requieren_examen_medico: int = 0
    requieren_capacitacion: int = 0
    empleados_asociados: int = 0
    sin_area: int = 0
    sin_codigo: int = 0
    sin_examenes: int = 0
    sin_capacitaciones: int = 0
    indice_gestion: int = 0
    cargos_por_riesgo: list[dict] = []
    distribucion_riesgo: list[dict] = []
    cargos_por_tipo: list[dict] = []
    distribucion_tipo: list[dict] = []
    cargos_por_area: list[dict] = []
    cargo_prioritario: Optional[dict] = None
    cargos_prioritarios: list[dict] = []
    recomendaciones: list[str] = []

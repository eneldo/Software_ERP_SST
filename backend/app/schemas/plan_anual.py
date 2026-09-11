from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from pydantic import ConfigDict, BaseModel, Field


class PlanAnualCabeceraCreate(BaseModel):
    empresa_id: int
    vigencia: str = Field(..., pattern=r"^\d{4}$")
    alcance: Optional[str] = None
    objetivo_general: Optional[str] = None
    meta_general: Optional[str] = None
    representante_legal_nombre: Optional[str] = None
    representante_legal_cargo: Optional[str] = None
    responsable_sst_nombre: Optional[str] = None
    responsable_sst_cargo: Optional[str] = None


class PlanAnualCabeceraUpdate(BaseModel):
    vigencia: Optional[str] = Field(default=None, pattern=r"^\d{4}$")
    alcance: Optional[str] = None
    objetivo_general: Optional[str] = None
    meta_general: Optional[str] = None
    representante_legal_nombre: Optional[str] = None
    representante_legal_cargo: Optional[str] = None
    responsable_sst_nombre: Optional[str] = None
    responsable_sst_cargo: Optional[str] = None
    activo: Optional[bool] = None


class PlanAnualCabeceraResponse(BaseModel):
    id: int
    empresa_id: int
    usuario_id: Optional[int] = None
    vigencia: str
    alcance: Optional[str] = None
    objetivo_general: Optional[str] = None
    meta_general: Optional[str] = None
    representante_legal_nombre: Optional[str] = None
    representante_legal_cargo: Optional[str] = None
    responsable_sst_nombre: Optional[str] = None
    responsable_sst_cargo: Optional[str] = None
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    actividades_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class PlanAnualCreate(BaseModel):
    plan_anual_cabecera_id: int
    codigo: str = "PA-SST-001"
    actividad: str
    objetivo: Optional[str] = None
    responsable: Optional[str] = None
    recurso_humano: Optional[str] = None
    recurso_fisico: Optional[str] = None
    recurso_financiero: Optional[str] = None
    presupuesto: Optional[Decimal] = Decimal("0.00")
    indicador: Optional[str] = None
    meta: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: str = "PLANIFICADO"
    porcentaje_avance: int = Field(default=0, ge=0, le=100)
    evidencia: Optional[str] = None
    observaciones: Optional[str] = None
    archivo_id: Optional[int] = None


class PlanAnualUpdate(BaseModel):
    codigo: Optional[str] = None
    actividad: Optional[str] = None
    objetivo: Optional[str] = None
    responsable: Optional[str] = None
    recurso_humano: Optional[str] = None
    recurso_fisico: Optional[str] = None
    recurso_financiero: Optional[str] = None
    presupuesto: Optional[Decimal] = None
    indicador: Optional[str] = None
    meta: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Optional[str] = None
    porcentaje_avance: Optional[int] = Field(default=None, ge=0, le=100)
    evidencia: Optional[str] = None
    observaciones: Optional[str] = None
    archivo_id: Optional[int] = None
    activo: Optional[bool] = None


class PlanAnualResponse(BaseModel):
    id: int
    empresa_id: int
    usuario_id: Optional[int] = None
    archivo_id: Optional[int] = None
    plan_anual_cabecera_id: Optional[int] = None
    codigo: str
    actividad: str
    objetivo: Optional[str] = None
    responsable: Optional[str] = None
    recurso_humano: Optional[str] = None
    recurso_fisico: Optional[str] = None
    recurso_financiero: Optional[str] = None
    presupuesto: Optional[Decimal] = None
    indicador: Optional[str] = None
    meta: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: str
    porcentaje_avance: int
    evidencia: Optional[str] = None
    observaciones: Optional[str] = None
    archivo_url: Optional[str] = None
    archivo_nombre: Optional[str] = None
    archivo_extension: Optional[str] = None
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PlanAnualResumenResponse(BaseModel):
    total: int
    planificados: int
    en_proceso: int
    ejecutados: int
    cancelados: int
    vencidos: int
    cumplimiento: int
    presupuesto_total: float


class PlanAnualCompletoResponse(BaseModel):
    cabecera: PlanAnualCabeceraResponse
    actividades: List[PlanAnualResponse]
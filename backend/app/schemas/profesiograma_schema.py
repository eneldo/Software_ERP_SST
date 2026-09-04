from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# ── Tipos de Evaluación Médica ──────────────────────────────

class TipoEvaluacionMedicaBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


class TipoEvaluacionMedicaCreate(TipoEvaluacionMedicaBase):
    pass


class TipoEvaluacionMedicaUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    codigo: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class TipoEvaluacionMedicaResponse(TipoEvaluacionMedicaBase):
    id: int
    fecha_creacion: Optional[datetime] = None


# ── Catálogo de Exámenes ────────────────────────────────────

class ExamenEvaluacionCatalogoBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


class ExamenEvaluacionCatalogoCreate(ExamenEvaluacionCatalogoBase):
    pass


class ExamenEvaluacionCatalogoUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    codigo: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class ExamenEvaluacionCatalogoResponse(ExamenEvaluacionCatalogoBase):
    id: int
    fecha_creacion: Optional[datetime] = None


# ── Profesiograma ───────────────────────────────────────────

class ProfesiogramaEvaluacionInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    tipo_evaluacion_id: int
    examenes_requeridos: Optional[str] = None


class ProfesiogramaEvaluacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo_evaluacion_id: int
    examenes_requeridos: Optional[str] = None
    activo: bool = True
    tipo_evaluacion_codigo: Optional[str] = None
    tipo_evaluacion_nombre: Optional[str] = None


class ProfesiogramaCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    cargo_id: int
    empresa_id: int
    riesgos_asociados: Optional[str] = None
    evaluaciones: list[ProfesiogramaEvaluacionInput] = []


class ProfesiogramaUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    riesgos_asociados: Optional[str] = None
    activo: Optional[bool] = None
    evaluaciones: Optional[list[ProfesiogramaEvaluacionInput]] = None


class ProfesiogramaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cargo_id: int
    empresa_id: int
    riesgos_asociados: Optional[str] = None
    activo: bool = True
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    cargo_nombre: Optional[str] = None
    empresa_nombre: Optional[str] = None
    evaluaciones: list[ProfesiogramaEvaluacionResponse] = []

# ============================================================
# SCHEMAS: EVALUACIÓN PSICOSOCIAL SST
# ============================================================

from datetime import datetime
from pydantic import BaseModel, Field


class FactorPsicosocialCreate(BaseModel):
    factor: str
    dominio: str | None = None
    puntuacion: float = Field(..., ge=1.0, le=5.0)
    nivel_riesgo: str | None = None
    observacion: str | None = None


class FactorPsicosocialResponse(BaseModel):
    id: int
    factor: str
    dominio: str | None
    puntuacion: float | None
    nivel_riesgo: str | None
    observacion: str | None

    class Config:
        from_attributes = True


class EvaluacionPsicosocialCreate(BaseModel):
    empleado_id: int
    fecha_evaluacion: datetime | None = None
    periodo: str | None = None
    evaluador: str | None = None
    conclusiones: str | None = None
    recomendaciones: str | None = None
    factores: list[FactorPsicosocialCreate] = []


class EvaluacionPsicosocialUpdate(BaseModel):
    fecha_evaluacion: datetime | None = None
    periodo: str | None = None
    evaluador: str | None = None
    puntaje_total: float | None = None
    nivel_riesgo: str | None = None
    conclusiones: str | None = None
    recomendaciones: str | None = None


class EvaluacionPsicosocialResponse(BaseModel):
    id: int
    empresa_id: int
    empleado_id: int
    fecha_evaluacion: datetime
    periodo: str | None
    evaluador: str | None
    puntaje_total: float | None
    nivel_riesgo: str | None
    conclusiones: str | None
    recomendaciones: str | None
    activo: bool
    fecha_creacion: datetime
    factores: list[FactorPsicosocialResponse] = []

    class Config:
        from_attributes = True


class EvaluacionPsicosocialList(BaseModel):
    id: int
    empleado_id: int
    fecha_evaluacion: datetime
    periodo: str | None
    nivel_riesgo: str | None
    activo: bool

    class Config:
        from_attributes = True

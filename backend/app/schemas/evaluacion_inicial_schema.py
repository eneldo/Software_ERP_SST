# ============================================================
# SCHEMAS EVALUACIÓN INICIAL SST
# FASE 2.3.2A - HARDENING EVIDENCIAS
# ============================================================

from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel


class EvaluacionInicialItemCreate(BaseModel):
    estandar: str
    numeral: Optional[str] = None
    criterio: str
    respuesta: str = "NO_CUMPLE"
    puntaje: int = 0
    evidencia: Optional[str] = None
    observaciones: Optional[str] = None
    responsable: Optional[str] = None
    archivo_id: Optional[int] = None


class EvaluacionInicialItemUpdate(BaseModel):
    estandar: Optional[str] = None
    criterio: Optional[str] = None
    respuesta: Optional[str] = None
    puntaje: Optional[int] = None
    evidencia: Optional[str] = None
    observaciones: Optional[str] = None
    responsable: Optional[str] = None
    archivo_id: Optional[int] = None
    activo: Optional[bool] = None


class EvaluacionInicialRespuestaMasiva(BaseModel):
    item_id: int
    respuesta: Optional[str] = None
    puntaje: Optional[int] = None
    evidencia: Optional[str] = None
    observaciones: Optional[str] = None
    responsable: Optional[str] = None


class EvaluacionInicialItemResponse(BaseModel):
    id: int
    evaluacion_id: int
    archivo_id: Optional[int] = None

    estandar: str
    numeral: Optional[str] = None
    criterio: str

    respuesta: str
    puntaje: int

    evidencia: Optional[str] = None
    observaciones: Optional[str] = None
    responsable: Optional[str] = None

    archivo_url: Optional[str] = None
    archivo_nombre: Optional[str] = None
    archivo_extension: Optional[str] = None

    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class EvaluacionInicialCreate(BaseModel):
    empresa_id: int
    codigo: str = "EVAL-SST-001"
    nombre: str = "Evaluación Inicial SG-SST"
    fecha_evaluacion: Optional[date] = None
    responsable: Optional[str] = None
    observaciones_generales: Optional[str] = None
    items: Optional[List[EvaluacionInicialItemCreate]] = None


class EvaluacionInicialUpdate(BaseModel):
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    fecha_evaluacion: Optional[date] = None
    responsable: Optional[str] = None
    estado: Optional[str] = None
    observaciones_generales: Optional[str] = None
    activo: Optional[bool] = None


class EvaluacionInicialResponse(BaseModel):
    id: int
    empresa_id: int
    usuario_id: Optional[int] = None

    codigo: str
    nombre: str
    fecha_evaluacion: Optional[date] = None
    responsable: Optional[str] = None

    total_items: int
    items_cumplen: int
    items_no_cumplen: int
    items_no_aplican: int
    porcentaje_cumplimiento: int
    nivel: str

    estado: str
    observaciones_generales: Optional[str] = None
    activo: bool

    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    items: List[EvaluacionInicialItemResponse] = []

    class Config:
        from_attributes = True

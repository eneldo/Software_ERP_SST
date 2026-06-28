from pydantic import BaseModel
from typing import Optional
from datetime import date


class ObjetivoSSTCreate(BaseModel):
    empresa_id: int
    objetivo: str
    meta: str
    indicador: str
    responsable: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    cumplimiento: int = 0
    estado: str = "PLANIFICADO"
    observaciones: Optional[str] = None


class ObjetivoSSTUpdate(BaseModel):
    objetivo: Optional[str] = None
    meta: Optional[str] = None
    indicador: Optional[str] = None
    responsable: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    cumplimiento: Optional[int] = None
    estado: Optional[str] = None
    observaciones: Optional[str] = None
    activo: Optional[bool] = None


class ObjetivoSSTResponse(ObjetivoSSTCreate):
    id: int

    class Config:
        from_attributes = True
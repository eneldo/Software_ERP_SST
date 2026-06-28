from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PlanMejoramientoSeguimientoCreate(BaseModel):
    observacion: str
    recomendacion: Optional[str] = None

    tipo_seguimiento: str = "SEGUIMIENTO"

    estado_nuevo: Optional[str] = None
    porcentaje_avance_nuevo: Optional[int] = None

    fecha_seguimiento: Optional[date] = None
    proxima_fecha: Optional[date] = None


class PlanMejoramientoSeguimientoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    plan_id: int
    empresa_id: int
    usuario_id: Optional[int]

    fecha_seguimiento: Optional[date]

    tipo_seguimiento: str

    estado_anterior: Optional[str]
    estado_nuevo: Optional[str]

    porcentaje_avance_anterior: int
    porcentaje_avance_nuevo: int

    observacion: str
    recomendacion: Optional[str]
    proxima_fecha: Optional[date]

    activo: bool

    fecha_creacion: Optional[datetime]
    fecha_actualizacion: Optional[datetime]
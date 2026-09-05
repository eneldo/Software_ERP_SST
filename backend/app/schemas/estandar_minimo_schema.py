# ============================================================
# SCHEMAS ESTANDARES MINIMOS CRITERIOS
# H-017: CRUD + Historial estandares
# ============================================================

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class EstandarMinimoCriterioCreate(BaseModel):
    tipo_estandares: str = "7"
    estandar: str
    numeral: str
    criterio: str
    puntaje: int = 1
    version_norma: str = "0312-2019"


class EstandarMinimoCriterioUpdate(BaseModel):
    tipo_estandares: Optional[str] = None
    estandar: Optional[str] = None
    numeral: Optional[str] = None
    criterio: Optional[str] = None
    puntaje: Optional[int] = None
    version_norma: Optional[str] = None
    activo: Optional[bool] = None


class EstandarMinimoCriterioResponse(BaseModel):
    id: int
    tipo_estandares: str
    estandar: str
    numeral: str
    criterio: str
    puntaje: int
    version_norma: str
    activo: bool
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class EstandarMinimoHistorialResponse(BaseModel):
    id: int
    estandar_criterio_id: int
    tipo_cambio: str
    descripcion_cambio: str
    valor_anterior: Optional[str] = None
    valor_nuevo: Optional[str] = None
    usuario_id: Optional[int] = None
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True

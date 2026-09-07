# ============================================================
# SCHEMAS MATRIZ IPER - GTC 45
# ============================================================

from typing import Optional, List
from datetime import datetime
from pydantic import ConfigDict,  BaseModel, field_validator


def _empty_str_to_none(cls, v):
    if isinstance(v, str) and v.strip() == "":
        return None
    return v


class MatrizIPERCreate(BaseModel):
    empresa_id: int
    proceso: str
    zona_lugar: Optional[str] = None
    actividades: Optional[str] = None
    tareas: Optional[str] = None
    rutinaria: str = "SI"
    clasificacion_peligro: str
    descripcion_peligro: str
    riesgo: Optional[str] = None
    efectos_posibles: str
    fuente: Optional[str] = None
    medio: Optional[str] = None
    individuo: Optional[str] = None
    nd: int = 0
    ne: int = 1
    nc: int = 10
    np: int = 0
    interpretacion_np: Optional[str] = None
    nr: int = 0
    interpretacion_nr: Optional[str] = None
    nivel_riesgo: Optional[str] = None
    aceptabilidad: Optional[str] = None
    expuestos_hombres: int = 0
    expuestos_mujeres: int = 0
    expuestos_gestantes: int = 0
    peor_consecuencia: Optional[str] = None
    eliminacion: Optional[str] = None
    control_ingenieria: Optional[str] = None
    sustitucion: Optional[str] = None
    senalizacion_admin: Optional[str] = None
    epp: Optional[str] = None
    responsable: Optional[str] = None
    fecha_proyectada: Optional[datetime] = None
    fecha_ejecucion: Optional[datetime] = None
    evidencias: Optional[str] = None
    realizado: Optional[str] = "NO"

    @field_validator("fecha_proyectada", "fecha_ejecucion", mode="before")
    @classmethod
    def empty_to_none(cls, v):
        return _empty_str_to_none(cls, v)


class MatrizIPERUpdate(BaseModel):
    proceso: Optional[str] = None
    zona_lugar: Optional[str] = None
    actividades: Optional[str] = None
    tareas: Optional[str] = None
    rutinaria: Optional[str] = None
    clasificacion_peligro: Optional[str] = None
    descripcion_peligro: Optional[str] = None
    riesgo: Optional[str] = None
    efectos_posibles: Optional[str] = None
    fuente: Optional[str] = None
    medio: Optional[str] = None
    individuo: Optional[str] = None
    nd: Optional[int] = None
    ne: Optional[int] = None
    nc: Optional[int] = None
    np: Optional[int] = None
    interpretacion_np: Optional[str] = None
    nr: Optional[int] = None
    interpretacion_nr: Optional[str] = None
    nivel_riesgo: Optional[str] = None
    aceptabilidad: Optional[str] = None
    expuestos_hombres: Optional[int] = None
    expuestos_mujeres: Optional[int] = None
    expuestos_gestantes: Optional[int] = None
    peor_consecuencia: Optional[str] = None
    eliminacion: Optional[str] = None
    control_ingenieria: Optional[str] = None
    sustitucion: Optional[str] = None
    senalizacion_admin: Optional[str] = None
    epp: Optional[str] = None
    responsable: Optional[str] = None
    fecha_proyectada: Optional[datetime] = None
    fecha_ejecucion: Optional[datetime] = None
    evidencias: Optional[str] = None
    realizado: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("fecha_proyectada", "fecha_ejecucion", mode="before")
    @classmethod
    def empty_to_none(cls, v):
        return _empty_str_to_none(cls, v)


class MatrizIPERResponse(BaseModel):
    id: int
    empresa_id: int
    usuario_id: Optional[int] = None

    proceso: str
    zona_lugar: Optional[str] = None
    actividades: Optional[str] = None
    tareas: Optional[str] = None
    rutinaria: str

    clasificacion_peligro: str
    descripcion_peligro: str
    riesgo: Optional[str] = None
    efectos_posibles: str

    fuente: Optional[str] = None
    medio: Optional[str] = None
    individuo: Optional[str] = None

    nd: int
    ne: int
    np: int
    interpretacion_np: Optional[str] = None
    nc: int
    nr: int
    interpretacion_nr: Optional[str] = None
    nivel_riesgo: Optional[str] = None
    aceptabilidad: Optional[str] = None

    expuestos_hombres: int
    expuestos_mujeres: int
    expuestos_gestantes: int
    peor_consecuencia: Optional[str] = None

    eliminacion: Optional[str] = None
    control_ingenieria: Optional[str] = None
    sustitucion: Optional[str] = None
    senalizacion_admin: Optional[str] = None
    epp: Optional[str] = None
    responsable: Optional[str] = None

    fecha_proyectada: Optional[datetime] = None
    fecha_ejecucion: Optional[datetime] = None
    evidencias: Optional[str] = None
    realizado: Optional[str] = None

    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MatrizIPERDashboardResponse(BaseModel):
    total: int
    por_clasificacion: list = []
    por_aceptabilidad: list = []
    por_nr: list = []
    expuestos_total: int = 0

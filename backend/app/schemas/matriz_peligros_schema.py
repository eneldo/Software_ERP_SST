from typing import Optional
from datetime import date, datetime
from pydantic import ConfigDict,  BaseModel


class MatrizPeligrosCreate(BaseModel):
    empresa_id: int
    codigo: str = "MP-SST-001"

    proceso: str
    actividad: str
    tarea: Optional[str] = None

    peligro: str
    clasificacion_peligro: str

    efectos_posibles: Optional[str] = None

    controles_fuente: Optional[str] = None
    controles_medio: Optional[str] = None
    controles_individuo: Optional[str] = None

    probabilidad: int = 1
    consecuencia: int = 1

    medidas_intervencion: Optional[str] = None
    responsable: Optional[str] = None

    fecha_revision: Optional[date] = None
    fecha_vencimiento: Optional[date] = None

    estado: str = "PENDIENTE"
    evidencia: Optional[str] = None
    observaciones: Optional[str] = None
    archivo_id: Optional[int] = None


class MatrizPeligrosUpdate(BaseModel):
    codigo: Optional[str] = None

    proceso: Optional[str] = None
    actividad: Optional[str] = None
    tarea: Optional[str] = None

    peligro: Optional[str] = None
    clasificacion_peligro: Optional[str] = None

    efectos_posibles: Optional[str] = None

    controles_fuente: Optional[str] = None
    controles_medio: Optional[str] = None
    controles_individuo: Optional[str] = None

    probabilidad: Optional[int] = None
    consecuencia: Optional[int] = None

    medidas_intervencion: Optional[str] = None
    responsable: Optional[str] = None

    fecha_revision: Optional[date] = None
    fecha_vencimiento: Optional[date] = None

    estado: Optional[str] = None
    evidencia: Optional[str] = None
    observaciones: Optional[str] = None
    archivo_id: Optional[int] = None
    activo: Optional[bool] = None


class MatrizPeligrosResponse(BaseModel):
    id: int
    empresa_id: int
    usuario_id: Optional[int] = None
    archivo_id: Optional[int] = None

    codigo: str
    proceso: str
    actividad: str
    tarea: Optional[str] = None

    peligro: str
    clasificacion_peligro: str

    efectos_posibles: Optional[str] = None

    controles_fuente: Optional[str] = None
    controles_medio: Optional[str] = None
    controles_individuo: Optional[str] = None

    probabilidad: int
    consecuencia: int
    nivel_riesgo: int

    interpretacion_riesgo: str
    aceptabilidad: str

    medidas_intervencion: Optional[str] = None
    responsable: Optional[str] = None

    fecha_revision: Optional[date] = None
    fecha_vencimiento: Optional[date] = None

    estado: str
    evidencia: Optional[str] = None
    observaciones: Optional[str] = None

    archivo_url: Optional[str] = None
    archivo_nombre: Optional[str] = None
    archivo_extension: Optional[str] = None

    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MatrizPeligrosResumenResponse(BaseModel):
    total: int
    bajos: int
    medios: int
    altos: int
    criticos: int
    pendientes: int
    porcentaje_criticos: int
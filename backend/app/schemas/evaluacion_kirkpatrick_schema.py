# ============================================================
# SCHEMAS EVALUACIÓN KIRKPATRICK SST
# ============================================================

from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import ConfigDict,  BaseModel, Field


class EvaluacionKirkpatrickCreate(BaseModel):
    empresa_id: int
    capacitacion_id: int
    empleado_id: Optional[int] = None

    nivel1_satisfaccion: Optional[int] = Field(default=None, ge=1, le=5)
    nivel1_comentario: Optional[str] = None

    nivel2_puntuacion_pre: Optional[Decimal] = None
    nivel2_puntuacion_post: Optional[Decimal] = None
    nivel2_aprobado: bool = False

    nivel3_observacion_30d: Optional[str] = None
    nivel3_observacion_60d: Optional[str] = None
    nivel3_observacion_90d: Optional[str] = None
    nivel3_aplicacion_pct: Optional[Decimal] = Field(default=None, ge=0, le=100)

    nivel4_indicador: Optional[str] = None
    nivel4_valor_antes: Optional[Decimal] = None
    nivel4_valor_despues: Optional[Decimal] = None
    nivel4_impacto: Optional[str] = None

    responsable_seguimiento: Optional[str] = None
    estado: str = "PENDIENTE"


class EvaluacionKirkpatrickUpdate(BaseModel):
    nivel1_satisfaccion: Optional[int] = Field(default=None, ge=1, le=5)
    nivel1_comentario: Optional[str] = None

    nivel2_puntuacion_pre: Optional[Decimal] = None
    nivel2_puntuacion_post: Optional[Decimal] = None
    nivel2_aprobado: Optional[bool] = None

    nivel3_observacion_30d: Optional[str] = None
    nivel3_observacion_60d: Optional[str] = None
    nivel3_observacion_90d: Optional[str] = None
    nivel3_aplicacion_pct: Optional[Decimal] = Field(default=None, ge=0, le=100)

    nivel4_indicador: Optional[str] = None
    nivel4_valor_antes: Optional[Decimal] = None
    nivel4_valor_despues: Optional[Decimal] = None
    nivel4_impacto: Optional[str] = None

    responsable_seguimiento: Optional[str] = None
    estado: Optional[str] = None
    activo: Optional[bool] = None


class EvaluacionKirkpatrickResponse(BaseModel):
    id: int
    empresa_id: int
    capacitacion_id: int
    empleado_id: Optional[int] = None

    nivel1_satisfaccion: Optional[int] = None
    nivel1_comentario: Optional[str] = None

    nivel2_puntuacion_pre: Optional[Decimal] = None
    nivel2_puntuacion_post: Optional[Decimal] = None
    nivel2_aprobado: bool

    nivel3_observacion_30d: Optional[str] = None
    nivel3_observacion_60d: Optional[str] = None
    nivel3_observacion_90d: Optional[str] = None
    nivel3_aplicacion_pct: Optional[Decimal] = None

    nivel4_indicador: Optional[str] = None
    nivel4_valor_antes: Optional[Decimal] = None
    nivel4_valor_despues: Optional[Decimal] = None
    nivel4_impacto: Optional[str] = None

    responsable_seguimiento: Optional[str] = None
    estado: str

    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    capacitacion_nombre: Optional[str] = None
    empleado_nombre: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

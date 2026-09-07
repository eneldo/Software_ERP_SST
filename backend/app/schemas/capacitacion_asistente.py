# ============================================================
# SCHEMAS: ASISTENTES DE CAPACITACIÓN SST
# FASE 2.7.4 - HARDENING ENTERPRISE CAPACITACIONES SST
# ============================================================

from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import ConfigDict,  BaseModel, Field


class CapacitacionAsistenteCreate(BaseModel):
    capacitacion_id: Optional[int] = None
    empleado_id: Optional[int] = None
    nombres: str
    documento: Optional[str] = None
    cargo: Optional[str] = None
    area: Optional[str] = None
    asistio: bool = True
    evaluacion: Optional[Decimal] = Field(default=None, ge=0, le=100)
    firma_url: Optional[str] = None
    observaciones: Optional[str] = None


class CapacitacionAsistenteUpdate(BaseModel):
    empleado_id: Optional[int] = None
    nombres: Optional[str] = None
    documento: Optional[str] = None
    cargo: Optional[str] = None
    area: Optional[str] = None
    asistio: Optional[bool] = None
    evaluacion: Optional[Decimal] = Field(default=None, ge=0, le=100)
    certificado_generado: Optional[bool] = None
    firma_url: Optional[str] = None
    observaciones: Optional[str] = None
    activo: Optional[bool] = None


class CapacitacionAsistenciaPatch(BaseModel):
    asistio: bool = True


class CapacitacionAsistenteResponse(BaseModel):
    id: int
    capacitacion_id: int
    empleado_id: Optional[int] = None
    nombres: str
    documento: Optional[str] = None
    cargo: Optional[str] = None
    area: Optional[str] = None
    asistio: bool
    evaluacion: Optional[Decimal] = None
    certificado_generado: bool
    firma_url: Optional[str] = None
    observaciones: Optional[str] = None
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# ============================================================
# SCHEMAS CAPACITACIONES SST
# FASE 2.7.1 - HACER / CAPACITACIONES SST PRO ENTERPRISE
# ============================================================

from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class CapacitacionAsistenteCreate(BaseModel):
    empleado_id: Optional[int] = None
    nombres: str
    documento: Optional[str] = None
    cargo: Optional[str] = None
    area: Optional[str] = None
    asistio: bool = True
    evaluacion: Optional[Decimal] = None
    firma_url: Optional[str] = None
    observaciones: Optional[str] = None


class CapacitacionAsistenteUpdate(BaseModel):
    empleado_id: Optional[int] = None
    nombres: Optional[str] = None
    documento: Optional[str] = None
    cargo: Optional[str] = None
    area: Optional[str] = None
    asistio: Optional[bool] = None
    evaluacion: Optional[Decimal] = None
    certificado_generado: Optional[bool] = None
    firma_url: Optional[str] = None
    observaciones: Optional[str] = None
    activo: Optional[bool] = None


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

    class Config:
        from_attributes = True


class CapacitacionCreate(BaseModel):
    empresa_id: int
    codigo: str = "CAP-SST-001"
    nombre: str
    tema: str
    objetivo: Optional[str] = None

    tipo: str = "INTERNA"
    modalidad: str = "PRESENCIAL"
    tipo_capacitacion: str = "CAPACITACION_GENERAL"
    riesgo_asociado: Optional[str] = None

    capacitador: Optional[str] = None
    responsable: Optional[str] = None

    fecha_programada: Optional[date] = None
    fecha_ejecucion: Optional[date] = None

    duracion_horas: Optional[Decimal] = Decimal("0.00")
    lugar: Optional[str] = None

    poblacion_objetivo: Optional[str] = None
    total_asistentes: int = 0

    estado: str = "PROGRAMADA"
    cumplimiento: int = Field(default=0, ge=0, le=100)

    evidencia: Optional[str] = None
    observaciones: Optional[str] = None
    archivo_id: Optional[int] = None


class CapacitacionUpdate(BaseModel):
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    tema: Optional[str] = None
    objetivo: Optional[str] = None

    tipo: Optional[str] = None
    modalidad: Optional[str] = None
    tipo_capacitacion: Optional[str] = None
    riesgo_asociado: Optional[str] = None

    capacitador: Optional[str] = None
    responsable: Optional[str] = None

    fecha_programada: Optional[date] = None
    fecha_ejecucion: Optional[date] = None

    duracion_horas: Optional[Decimal] = None
    lugar: Optional[str] = None

    poblacion_objetivo: Optional[str] = None
    total_asistentes: Optional[int] = None

    estado: Optional[str] = None
    cumplimiento: Optional[int] = Field(default=None, ge=0, le=100)

    evidencia: Optional[str] = None
    observaciones: Optional[str] = None
    archivo_id: Optional[int] = None
    activo: Optional[bool] = None


class CapacitacionResponse(BaseModel):
    id: int
    empresa_id: int
    usuario_id: Optional[int] = None
    archivo_id: Optional[int] = None

    codigo: str
    nombre: str
    tema: str
    objetivo: Optional[str] = None

    tipo: str
    modalidad: str
    tipo_capacitacion: str
    riesgo_asociado: Optional[str] = None

    capacitador: Optional[str] = None
    responsable: Optional[str] = None

    fecha_programada: Optional[date] = None
    fecha_ejecucion: Optional[date] = None

    duracion_horas: Optional[Decimal] = None
    lugar: Optional[str] = None

    poblacion_objetivo: Optional[str] = None
    total_asistentes: int

    estado: str
    cumplimiento: int

    evidencia: Optional[str] = None
    observaciones: Optional[str] = None

    archivo_url: Optional[str] = None
    archivo_nombre: Optional[str] = None
    archivo_extension: Optional[str] = None

    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    asistentes: List[CapacitacionAsistenteResponse] = []

    class Config:
        from_attributes = True


class CapacitacionResumenResponse(BaseModel):
    total: int
    programadas: int
    ejecutadas: int
    canceladas: int
    vencidas: int
    total_asistentes: int
    cumplimiento: int
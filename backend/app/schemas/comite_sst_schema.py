# ============================================================
# SCHEMA COMITÉS SST
# ============================================================

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class ComiteIntegranteCreate(BaseModel):
    empleado_id: Optional[int] = None
    nombre: str
    documento: Optional[str] = None
    cargo: Optional[str] = None
    rol_comite: str
    representa: Optional[str] = None
    fecha_eleccion: Optional[date] = None
    fecha_fin_cargo: Optional[date] = None


class ComiteIntegranteResponse(BaseModel):
    id: int
    comite_id: int
    empleado_id: Optional[int] = None
    nombre: str
    documento: Optional[str] = None
    cargo: Optional[str] = None
    rol_comite: str
    representa: Optional[str] = None
    fecha_eleccion: Optional[date] = None
    fecha_fin_cargo: Optional[date] = None
    activo: bool
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class ComiteReunionCreate(BaseModel):
    numero_reunion: int
    fecha_reunion: date
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    lugar: Optional[str] = None
    tema: Optional[str] = None
    acuerdos: Optional[str] = None
    compromisos: Optional[str] = None
    total_asistentes: Optional[int] = 0
    asistentes_ids: Optional[str] = None


class ComiteReunionResponse(BaseModel):
    id: int
    comite_id: int
    numero_reunion: int
    fecha_reunion: date
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    lugar: Optional[str] = None
    tema: Optional[str] = None
    acuerdos: Optional[str] = None
    compromisos: Optional[str] = None
    total_asistentes: Optional[int] = 0
    acta_url: Optional[str] = None
    estado: str
    activo: bool
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class ComiteCreate(BaseModel):
    empresa_id: int
    tipo_comite: str
    nombre: str
    descripcion: Optional[str] = None
    fecha_constitucion: Optional[date] = None
    fecha_fin_periodo: Optional[date] = None
    observaciones: Optional[str] = None


class ComiteUpdate(BaseModel):
    tipo_comite: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_constitucion: Optional[date] = None
    fecha_fin_periodo: Optional[date] = None
    vigente: Optional[bool] = None
    observaciones: Optional[str] = None


class ComiteResponse(BaseModel):
    id: int
    empresa_id: int
    tipo_comite: str
    nombre: str
    descripcion: Optional[str] = None
    fecha_constitucion: Optional[date] = None
    fecha_fin_periodo: Optional[date] = None
    vigente: bool
    observaciones: Optional[str] = None
    activo: bool
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    total_integrantes: Optional[int] = 0
    total_reuniones: Optional[int] = 0

    class Config:
        from_attributes = True

# ============================================================
# SCHEMA EMERGENCIAS SST
# ============================================================

from datetime import date, datetime
from typing import Optional
from pydantic import ConfigDict,  BaseModel


class BrigadaCreate(BaseModel):
    empresa_id: int
    nombre: str
    tipo_brigada: str
    descripcion: Optional[str] = None
    fecha_conformacion: Optional[date] = None


class BrigadaUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo_brigada: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_conformacion: Optional[date] = None


class BrigadaResponse(BaseModel):
    id: int
    empresa_id: int
    nombre: str
    tipo_brigada: str
    descripcion: Optional[str] = None
    fecha_conformacion: Optional[date] = None
    activo: bool
    fecha_creacion: Optional[datetime] = None
    total_integrantes: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class BrigadaIntegranteCreate(BaseModel):
    empleado_id: Optional[int] = None
    nombre: str
    documento: Optional[str] = None
    cargo: Optional[str] = None
    rol_brigada: str
    telefono: Optional[str] = None


class BrigadaIntegranteResponse(BaseModel):
    id: int
    brigada_id: int
    empleado_id: Optional[int] = None
    nombre: str
    documento: Optional[str] = None
    cargo: Optional[str] = None
    rol_brigada: str
    telefono: Optional[str] = None
    activo: bool

    model_config = ConfigDict(from_attributes=True)


class SimulacroCreate(BaseModel):
    empresa_id: int
    codigo: str
    nombre: str
    tipo_emergencia: str
    fecha_programada: date
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    lugar: Optional[str] = None
    observaciones: Optional[str] = None


class SimulacroUpdate(BaseModel):
    fecha_ejecutada: Optional[date] = None
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    total_participantes: Optional[int] = None
    tiempo_respuesta_minutos: Optional[int] = None
    resultado: Optional[str] = None
    recomendaciones: Optional[str] = None
    plan_mejora: Optional[str] = None
    observaciones: Optional[str] = None
    estado: Optional[str] = None


class SimulacroResponse(BaseModel):
    id: int
    empresa_id: int
    codigo: str
    nombre: str
    tipo_emergencia: str
    fecha_programada: date
    fecha_ejecutada: Optional[date] = None
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    lugar: Optional[str] = None
    total_participantes: Optional[int] = 0
    tiempo_respuesta_minutos: Optional[int] = None
    resultado: Optional[str] = None
    recomendaciones: Optional[str] = None
    plan_mejora: Optional[str] = None
    observaciones: Optional[str] = None
    evidencia_url: Optional[str] = None
    estado: str
    activo: bool
    fecha_creacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AmenazaCreate(BaseModel):
    empresa_id: int
    nombre: str
    tipo_amenaza: str
    descripcion: Optional[str] = None
    probabilidad: Optional[str] = None
    impacto: Optional[str] = None
    medidas_prevencion: Optional[str] = None
    medidas_control: Optional[str] = None


class AmenazaUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo_amenaza: Optional[str] = None
    descripcion: Optional[str] = None
    probabilidad: Optional[str] = None
    impacto: Optional[str] = None
    medidas_prevencion: Optional[str] = None
    medidas_control: Optional[str] = None


class AmenazaResponse(BaseModel):
    id: int
    empresa_id: int
    nombre: str
    tipo_amenaza: str
    descripcion: Optional[str] = None
    probabilidad: Optional[str] = None
    impacto: Optional[str] = None
    nivel_riesgo: Optional[str] = None
    medidas_prevencion: Optional[str] = None
    medidas_control: Optional[str] = None
    activo: bool
    fecha_creacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class InspeccionEmergenciaCreate(BaseModel):
    empresa_id: int
    codigo: str
    nombre: str
    tipo_inspeccion: str
    fecha_inspeccion: date
    lugar: Optional[str] = None
    estado_equipo: Optional[str] = None
    observaciones: Optional[str] = None
    hallazgos: Optional[str] = None
    acciones_correctivas: Optional[str] = None


class InspeccionEmergenciaUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo_inspeccion: Optional[str] = None
    fecha_inspeccion: Optional[date] = None
    lugar: Optional[str] = None
    estado_equipo: Optional[str] = None
    observaciones: Optional[str] = None
    hallazgos: Optional[str] = None
    acciones_correctivas: Optional[str] = None
    estado: Optional[str] = None


class InspeccionEmergenciaResponse(BaseModel):
    id: int
    empresa_id: int
    codigo: str
    nombre: str
    tipo_inspeccion: str
    fecha_inspeccion: date
    lugar: Optional[str] = None
    estado_equipo: Optional[str] = None
    observaciones: Optional[str] = None
    hallazgos: Optional[str] = None
    acciones_correctivas: Optional[str] = None
    evidencia_url: Optional[str] = None
    estado: str
    activo: bool
    fecha_creacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

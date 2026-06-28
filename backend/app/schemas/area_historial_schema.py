# ============================================================
# SCHEMAS HISTÓRICO SST POR ÁREA - ERP SST PRO
# Archivo: backend/app/schemas/area_historial_schema.py
# FASE 1.1.3.4 — Histórico SST por Área
# ============================================================

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AreaHistorialBase(BaseModel):
    tipo_evento: str = Field(..., min_length=2, max_length=80)
    titulo: str = Field(..., min_length=3, max_length=180)
    descripcion: Optional[str] = Field(default=None, max_length=3000)
    impacto_sst: Optional[str] = Field(default="MEDIO", max_length=50)
    estado_resultante: Optional[str] = Field(default="REGISTRADO", max_length=50)
    responsable: Optional[str] = Field(default=None, max_length=180)
    evidencia_url: Optional[str] = Field(default=None, max_length=500)


class AreaHistorialCreate(AreaHistorialBase):
    fecha_evento: Optional[datetime] = None


class AreaHistorialUpdate(BaseModel):
    tipo_evento: Optional[str] = Field(default=None, min_length=2, max_length=80)
    titulo: Optional[str] = Field(default=None, min_length=3, max_length=180)
    descripcion: Optional[str] = Field(default=None, max_length=3000)
    impacto_sst: Optional[str] = Field(default=None, max_length=50)
    estado_resultante: Optional[str] = Field(default=None, max_length=50)
    responsable: Optional[str] = Field(default=None, max_length=180)
    evidencia_url: Optional[str] = Field(default=None, max_length=500)
    fecha_evento: Optional[datetime] = None


class AreaHistorialResponse(BaseModel):
    id: int
    area_id: int
    tipo_evento: str
    titulo: str
    descripcion: Optional[str] = None
    impacto_sst: Optional[str] = None
    estado_resultante: Optional[str] = None
    responsable: Optional[str] = None
    evidencia_url: Optional[str] = None
    fecha_evento: Optional[datetime] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class AreaHistorialResumenResponse(BaseModel):
    total_eventos: int = 0
    eventos_alto_impacto: int = 0
    eventos_abiertos: int = 0
    ultimo_evento: Optional[AreaHistorialResponse] = None
    eventos_por_tipo: dict[str, int] = {}
    eventos_por_impacto: dict[str, int] = {}

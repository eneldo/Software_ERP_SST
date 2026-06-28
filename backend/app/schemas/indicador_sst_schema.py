# ============================================================
# SCHEMAS INDICADORES SST - ERP SST PRO
# FASE 1.1.18.1 — NÚCLEO INDICADORES SST BI EXECUTIVE
# Archivo: backend/app/schemas/indicador_sst_schema.py
# ============================================================

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class IndicadorSSTBase(BaseModel):
    empresa_id: int
    sede_id: Optional[int] = None
    area_id: Optional[int] = None
    cargo_id: Optional[int] = None

    codigo: str = Field(..., min_length=2, max_length=80)
    nombre: str = Field(..., min_length=3, max_length=255)
    descripcion: Optional[str] = None

    categoria: str = Field(default="GESTION", max_length=80)
    tipo_indicador: str = Field(default="RESULTADO", max_length=80)
    origen_dato: str = Field(default="MANUAL", max_length=80)
    frecuencia: str = Field(default="MENSUAL", max_length=50)

    formula: Optional[str] = None
    unidad: str = Field(default="%", max_length=40)
    meta: Decimal = Field(default=100, ge=0)
    valor_actual: Decimal = Field(default=0, ge=0)
    resultado: Decimal = Field(default=0, ge=0)
    semaforo: str = Field(default="ROJO", max_length=30)
    tendencia: Optional[str] = Field(default="ESTABLE", max_length=30)

    periodo_inicio: Optional[date] = None
    periodo_fin: Optional[date] = None
    responsable: Optional[str] = Field(default=None, max_length=255)
    fuente: Optional[str] = Field(default=None, max_length=255)
    observaciones: Optional[str] = None
    activo: bool = True


class IndicadorSSTCreate(IndicadorSSTBase):
    pass


class IndicadorSSTUpdate(BaseModel):
    empresa_id: Optional[int] = None
    sede_id: Optional[int] = None
    area_id: Optional[int] = None
    cargo_id: Optional[int] = None

    codigo: Optional[str] = Field(default=None, min_length=2, max_length=80)
    nombre: Optional[str] = Field(default=None, min_length=3, max_length=255)
    descripcion: Optional[str] = None

    categoria: Optional[str] = Field(default=None, max_length=80)
    tipo_indicador: Optional[str] = Field(default=None, max_length=80)
    origen_dato: Optional[str] = Field(default=None, max_length=80)
    frecuencia: Optional[str] = Field(default=None, max_length=50)

    formula: Optional[str] = None
    unidad: Optional[str] = Field(default=None, max_length=40)
    meta: Optional[Decimal] = Field(default=None, ge=0)
    valor_actual: Optional[Decimal] = Field(default=None, ge=0)
    resultado: Optional[Decimal] = Field(default=None, ge=0)
    semaforo: Optional[str] = Field(default=None, max_length=30)
    tendencia: Optional[str] = Field(default=None, max_length=30)

    periodo_inicio: Optional[date] = None
    periodo_fin: Optional[date] = None
    responsable: Optional[str] = Field(default=None, max_length=255)
    fuente: Optional[str] = Field(default=None, max_length=255)
    observaciones: Optional[str] = None
    activo: Optional[bool] = None


class IndicadorSSTResponse(IndicadorSSTBase):
    id: int
    usuario_id: Optional[int] = None
    empresa_nombre: Optional[str] = None
    sede_nombre: Optional[str] = None
    area_nombre: Optional[str] = None
    cargo_nombre: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class KPIAutomaticoResponse(BaseModel):
    codigo: str
    nombre: str
    categoria: str
    valor: float
    meta: float
    unidad: str
    cumplimiento: float
    semaforo: str
    tendencia: str = "ESTABLE"
    fuente: str
    descripcion: Optional[str] = None


class IndicadoresDashboardResponse(BaseModel):
    total_indicadores: int
    automaticos: int
    manuales: int
    verdes: int
    amarillos: int
    rojos: int
    cumplimiento_global: float
    score_sst: float
    semaforo_global: str
    kpis_automaticos: list[KPIAutomaticoResponse]
    distribucion_categoria: dict[str, int]
    distribucion_semaforo: dict[str, int]
    alertas: dict[str, int]
    recomendaciones: list[str]

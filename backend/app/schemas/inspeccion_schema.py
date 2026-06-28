# ============================================================
# SCHEMAS INSPECCIONES SST ENTERPRISE - ERP SST PRO
# FASE 1.1.8 — INSPECCIONES SST ENTERPRISE
# Archivo: backend/app/schemas/inspeccion_schema.py
# ============================================================

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


ESTADOS_INSPECCION = {"PROGRAMADA", "EN_PROCESO", "EJECUTADA", "CERRADA", "ANULADA"}
RESULTADOS_INSPECCION = {"PENDIENTE", "CUMPLE", "NO_CUMPLE", "CUMPLE_PARCIAL"}
NIVELES_RIESGO = {"BAJO", "MEDIO", "ALTO", "CRITICO"}
ESTADOS_HALLAZGO = {"ABIERTO", "EN_SEGUIMIENTO", "CERRADO", "ANULADO"}


def _upper_clean(value, default=None):
    if value is None:
        return default
    value = str(value).strip().upper()
    return value if value else default


class InspeccionBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    empresa_id: int = Field(..., gt=0)
    sede_id: Optional[int] = Field(default=None, gt=0)
    area_id: Optional[int] = Field(default=None, gt=0)
    cargo_id: Optional[int] = Field(default=None, gt=0)
    empleado_id: Optional[int] = Field(default=None, gt=0)
    usuario_id: Optional[int] = Field(default=None, gt=0)

    codigo: str = Field(..., min_length=2, max_length=80)
    tipo_inspeccion: str = Field(default="GENERAL", max_length=80)
    titulo: str = Field(..., min_length=3, max_length=255)
    descripcion: Optional[str] = None
    lugar: Optional[str] = Field(default=None, max_length=255)
    responsable: Optional[str] = Field(default=None, max_length=255)
    fecha_programada: Optional[date] = None
    fecha_inspeccion: date
    estado: str = "PROGRAMADA"
    resultado: str = "PENDIENTE"
    nivel_riesgo: str = "BAJO"
    cumplimiento: Optional[Decimal] = Field(default=0, ge=0, le=100)
    observaciones: Optional[str] = None
    firma_inspector: Optional[str] = None
    firma_inspector_nombre: Optional[str] = Field(default=None, max_length=255)
    firma_responsable_area: Optional[str] = None
    firma_responsable_area_nombre: Optional[str] = Field(default=None, max_length=255)
    firma_sst: Optional[str] = None
    firma_sst_nombre: Optional[str] = Field(default=None, max_length=255)
    cierre_digital: bool = False
    trazabilidad: Optional[str] = None
    activo: bool = True

    @field_validator("codigo", "tipo_inspeccion", "estado", "resultado", "nivel_riesgo")
    @classmethod
    def upper_values(cls, value):
        return _upper_clean(value)

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value):
        value = _upper_clean(value, "PROGRAMADA")
        if value not in ESTADOS_INSPECCION:
            raise ValueError("Estado de inspección no válido")
        return value

    @field_validator("resultado")
    @classmethod
    def validar_resultado(cls, value):
        value = _upper_clean(value, "PENDIENTE")
        if value not in RESULTADOS_INSPECCION:
            raise ValueError("Resultado de inspección no válido")
        return value

    @field_validator("nivel_riesgo")
    @classmethod
    def validar_riesgo(cls, value):
        value = _upper_clean(value, "BAJO")
        if value not in NIVELES_RIESGO:
            raise ValueError("Nivel de riesgo no válido")
        return value


class InspeccionCreate(InspeccionBase):
    pass


class InspeccionUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    empresa_id: Optional[int] = Field(default=None, gt=0)
    sede_id: Optional[int] = Field(default=None, gt=0)
    area_id: Optional[int] = Field(default=None, gt=0)
    cargo_id: Optional[int] = Field(default=None, gt=0)
    empleado_id: Optional[int] = Field(default=None, gt=0)
    usuario_id: Optional[int] = Field(default=None, gt=0)
    codigo: Optional[str] = Field(default=None, min_length=2, max_length=80)
    tipo_inspeccion: Optional[str] = Field(default=None, max_length=80)
    titulo: Optional[str] = Field(default=None, min_length=3, max_length=255)
    descripcion: Optional[str] = None
    lugar: Optional[str] = Field(default=None, max_length=255)
    responsable: Optional[str] = Field(default=None, max_length=255)
    fecha_programada: Optional[date] = None
    fecha_inspeccion: Optional[date] = None
    estado: Optional[str] = None
    resultado: Optional[str] = None
    nivel_riesgo: Optional[str] = None
    cumplimiento: Optional[Decimal] = Field(default=None, ge=0, le=100)
    observaciones: Optional[str] = None
    firma_inspector: Optional[str] = None
    firma_inspector_nombre: Optional[str] = Field(default=None, max_length=255)
    firma_responsable_area: Optional[str] = None
    firma_responsable_area_nombre: Optional[str] = Field(default=None, max_length=255)
    firma_sst: Optional[str] = None
    firma_sst_nombre: Optional[str] = Field(default=None, max_length=255)
    cierre_digital: Optional[bool] = None
    trazabilidad: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("codigo", "tipo_inspeccion", "estado", "resultado", "nivel_riesgo")
    @classmethod
    def upper_values(cls, value):
        return _upper_clean(value) if value is not None else value


class InspeccionResponse(InspeccionBase):
    id: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    empresa_nombre: Optional[str] = None
    sede_nombre: Optional[str] = None
    area_nombre: Optional[str] = None
    cargo_nombre: Optional[str] = None
    empleado_nombre: Optional[str] = None
    empleado_documento: Optional[str] = None
    total_hallazgos: int = 0
    hallazgos_abiertos: int = 0
    total_evidencias: int = 0
    firma_inspector_fecha: Optional[datetime] = None
    firma_responsable_area_fecha: Optional[datetime] = None
    firma_sst_fecha: Optional[datetime] = None
    cierre_digital_fecha: Optional[datetime] = None
    cierre_digital_usuario_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class HallazgoBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    inspeccion_id: int = Field(..., gt=0)
    empresa_id: int = Field(..., gt=0)
    descripcion: str = Field(..., min_length=3)
    tipo_hallazgo: str = "CONDICION_INSEGURA"
    nivel_riesgo: str = "MEDIO"
    accion_recomendada: Optional[str] = None
    responsable: Optional[str] = Field(default=None, max_length=255)
    fecha_compromiso: Optional[date] = None
    fecha_cierre: Optional[date] = None
    estado: str = "ABIERTO"
    observaciones: Optional[str] = None
    firma_inspector: Optional[str] = None
    firma_inspector_nombre: Optional[str] = Field(default=None, max_length=255)
    firma_responsable_area: Optional[str] = None
    firma_responsable_area_nombre: Optional[str] = Field(default=None, max_length=255)
    firma_sst: Optional[str] = None
    firma_sst_nombre: Optional[str] = Field(default=None, max_length=255)
    cierre_digital: bool = False
    trazabilidad: Optional[str] = None
    activo: bool = True

    @field_validator("tipo_hallazgo", "nivel_riesgo", "estado")
    @classmethod
    def upper_values(cls, value):
        return _upper_clean(value)

    @field_validator("nivel_riesgo")
    @classmethod
    def validar_riesgo(cls, value):
        value = _upper_clean(value, "MEDIO")
        if value not in NIVELES_RIESGO:
            raise ValueError("Nivel de riesgo no válido")
        return value

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value):
        value = _upper_clean(value, "ABIERTO")
        if value not in ESTADOS_HALLAZGO:
            raise ValueError("Estado de hallazgo no válido")
        return value


class HallazgoCreate(HallazgoBase):
    pass


class HallazgoUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    descripcion: Optional[str] = Field(default=None, min_length=3)
    tipo_hallazgo: Optional[str] = None
    nivel_riesgo: Optional[str] = None
    accion_recomendada: Optional[str] = None
    responsable: Optional[str] = Field(default=None, max_length=255)
    fecha_compromiso: Optional[date] = None
    fecha_cierre: Optional[date] = None
    estado: Optional[str] = None
    observaciones: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("tipo_hallazgo", "nivel_riesgo", "estado")
    @classmethod
    def upper_values(cls, value):
        return _upper_clean(value) if value is not None else value


class HallazgoResponse(HallazgoBase):
    id: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    total_evidencias: int = 0
    firma_inspector_fecha: Optional[datetime] = None
    firma_responsable_area_fecha: Optional[datetime] = None
    firma_sst_fecha: Optional[datetime] = None
    cierre_digital_fecha: Optional[datetime] = None
    cierre_digital_usuario_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class InspeccionDashboardResponse(BaseModel):
    kpis: dict
    charts: dict
    alertas: dict
    recomendaciones: list[str]


class InspeccionFirmaRequest(BaseModel):
    rol_firma: str = Field(..., description="INSPECTOR, RESPONSABLE_AREA o SST")
    nombre_firmante: str = Field(..., min_length=2, max_length=255)
    firma_base64: str = Field(..., min_length=10)
    observacion: Optional[str] = None

    @field_validator("rol_firma")
    @classmethod
    def validar_rol_firma(cls, value):
        value = _upper_clean(value)
        permitidos = {"INSPECTOR", "RESPONSABLE_AREA", "SST"}
        if value not in permitidos:
            raise ValueError("Rol de firma no válido")
        return value


class InspeccionCierreDigitalRequest(BaseModel):
    observacion: Optional[str] = None

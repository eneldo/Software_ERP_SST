# ============================================================
# SCHEMAS CAPA SST ENTERPRISE - ERP SST PRO
# FASE 1.1.8.7.1 — Optimización CAPA Enterprise
# Archivo: backend/app/schemas/capa_schema.py
# ============================================================

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


TIPOS_ACCION = {"CORRECTIVA", "PREVENTIVA", "MEJORA"}
ORIGENES_CAPA = {"INSPECCION_SST", "HALLAZGO_SST", "ACCIDENTE", "INCIDENTE", "AUDITORIA", "MATRIZ_LEGAL", "OBSERVACION_SST", "REPORTE_ANONIMO_SST", "ACTO_INSEGURO", "CONDICION_INSEGURA","OTRO"}
PRIORIDADES_CAPA = {"BAJA", "MEDIA", "ALTA", "CRITICA"}
ESTADOS_CAPA = {"ABIERTA", "EN_ANALISIS", "PLANIFICADA", "EN_EJECUCION", "VERIFICACION", "CERRADA", "ANULADA"}
RESULTADOS_SEGUIMIENTO = {"EN_SEGUIMIENTO", "AVANCE", "SIN_AVANCE", "BLOQUEADO", "VERIFICADO", "CERRADO", "COMPLETADO", "FINALIZADO", "EFECTIVO", "NO_EFECTIVO", "REPROGRAMADO"}


def _upper_clean(value, default=None):
    if value is None:
        return default
    value = str(value).strip().upper()
    return value if value else default


class CapaBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    empresa_id: int = Field(..., gt=0)
    sede_id: Optional[int] = Field(default=None, gt=0)
    area_id: Optional[int] = Field(default=None, gt=0)
    cargo_id: Optional[int] = Field(default=None, gt=0)
    empleado_id: Optional[int] = Field(default=None, gt=0)
    usuario_id: Optional[int] = Field(default=None, gt=0)
    inspeccion_id: Optional[int] = Field(default=None, gt=0)
    hallazgo_id: Optional[int] = Field(default=None, gt=0)

    codigo: str = Field(..., min_length=2, max_length=80)
    titulo: str = Field(..., min_length=3, max_length=255)
    descripcion: str = Field(..., min_length=3)
    tipo_accion: str = "CORRECTIVA"
    origen: str = "INSPECCION_SST"
    prioridad: str = "MEDIA"
    estado: str = "ABIERTA"
    responsable: Optional[str] = Field(default=None, max_length=255)
    fecha_apertura: Optional[date] = None
    fecha_compromiso: Optional[date] = None
    fecha_cierre: Optional[date] = None
    avance: Decimal = Field(default=0, ge=0, le=100)

    causa_raiz: Optional[str] = None
    porque_1: Optional[str] = None
    porque_2: Optional[str] = None
    porque_3: Optional[str] = None
    porque_4: Optional[str] = None
    porque_5: Optional[str] = None
    ishikawa_metodo: Optional[str] = None
    ishikawa_mano_obra: Optional[str] = None
    ishikawa_maquinaria: Optional[str] = None
    ishikawa_materiales: Optional[str] = None
    ishikawa_medio_ambiente: Optional[str] = None
    ishikawa_medicion: Optional[str] = None
    accion_inmediata: Optional[str] = None
    accion_correctiva: Optional[str] = None
    accion_preventiva: Optional[str] = None
    verificacion_eficacia: Optional[str] = None
    efectiva: Optional[bool] = None
    observaciones: Optional[str] = None
    activo: bool = True

    @field_validator("codigo", "tipo_accion", "origen", "prioridad", "estado")
    @classmethod
    def upper_values(cls, value):
        return _upper_clean(value)

    @field_validator("tipo_accion")
    @classmethod
    def validar_tipo(cls, value):
        value = _upper_clean(value, "CORRECTIVA")
        if value not in TIPOS_ACCION:
            raise ValueError("Tipo de acción CAPA no válido")
        return value

    @field_validator("origen")
    @classmethod
    def validar_origen(cls, value):
        value = _upper_clean(value, "INSPECCION_SST")
        if value not in ORIGENES_CAPA:
            raise ValueError("Origen CAPA no válido")
        return value

    @field_validator("prioridad")
    @classmethod
    def validar_prioridad(cls, value):
        value = _upper_clean(value, "MEDIA")
        if value not in PRIORIDADES_CAPA:
            raise ValueError("Prioridad CAPA no válida")
        return value

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value):
        value = _upper_clean(value, "ABIERTA")
        if value not in ESTADOS_CAPA:
            raise ValueError("Estado CAPA no válido")
        return value


class CapaCreate(CapaBase):
    pass


class CapaUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    empresa_id: Optional[int] = Field(default=None, gt=0)
    sede_id: Optional[int] = Field(default=None, gt=0)
    area_id: Optional[int] = Field(default=None, gt=0)
    cargo_id: Optional[int] = Field(default=None, gt=0)
    empleado_id: Optional[int] = Field(default=None, gt=0)
    inspeccion_id: Optional[int] = Field(default=None, gt=0)
    hallazgo_id: Optional[int] = Field(default=None, gt=0)
    codigo: Optional[str] = Field(default=None, min_length=2, max_length=80)
    titulo: Optional[str] = Field(default=None, min_length=3, max_length=255)
    descripcion: Optional[str] = Field(default=None, min_length=3)
    tipo_accion: Optional[str] = None
    origen: Optional[str] = None
    prioridad: Optional[str] = None
    estado: Optional[str] = None
    responsable: Optional[str] = Field(default=None, max_length=255)
    fecha_apertura: Optional[date] = None
    fecha_compromiso: Optional[date] = None
    fecha_cierre: Optional[date] = None
    avance: Optional[Decimal] = Field(default=None, ge=0, le=100)
    causa_raiz: Optional[str] = None
    porque_1: Optional[str] = None
    porque_2: Optional[str] = None
    porque_3: Optional[str] = None
    porque_4: Optional[str] = None
    porque_5: Optional[str] = None
    ishikawa_metodo: Optional[str] = None
    ishikawa_mano_obra: Optional[str] = None
    ishikawa_maquinaria: Optional[str] = None
    ishikawa_materiales: Optional[str] = None
    ishikawa_medio_ambiente: Optional[str] = None
    ishikawa_medicion: Optional[str] = None
    accion_inmediata: Optional[str] = None
    accion_correctiva: Optional[str] = None
    accion_preventiva: Optional[str] = None
    verificacion_eficacia: Optional[str] = None
    efectiva: Optional[bool] = None
    observaciones: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("codigo", "tipo_accion", "origen", "prioridad", "estado")
    @classmethod
    def upper_values(cls, value):
        return _upper_clean(value) if value is not None else value


class CapaResponse(CapaBase):
    id: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    fecha_cierre: Optional[date] = None
    trazabilidad: Optional[str] = None
    empresa_nombre: Optional[str] = None
    sede_nombre: Optional[str] = None
    area_nombre: Optional[str] = None
    cargo_nombre: Optional[str] = None
    empleado_nombre: Optional[str] = None
    inspeccion_codigo: Optional[str] = None
    hallazgo_descripcion: Optional[str] = None
    total_seguimientos: int = 0
    total_evidencias: int = 0
    vencida: bool = False
    dias_vencimiento: Optional[int] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class CapaSeguimientoBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    capa_id: int = Field(..., gt=0)
    empresa_id: int = Field(..., gt=0)
    fecha_seguimiento: date
    responsable: Optional[str] = Field(default=None, max_length=255)
    avance: Decimal = Field(default=0, ge=0, le=100)
    resultado: str = "EN_SEGUIMIENTO"
    comentario: str = Field(..., min_length=3)
    proximo_seguimiento: Optional[date] = None
    activo: bool = True

    @field_validator("resultado")
    @classmethod
    def validar_resultado(cls, value):
        value = _upper_clean(value, "EN_SEGUIMIENTO")
        if value not in RESULTADOS_SEGUIMIENTO:
            raise ValueError("Resultado de seguimiento no válido")
        return value


class CapaSeguimientoCreate(CapaSeguimientoBase):
    pass


class CapaSeguimientoUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    fecha_seguimiento: Optional[date] = None
    responsable: Optional[str] = Field(default=None, max_length=255)
    avance: Optional[Decimal] = Field(default=None, ge=0, le=100)
    resultado: Optional[str] = None
    comentario: Optional[str] = Field(default=None, min_length=3)
    proximo_seguimiento: Optional[date] = None
    activo: Optional[bool] = None

    @field_validator("resultado")
    @classmethod
    def upper_values(cls, value):
        return _upper_clean(value) if value is not None else value


class CapaSeguimientoResponse(CapaSeguimientoBase):
    id: int
    usuario_id: Optional[int] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class CapaCierreRequest(BaseModel):
    efectiva: bool = True
    verificacion_eficacia: str = Field(..., min_length=5)
    observacion: Optional[str] = None


class CapaDashboardResponse(BaseModel):
    kpis: dict
    charts: dict
    alertas: dict
    recomendaciones: list[str]

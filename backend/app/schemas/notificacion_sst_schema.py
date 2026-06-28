# ============================================================
# SCHEMAS NOTIFICACIONES SST - ERP SST PRO
# FASE 1.1.24.1 — CENTRO DE NOTIFICACIONES INTELIGENTES SST
# Archivo: backend/app/schemas/notificacion_sst_schema.py
# ============================================================

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


PRIORIDADES_NOTIFICACION = {"CRITICA", "ALTA", "MEDIA", "BAJA"}
ESTADOS_NOTIFICACION = {"PENDIENTE", "LEIDA", "ARCHIVADA", "RESUELTA"}
TIPOS_NOTIFICACION = {"ALERTA", "VENCIMIENTO", "SEGUIMIENTO", "CUMPLIMIENTO", "SISTEMA"}


def _upper_clean(value, default=None):
    if value is None:
        return default
    value = str(value).strip().upper()
    return value if value else default


class NotificacionSSTBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    empresa_id: Optional[int] = Field(default=None, gt=0)
    sede_id: Optional[int] = Field(default=None, gt=0)
    area_id: Optional[int] = Field(default=None, gt=0)
    usuario_id: Optional[int] = Field(default=None, gt=0)

    modulo: str = Field(..., min_length=2, max_length=80)
    referencia_id: Optional[int] = None
    clave_unica: Optional[str] = Field(default=None, max_length=180)

    tipo: str = Field(default="ALERTA", max_length=80)
    prioridad: str = Field(default="MEDIA", max_length=40)
    estado: str = Field(default="PENDIENTE", max_length=40)

    titulo: str = Field(..., min_length=3, max_length=255)
    descripcion: Optional[str] = None
    accion_recomendada: Optional[str] = None
    url_destino: Optional[str] = Field(default=None, max_length=500)

    fecha_evento: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    leida: bool = False
    archivada: bool = False
    activa: bool = True
    origen_generacion: Optional[str] = Field(default="AUTOMATICA", max_length=80)
    metadata_json: Optional[str] = None

    @field_validator("modulo", "tipo", "prioridad", "estado", "origen_generacion")
    @classmethod
    def upper_values(cls, value):
        return _upper_clean(value) if value is not None else value

    @field_validator("prioridad")
    @classmethod
    def validar_prioridad(cls, value):
        value = _upper_clean(value, "MEDIA")
        if value not in PRIORIDADES_NOTIFICACION:
            raise ValueError("Prioridad de notificación no válida")
        return value

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value):
        value = _upper_clean(value, "PENDIENTE")
        if value not in ESTADOS_NOTIFICACION:
            raise ValueError("Estado de notificación no válido")
        return value

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, value):
        value = _upper_clean(value, "ALERTA")
        if value not in TIPOS_NOTIFICACION:
            raise ValueError("Tipo de notificación no válido")
        return value


class NotificacionSSTCreate(NotificacionSSTBase):
    pass


class NotificacionSSTUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    tipo: Optional[str] = None
    prioridad: Optional[str] = None
    estado: Optional[str] = None
    titulo: Optional[str] = Field(default=None, min_length=3, max_length=255)
    descripcion: Optional[str] = None
    accion_recomendada: Optional[str] = None
    url_destino: Optional[str] = Field(default=None, max_length=500)
    fecha_evento: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    leida: Optional[bool] = None
    archivada: Optional[bool] = None
    activa: Optional[bool] = None

    @field_validator("tipo", "prioridad", "estado")
    @classmethod
    def upper_values(cls, value):
        return _upper_clean(value) if value is not None else value


class NotificacionSSTResponse(NotificacionSSTBase):
    id: int
    fecha_lectura: Optional[datetime] = None
    fecha_archivo: Optional[datetime] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    empresa_nombre: Optional[str] = None
    sede_nombre: Optional[str] = None
    area_nombre: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class NotificacionesDashboardResponse(BaseModel):
    total: int
    no_leidas: int
    leidas: int
    archivadas: int
    criticas: int
    altas: int
    medias: int
    bajas: int
    por_modulo: dict[str, int]
    por_prioridad: dict[str, int]
    por_estado: dict[str, int]
    recomendaciones: list[str]


class GeneracionNotificacionesResponse(BaseModel):
    generadas: int
    existentes: int
    total_activas: int
    detalle: dict[str, int]


class ConfiguracionNotificacionSSTBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    empresa_id: int = Field(..., gt=0)
    habilitar_notificaciones: bool = True
    dias_alerta_vencimiento: int = Field(default=15, ge=0, le=365)
    dias_alerta_critica: int = Field(default=0, ge=0, le=365)
    canal_sistema: bool = True
    canal_email: bool = False
    canal_whatsapp: bool = False
    email_destino: Optional[str] = Field(default=None, max_length=255)
    whatsapp_destino: Optional[str] = Field(default=None, max_length=80)
    frecuencia_generacion: str = Field(default="DIARIA", max_length=50)
    hora_generacion: Optional[str] = Field(default="08:00", max_length=20)
    activo: bool = True

    @field_validator("frecuencia_generacion")
    @classmethod
    def normalizar_frecuencia(cls, value):
        return _upper_clean(value, "DIARIA")


class ConfiguracionNotificacionSSTCreate(ConfiguracionNotificacionSSTBase):
    pass


class ConfiguracionNotificacionSSTUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    habilitar_notificaciones: Optional[bool] = None
    dias_alerta_vencimiento: Optional[int] = Field(default=None, ge=0, le=365)
    dias_alerta_critica: Optional[int] = Field(default=None, ge=0, le=365)
    canal_sistema: Optional[bool] = None
    canal_email: Optional[bool] = None
    canal_whatsapp: Optional[bool] = None
    email_destino: Optional[str] = Field(default=None, max_length=255)
    whatsapp_destino: Optional[str] = Field(default=None, max_length=80)
    frecuencia_generacion: Optional[str] = Field(default=None, max_length=50)
    hora_generacion: Optional[str] = Field(default=None, max_length=20)
    activo: Optional[bool] = None


class ConfiguracionNotificacionSSTResponse(ConfiguracionNotificacionSSTBase):
    id: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True, extra="ignore")

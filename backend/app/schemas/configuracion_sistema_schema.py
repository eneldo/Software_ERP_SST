# ============================================================
# SCHEMAS CONFIGURACIÓN SISTEMA PRO
# ERP SST PRO ENTERPRISE
# FASE 35.4.2 — Configuración Sistema PRO
# Archivo: backend/app/schemas/configuracion_sistema_schema.py
# ============================================================

from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ConfiguracionSistemaBase(BaseModel):
    nombre_plataforma: str = Field(default="ERP SST PRO", max_length=150)
    ambiente: str = Field(default="LOCAL", max_length=50)
    version: str = Field(default="1.0.0", max_length=50)
    dominio_frontend: str | None = Field(default=None, max_length=255)
    dominio_backend: str | None = Field(default=None, max_length=255)
    soporte_correo: str | None = Field(default=None, max_length=150)
    soporte_telefono: str | None = Field(default=None, max_length=80)
    jwt_expiracion_minutos: int = Field(default=480, ge=5, le=10080)
    intentos_login_maximos: int = Field(default=5, ge=1, le=20)
    bloqueo_login_minutos: int = Field(default=15, ge=1, le=1440)
    exigir_password_fuerte: bool = True
    permitir_registro_publico: bool = False
    upload_max_mb: int = Field(default=25, ge=1, le=200)
    evidencias_webp: bool = True
    evidencias_preview: bool = True
    evidencias_thumbnail: bool = True
    retencion_evidencias_meses: int = Field(default=60, ge=1, le=240)
    smtp_activo: bool = False
    smtp_host: str | None = Field(default=None, max_length=150)
    smtp_puerto: int | None = Field(default=None, ge=1, le=65535)
    smtp_usuario: str | None = Field(default=None, max_length=150)
    smtp_from: str | None = Field(default=None, max_length=150)
    notificaciones_activas: bool = True
    backups_activos: bool = True
    backups_frecuencia: str = Field(default="DIARIO", max_length=50)
    backups_retencion_dias: int = Field(default=30, ge=1, le=3650)
    mantenimiento_activo: bool = False
    mantenimiento_mensaje: str | None = None
    observaciones: str | None = None


class ConfiguracionSistemaUpdate(ConfiguracionSistemaBase):
    pass


class ConfiguracionSistemaResponse(ConfiguracionSistemaBase):
    id: int
    actualizado_por: int | None = None
    fecha_creacion: datetime | None = None
    fecha_actualizacion: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class ConfiguracionSistemaHealth(BaseModel):
    ok: bool
    mensaje: str
    configuracion_creada: bool
    seguridad: dict
    evidencias: dict
    backups: dict
    notificaciones: dict
    mantenimiento: dict

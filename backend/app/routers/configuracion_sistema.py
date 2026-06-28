# ============================================================
# ROUTER CONFIGURACIÓN SISTEMA PRO
# ERP SST PRO ENTERPRISE
# FASE 35.4.2 — Configuración Sistema PRO
# Archivo: backend/app/routers/configuracion_sistema.py
# ============================================================

from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.dependencies import require_roles
from app.database import get_db
from app.models.configuracion_sistema import ConfiguracionSistema
from app.schemas.configuracion_sistema_schema import ConfiguracionSistemaHealth, ConfiguracionSistemaResponse, ConfiguracionSistemaUpdate

router = APIRouter(prefix="/configuracion-sistema", tags=["Configuración Sistema PRO"])
ROLES_CONFIGURACION = ["SUPER_ADMIN"]


def _get_or_create_config(db: Session) -> ConfiguracionSistema:
    config = db.query(ConfiguracionSistema).order_by(ConfiguracionSistema.id.asc()).first()
    if config:
        return config
    config = ConfiguracionSistema()
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.get("/", response_model=ConfiguracionSistemaResponse)
def obtener_configuracion_sistema(db: Session = Depends(get_db), usuario=Depends(require_roles(ROLES_CONFIGURACION))):
    return _get_or_create_config(db)


@router.put("/", response_model=ConfiguracionSistemaResponse)
def actualizar_configuracion_sistema(data: ConfiguracionSistemaUpdate, db: Session = Depends(get_db), usuario=Depends(require_roles(ROLES_CONFIGURACION))):
    config = _get_or_create_config(db)
    payload = data.model_dump(exclude_unset=True)
    for key, value in payload.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(config, key, value)
    config.actualizado_por = getattr(usuario, "id", None)
    db.commit()
    db.refresh(config)
    return config


@router.get("/health", response_model=ConfiguracionSistemaHealth)
def health_configuracion_sistema(db: Session = Depends(get_db), usuario=Depends(require_roles(ROLES_CONFIGURACION))):
    config = _get_or_create_config(db)
    seguridad_ok = bool(config.jwt_expiracion_minutos and config.intentos_login_maximos)
    evidencias_ok = bool(config.upload_max_mb and config.evidencias_webp)
    backups_ok = bool(config.backups_activos and config.backups_retencion_dias)
    notificaciones_ok = bool(config.notificaciones_activas)
    mantenimiento_ok = not bool(config.mantenimiento_activo) or bool(config.mantenimiento_mensaje)
    return ConfiguracionSistemaHealth(
        ok=seguridad_ok and evidencias_ok,
        mensaje="Configuración del sistema validada correctamente.",
        configuracion_creada=True,
        seguridad={"ok": seguridad_ok, "jwt_expiracion_minutos": config.jwt_expiracion_minutos, "intentos_login_maximos": config.intentos_login_maximos, "bloqueo_login_minutos": config.bloqueo_login_minutos, "password_fuerte": config.exigir_password_fuerte},
        evidencias={"ok": evidencias_ok, "upload_max_mb": config.upload_max_mb, "webp": config.evidencias_webp, "preview": config.evidencias_preview, "thumbnail": config.evidencias_thumbnail, "retencion_meses": config.retencion_evidencias_meses},
        backups={"ok": backups_ok, "activos": config.backups_activos, "frecuencia": config.backups_frecuencia, "retencion_dias": config.backups_retencion_dias},
        notificaciones={"ok": notificaciones_ok, "activas": config.notificaciones_activas, "smtp_activo": config.smtp_activo, "smtp_host": config.smtp_host, "smtp_from": config.smtp_from},
        mantenimiento={"ok": mantenimiento_ok, "activo": config.mantenimiento_activo, "mensaje": config.mantenimiento_mensaje},
    )

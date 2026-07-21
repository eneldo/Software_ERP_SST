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
from app.models.configuracion_sistema import AparienciaSistema, ConfiguracionSistema
from app.schemas.configuracion_sistema_schema import AparienciaSistemaResponse, ConfiguracionSistemaHealth, ConfiguracionSistemaResponse, ConfiguracionSistemaUpdate

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


def _get_or_create_appearance(db: Session) -> AparienciaSistema:
    appearance = db.query(AparienciaSistema).order_by(AparienciaSistema.id.asc()).first()
    if appearance:
        return appearance
    appearance = AparienciaSistema()
    db.add(appearance)
    db.commit()
    db.refresh(appearance)
    return appearance


def _config_response(config: ConfiguracionSistema, appearance: AparienciaSistema) -> dict:
    data = {column.name: getattr(config, column.name) for column in ConfiguracionSistema.__table__.columns}
    for field in ("logo_data_url", "color_primario", "color_secundario", "color_menu_inicio", "color_menu_fin", "tipografia"):
        data[field] = getattr(appearance, field)
    return data


@router.get("/", response_model=ConfiguracionSistemaResponse)
def obtener_configuracion_sistema(db: Session = Depends(get_db), usuario=Depends(require_roles(ROLES_CONFIGURACION))):
    return _config_response(_get_or_create_config(db), _get_or_create_appearance(db))


@router.get("/apariencia", response_model=AparienciaSistemaResponse)
def obtener_apariencia_sistema(db: Session = Depends(get_db)):
    """Configuración visual pública necesaria antes y después del inicio de sesión."""
    config = _get_or_create_config(db)
    appearance = _get_or_create_appearance(db)
    return {"nombre_plataforma": config.nombre_plataforma, **{field: getattr(appearance, field) for field in ("logo_data_url", "color_primario", "color_secundario", "color_menu_inicio", "color_menu_fin", "tipografia")}}


@router.put("/", response_model=ConfiguracionSistemaResponse)
def actualizar_configuracion_sistema(data: ConfiguracionSistemaUpdate, db: Session = Depends(get_db), usuario=Depends(require_roles(ROLES_CONFIGURACION))):
    config = _get_or_create_config(db)
    appearance = _get_or_create_appearance(db)
    payload = data.model_dump(exclude_unset=True)
    appearance_fields = {"logo_data_url", "color_primario", "color_secundario", "color_menu_inicio", "color_menu_fin", "tipografia"}
    for key, value in payload.items():
        if isinstance(value, str):
            value = value.strip()
        if key in appearance_fields:
            setattr(appearance, key, value)
        else:
            setattr(config, key, value)
    config.actualizado_por = getattr(usuario, "id", None)
    db.commit()
    db.refresh(config)
    return _config_response(config, appearance)


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

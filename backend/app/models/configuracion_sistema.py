# ============================================================
# MODELO CONFIGURACIÓN SISTEMA PRO
# ERP SST PRO ENTERPRISE
# FASE 35.4.2 — Configuración Sistema PRO
# Archivo: backend/app/models/configuracion_sistema.py
# ============================================================

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func
from app.database import Base


class ConfiguracionSistema(Base):
    __tablename__ = "configuracion_sistema"

    id = Column(Integer, primary_key=True, index=True)
    nombre_plataforma = Column(String(150), nullable=False, default="ERP SST PRO")
    ambiente = Column(String(50), nullable=False, default="LOCAL")
    version = Column(String(50), nullable=False, default="1.0.0")
    dominio_frontend = Column(String(255), nullable=True)
    dominio_backend = Column(String(255), nullable=True)
    soporte_correo = Column(String(150), nullable=True)
    soporte_telefono = Column(String(80), nullable=True)
    jwt_expiracion_minutos = Column(Integer, nullable=False, default=480)
    intentos_login_maximos = Column(Integer, nullable=False, default=5)
    bloqueo_login_minutos = Column(Integer, nullable=False, default=15)
    exigir_password_fuerte = Column(Boolean, nullable=False, default=True)
    permitir_registro_publico = Column(Boolean, nullable=False, default=False)
    upload_max_mb = Column(Integer, nullable=False, default=25)
    evidencias_webp = Column(Boolean, nullable=False, default=True)
    evidencias_preview = Column(Boolean, nullable=False, default=True)
    evidencias_thumbnail = Column(Boolean, nullable=False, default=True)
    retencion_evidencias_meses = Column(Integer, nullable=False, default=60)
    smtp_activo = Column(Boolean, nullable=False, default=False)
    smtp_host = Column(String(150), nullable=True)
    smtp_puerto = Column(Integer, nullable=True)
    smtp_usuario = Column(String(150), nullable=True)
    smtp_from = Column(String(150), nullable=True)
    notificaciones_activas = Column(Boolean, nullable=False, default=True)
    backups_activos = Column(Boolean, nullable=False, default=True)
    backups_frecuencia = Column(String(50), nullable=False, default="DIARIO")
    backups_retencion_dias = Column(Integer, nullable=False, default=30)
    mantenimiento_activo = Column(Boolean, nullable=False, default=False)
    mantenimiento_mensaje = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)
    actualizado_por = Column(Integer, nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class AparienciaSistema(Base):
    __tablename__ = "apariencia_sistema"

    id = Column(Integer, primary_key=True, index=True)
    logo_data_url = Column(Text, nullable=True)
    color_primario = Column(String(7), nullable=False, default="#2563EB")
    color_secundario = Column(String(7), nullable=False, default="#1E40AF")
    color_menu_inicio = Column(String(7), nullable=False, default="#0F172A")
    color_menu_fin = Column(String(7), nullable=False, default="#1E3A8A")
    tipografia = Column(String(50), nullable=False, default="Inter")
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

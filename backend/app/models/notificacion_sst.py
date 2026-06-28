# ============================================================
# MODELO NOTIFICACIONES SST - ERP SST PRO
# FASE 1.1.24.1 — CENTRO DE NOTIFICACIONES INTELIGENTES SST
# Archivo: backend/app/models/notificacion_sst.py
# ============================================================

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class NotificacionSST(Base):
    __tablename__ = "notificaciones_sst"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=True, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="SET NULL"), nullable=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id", ondelete="SET NULL"), nullable=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)

    modulo = Column(String(80), nullable=False, index=True)
    referencia_id = Column(Integer, nullable=True, index=True)
    clave_unica = Column(String(180), nullable=True, unique=True, index=True)

    tipo = Column(String(80), nullable=False, default="ALERTA", index=True)
    prioridad = Column(String(40), nullable=False, default="MEDIA", index=True)
    estado = Column(String(40), nullable=False, default="PENDIENTE", index=True)

    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    accion_recomendada = Column(Text, nullable=True)
    url_destino = Column(String(500), nullable=True)

    fecha_evento = Column(Date, nullable=True, index=True)
    fecha_vencimiento = Column(Date, nullable=True, index=True)
    fecha_lectura = Column(DateTime(timezone=True), nullable=True)
    fecha_archivo = Column(DateTime(timezone=True), nullable=True)

    leida = Column(Boolean, nullable=False, default=False, index=True)
    archivada = Column(Boolean, nullable=False, default=False, index=True)
    activa = Column(Boolean, nullable=False, default=True, index=True)

    origen_generacion = Column(String(80), nullable=True, default="AUTOMATICA", index=True)
    metadata_json = Column(Text, nullable=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    empresa = relationship("Empresa")
    sede = relationship("Sede")
    area = relationship("Area")
    usuario = relationship("Usuario")


class ConfiguracionNotificacionSST(Base):
    __tablename__ = "configuracion_notificaciones_sst"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)

    habilitar_notificaciones = Column(Boolean, nullable=False, default=True)
    dias_alerta_vencimiento = Column(Integer, nullable=False, default=15)
    dias_alerta_critica = Column(Integer, nullable=False, default=0)

    canal_sistema = Column(Boolean, nullable=False, default=True)
    canal_email = Column(Boolean, nullable=False, default=False)
    canal_whatsapp = Column(Boolean, nullable=False, default=False)

    email_destino = Column(String(255), nullable=True)
    whatsapp_destino = Column(String(80), nullable=True)

    frecuencia_generacion = Column(String(50), nullable=False, default="DIARIA")
    hora_generacion = Column(String(20), nullable=True, default="08:00")

    activo = Column(Boolean, nullable=False, default=True, index=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    empresa = relationship("Empresa")

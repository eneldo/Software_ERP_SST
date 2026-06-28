# ============================================================
# MODELO ALERTAS MEDIDAS CORRECTIVAS SST
# ERP SST PRO - FASE 1.1.8.7.3
# Archivo: backend/app/models/alerta_medida_correctiva.py
# ============================================================
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class AlertaMedidaCorrectivaSST(Base):
    __tablename__ = "alertas_medidas_correctivas_sst"
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    capa_id = Column(Integer, ForeignKey("capas_sst.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)
    tipo_alerta = Column(String(80), nullable=False, index=True)
    prioridad = Column(String(30), nullable=False, default="MEDIA", index=True)
    estado = Column(String(30), nullable=False, default="PENDIENTE", index=True)
    titulo = Column(String(255), nullable=False)
    mensaje = Column(Text, nullable=False)
    accion_recomendada = Column(Text, nullable=True)
    url_destino = Column(String(255), nullable=True)
    leida = Column(Boolean, nullable=False, default=False)
    archivada = Column(Boolean, nullable=False, default=False)
    activa = Column(Boolean, nullable=False, default=True)
    fecha_evento = Column(DateTime(timezone=True), nullable=True)
    fecha_vencimiento = Column(DateTime(timezone=True), nullable=True)
    fecha_lectura = Column(DateTime(timezone=True), nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    empresa = relationship("Empresa")
    capa = relationship("CapaSST")
    usuario = relationship("Usuario")

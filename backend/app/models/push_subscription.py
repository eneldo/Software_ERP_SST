# ============================================================
# MODELO SUSCRIPCIÓN PUSH
# H-035: Almacena suscripciones web push de los usuarios
# ============================================================

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class PushSubscriptionModel(Base):
    __tablename__ = "push_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint = Column(Text, nullable=False, unique=True)
    p256dh = Column(Text, nullable=False, default="")
    auth = Column(Text, nullable=False, default="")
    activo = Column(Boolean, nullable=False, default=True, index=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

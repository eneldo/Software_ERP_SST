# ============================================================
# MODELO PLANTILLA NOTIFICACION SST
# H-020: Plantillas parametrizables para alertas
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class PlantillaNotificacionSST(Base):
    __tablename__ = "plantillas_notificaciones_sst"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=True, index=True)

    codigo = Column(String(80), nullable=False, index=True)
    nombre = Column(String(255), nullable=False)

    modulo = Column(String(80), nullable=False, index=True)
    tipo_evento = Column(String(80), nullable=False, index=True)
    # VENCIMIENTO, CUMPLIMIENTO, INCUMPLIMIENTO, SEGUIMIENTO, SISTEMA

    asunto = Column(String(500), nullable=False)
    cuerpo_html = Column(Text, nullable=False)
    cuerpo_plano = Column(Text, nullable=True)

    canal_sistema = Column(Boolean, default=True, nullable=False)
    canal_email = Column(Boolean, default=False, nullable=False)
    canal_whatsapp = Column(Boolean, default=False, nullable=False)

    prioridad_default = Column(String(40), default="MEDIA", nullable=False)

    variables_disponibles = Column(Text, nullable=True)
    # JSON con las variables que soporta: ["nombre_norma", "fecha_vencimiento", "responsable"]

    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    empresa = relationship("Empresa")

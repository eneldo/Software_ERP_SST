from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class PlanMejoramientoSeguimientoSST(Base):
    __tablename__ = "planes_mejoramiento_seguimientos_sst"

    id = Column(Integer, primary_key=True, index=True)

    plan_id = Column(Integer, ForeignKey("planes_mejoramiento_sst.id", ondelete="CASCADE"), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    fecha_seguimiento = Column(Date, nullable=True)

    tipo_seguimiento = Column(String(80), default="SEGUIMIENTO")
    estado_anterior = Column(String(50), nullable=True)
    estado_nuevo = Column(String(50), nullable=True)

    porcentaje_avance_anterior = Column(Integer, default=0)
    porcentaje_avance_nuevo = Column(Integer, default=0)

    observacion = Column(Text, nullable=False)
    recomendacion = Column(Text, nullable=True)
    proxima_fecha = Column(Date, nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    plan = relationship("PlanMejoramientoSST")
    empresa = relationship("Empresa")
    usuario = relationship("Usuario")
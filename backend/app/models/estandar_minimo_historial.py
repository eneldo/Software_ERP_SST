# ============================================================
# MODELO HISTORIAL ESTANDARES MINIMOS
# H-017: Registro de cambios en criterios estandares
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class EstandarMinimoHistorial(Base):
    __tablename__ = "estandares_minimos_historial"

    id = Column(Integer, primary_key=True, index=True)

    estandar_criterio_id = Column(
        Integer,
        ForeignKey("estandares_minimos_criterios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    tipo_cambio = Column(String(50), nullable=False, index=True)
    # CREACION, MODIFICACION, ACTIVACION, DESACTIVACION

    descripcion_cambio = Column(Text, nullable=False)
    valor_anterior = Column(Text, nullable=True)
    valor_nuevo = Column(Text, nullable=True)

    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    estandar_criterio = relationship("EstandarMinimoCriterio")
    empresa = relationship("Empresa")
    usuario = relationship("Usuario")

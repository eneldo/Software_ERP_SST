# ============================================================
# MODELO
# FIRMA ELECTRÓNICA SST ENTERPRISE
# FASE 1.7.4.2.4
# ============================================================

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class FirmaDigitalSST(Base):
    __tablename__ = "firmas_digitales_sst"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    nombre_firmante = Column(String(255), nullable=False)
    cargo = Column(String(255), nullable=True)

    tipo_firma = Column(String(50), default="FIRMA_PNG")

    archivo = Column(String(500), nullable=False)
    url = Column(String(500), nullable=False)

    mime_type = Column(String(120), nullable=True)
    tamano_bytes = Column(Integer, default=0)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    usuario = relationship("Usuario")
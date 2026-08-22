# ============================================================
# MODELO CONFIGURACIÓN DOCUMENTAL
# FASE 2.2.1B - Configuración Documental y Firmas PRO
# ============================================================

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class ConfiguracionDocumental(Base):
    __tablename__ = "configuracion_documental"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    logo_url = Column(String(500), nullable=True)

    firma_representante_url = Column(String(500), nullable=True)

    firma_sst_url = Column(String(500), nullable=True)

    sello_url = Column(String(500), nullable=True)

    prefijo_documental = Column(String(50), default="SGSST")

    version_documental = Column(String(20), default="1.0")

    pie_documental = Column(
        Text,
        default="Documento controlado generado desde ERP SST PRO.",
    )

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    fecha_actualizacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    empresa = relationship("Empresa")
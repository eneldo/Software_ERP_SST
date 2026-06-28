# ============================================================
# MODELO
# EVIDENCIAS FOTOGRÁFICAS HALLAZGOS AUDITORÍA SST
# FASE 1.7.4.2.2
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class AuditoriaHallazgoEvidenciaSST(Base):
    __tablename__ = "auditorias_hallazgos_evidencias"

    id = Column(Integer, primary_key=True, index=True)

    hallazgo_id = Column(
        Integer,
        ForeignKey("auditorias_hallazgos_sst.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    auditoria_id = Column(
        Integer,
        ForeignKey("auditorias_sst.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    tipo = Column(String(50), default="FOTO")
    descripcion = Column(Text, nullable=True)

    nombre_original = Column(String(255), nullable=True)
    archivo = Column(String(500), nullable=False)
    url = Column(String(500), nullable=False)
    extension = Column(String(20), nullable=True)
    mime_type = Column(String(120), nullable=True)
    tamano_bytes = Column(Integer, default=0)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    hallazgo = relationship("AuditoriaHallazgoSST")
    auditoria = relationship("AuditoriaSST")
    empresa = relationship("Empresa")
    usuario = relationship("Usuario")





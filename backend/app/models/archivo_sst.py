# ============================================================
# MODELO ARCHIVOS SST
# FASE 2.2.1A - Gestión Documental y Evidencias PRO
# ============================================================

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class ArchivoSST(Base):
    __tablename__ = "archivos_sst"

    id = Column(Integer, primary_key=True, index=True)

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

    tipo = Column(String(80), nullable=False)
    nombre_original = Column(String(255), nullable=False)
    nombre_archivo = Column(String(255), nullable=False)
    ruta = Column(String(500), nullable=False)
    url = Column(String(500), nullable=False)
    extension = Column(String(20), nullable=True)
    mime_type = Column(String(120), nullable=True)
    tamano_bytes = Column(Integer, nullable=True)

    modulo = Column(String(100), nullable=True)
    referencia_id = Column(Integer, nullable=True)

    hash_sha256 = Column(String(64), nullable=True, index=True)

    descripcion = Column(String(500), nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_descarga = Column(DateTime(timezone=True), nullable=True)

    empresa = relationship("Empresa")
    usuario = relationship("Usuario")

    __table_args__ = (
        Index("ix_archivo_sst_modulo_ref", "modulo", "referencia_id"),
    )
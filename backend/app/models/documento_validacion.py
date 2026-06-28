# ============================================================
# MODELO
# DOCUMENTOS VALIDACIÓN SST
# FASE 1.7.4.2.5
# ============================================================

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class DocumentoValidacionSST(Base):
    __tablename__ = "documentos_validacion_sst"

    id = Column(Integer, primary_key=True, index=True)

    codigo_validacion = Column(String(120), unique=True, nullable=False, index=True)
    tipo_documento = Column(String(80), nullable=False)
    referencia_id = Column(Integer, nullable=False)

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="SET NULL"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    nombre_archivo = Column(String(255), nullable=True)
    hash_sha256 = Column(String(128), nullable=False)
    url_archivo = Column(String(500), nullable=True)

    estado = Column(String(50), default="VALIDO")
    observacion = Column(Text, nullable=True)

    fecha_generacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_anulacion = Column(DateTime(timezone=True), nullable=True)

    empresa = relationship("Empresa")
    usuario = relationship("Usuario")
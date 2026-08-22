# ============================================================
# MODELO: BibliotecaDocumental
# Archivo: backend/app/models/biblioteca_documental.py
# FASE 1.8.4.3.9.2 - Centro Documental Enterprise Visual PRO
# ------------------------------------------------------------
# Tabla principal para controlar documentos SST, versiones,
# revisión, aprobación, vigencias y trazabilidad documental.
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class BibliotecaDocumental(Base):
    __tablename__ = "biblioteca_documental"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    archivo_id = Column(Integer, ForeignKey("archivos_sst.id", ondelete="SET NULL"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    codigo_documental = Column(String(80), nullable=False)
    titulo = Column(String(255), nullable=False)
    categoria = Column(String(100), nullable=False)
    tipo_documento = Column(String(80), nullable=False)

    modulo_origen = Column(String(100), nullable=True)
    version = Column(String(30), default="1.0")
    estado = Column(String(50), default="BORRADOR")

    # Campos Enterprise de control documental.
    estado_revision = Column(String(50), default="PENDIENTE")
    aprobador = Column(String(255), nullable=True)
    motivo_cambio_estado = Column(Text, nullable=True)
    ultima_revision = Column(Date, nullable=True)
    proxima_revision = Column(Date, nullable=True)

    responsable = Column(String(255), nullable=True)
    descripcion = Column(Text, nullable=True)
    palabras_clave = Column(String(500), nullable=True)

    fecha_aprobacion = Column(Date, nullable=True)
    fecha_vencimiento = Column(Date, nullable=True)

    activo = Column(Boolean, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    empresa = relationship("Empresa")
    archivo = relationship("ArchivoSST")
    usuario = relationship("Usuario")

# ============================================================
# MODELO: Firma Documental SST
# Archivo: backend/app/models/firma_documental_sst.py
# FASE 1.8.4.3.10.1 - Backend de Firma y Aprobación Digital
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class FirmaDocumentalSST(Base):
    """
    Registra la trazabilidad de firmas, aprobaciones y rechazos
    aplicados sobre documentos de la biblioteca documental SST.

    No reemplaza la firma digital del usuario. Esta tabla guarda el
    acto documental: quién firmó/aprobó/rechazó, cuándo, con qué rol,
    sobre qué documento y usando qué firma digital activa.
    """

    __tablename__ = "firmas_documentales_sst"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    documento_id = Column(Integer, ForeignKey("biblioteca_documental.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)
    firma_digital_id = Column(Integer, ForeignKey("firmas_digitales_sst.id", ondelete="SET NULL"), nullable=True)

    # RESPONSABLE_SST, GERENCIA, COORDINADOR, AUDITOR, REPRESENTANTE_LEGAL
    rol_firmante = Column(String(80), nullable=False)

    nombre_firmante = Column(String(255), nullable=False)
    cargo_firmante = Column(String(255), nullable=True)

    # FIRMA, APROBACION, RECHAZO, REVISION
    tipo_accion = Column(String(50), nullable=False, default="FIRMA")

    # PENDIENTE, FIRMADO, APROBADO, RECHAZADO, ANULADO
    estado = Column(String(50), nullable=False, default="FIRMADO")

    observaciones = Column(Text, nullable=True)
    motivo_rechazo = Column(Text, nullable=True)

    ip_origen = Column(String(80), nullable=True)
    user_agent = Column(String(500), nullable=True)

    hash_firma = Column(String(255), nullable=True)

    activo = Column(Boolean, default=True)

    fecha_firma = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    empresa = relationship("Empresa")
    documento = relationship("BibliotecaDocumental")
    usuario = relationship("Usuario")
    firma_digital = relationship("FirmaDigitalSST")

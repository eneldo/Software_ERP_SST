# ============================================================
# FASE 1.8.4.3.9
# CONTROL DE VERSIONES DOCUMENTALES
# ============================================================

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class DocumentoVersion(Base):
    __tablename__ = "documentos_versiones"

    id = Column(Integer, primary_key=True, index=True)

    documento_id = Column(
        Integer,
        ForeignKey("biblioteca_documental.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    version = Column(String(20), nullable=False)
    descripcion_cambio = Column(Text, nullable=True)
    usuario = Column(String(255), nullable=True)
    archivo_url = Column(String(500), nullable=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    documento = relationship("BibliotecaDocumental", backref="versiones")
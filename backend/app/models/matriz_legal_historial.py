# ============================================================
# MODELO HISTORIAL MODIFICACIONES NORMATIVAS
# FASE auditoría - H-003
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class MatrizLegalHistorial(Base):
    __tablename__ = "matriz_legal_historial"

    id = Column(Integer, primary_key=True, index=True)

    matriz_legal_id = Column(
        Integer,
        ForeignKey("matriz_legal_sst.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)

    tipo_cambio = Column(String(50), nullable=False)  # CREACION / MODIFICACION / DEROGACION / SUSPENSION
    descripcion_cambio = Column(Text, nullable=False)
    valor_anterior = Column(Text, nullable=True)
    valor_nuevo = Column(Text, nullable=True)

    norma_anterior = Column(String(255), nullable=True)
    estado_norma_anterior = Column(String(80), nullable=True)
    estado_norma_nuevo = Column(String(80), nullable=True)

    motivo = Column(Text, nullable=True)
    fecha_efectiva = Column(Date, nullable=True)

    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    matriz_legal = relationship("MatrizLegalSST")
    empresa = relationship("Empresa")
    usuario = relationship("Usuario")

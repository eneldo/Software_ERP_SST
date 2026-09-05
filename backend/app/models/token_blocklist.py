# ============================================================
# MODELO TOKEN BLOCKLIST
# H-013a: Revocación de tokens JWT
# ============================================================

from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.sql import func

from app.database import Base


class TokenBlocklist(Base):
    __tablename__ = "token_blocklist"

    id = Column(Integer, primary_key=True, index=True)

    jti = Column(String(36), nullable=False, unique=True, index=True)
    token_type = Column(String(20), nullable=False, default="access")
    usuario_id = Column(Integer, nullable=True, index=True)
    empresa_id = Column(Integer, nullable=True)

    motivo = Column(String(100), nullable=True)
    bloqueado_por = Column(Integer, nullable=True)

    exp = Column(DateTime(timezone=True), nullable=False, index=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_token_blocklist_jti_type", "jti", "token_type"),
    )

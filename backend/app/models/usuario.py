# ============================================================
# MODELO: USUARIO
# ERP SST PRO ENTERPRISE
# FASE HARDENING — Usuarios del Sistema PRO
# ============================================================

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)

    nombres = Column(String(255), nullable=False)
    apellidos = Column(String(255), nullable=False)
    correo = Column(String(255), unique=True, nullable=False, index=True)

    # Hash bcrypt de la contraseña. Nunca guardar texto plano.
    password = Column(String(255), nullable=False)

    rol = Column(String(50), default="ADMIN_EMPRESA", nullable=False, index=True)
    activo = Column(Boolean, default=True, nullable=False, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=True, index=True)
    empresa = relationship("Empresa")

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    ultimo_acceso = Column(DateTime(timezone=True), nullable=True)

    # H-013b: MFA TOTP
    mfa_secret = Column(String(64), nullable=True)
    mfa_enabled = Column(Boolean, default=False, nullable=False)

# ============================================================
# MODELOS EPP SST ENTERPRISE - ERP SST PRO
# FASE 1.1.7.1 — EPP SST BASE
# Archivo: backend/app/models/epp.py
# ============================================================

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class EPPCatalogo(Base):
    __tablename__ = "epp_catalogo"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)

    codigo = Column(String(50), nullable=False, index=True)
    nombre = Column(String(255), nullable=False, index=True)
    categoria = Column(String(100), nullable=True, index=True)
    descripcion = Column(Text, nullable=True)

    vida_util_dias = Column(Integer, default=365)
    requiere_reposicion = Column(Boolean, default=True)
    requiere_firma = Column(Boolean, default=True)
    requiere_evidencia = Column(Boolean, default=False)

    estado = Column(String(30), default="ACTIVO", index=True)
    activo = Column(Boolean, default=True, index=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    empresa = relationship("Empresa")
    cargo_asociaciones = relationship(
        "CargoEPPCatalogo",
        back_populates="epp",
        cascade="all, delete-orphan",
    )


class CargoEPPCatalogo(Base):
    __tablename__ = "cargo_epp_catalogo"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    cargo_id = Column(Integer, ForeignKey("cargos.id", ondelete="CASCADE"), nullable=False, index=True)
    epp_id = Column(Integer, ForeignKey("epp_catalogo.id", ondelete="CASCADE"), nullable=False, index=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    empresa = relationship("Empresa")
    cargo = relationship("Cargo", back_populates="epp_asociaciones")
    epp = relationship("EPPCatalogo", back_populates="cargo_asociaciones")

    __table_args__ = (
        UniqueConstraint("cargo_id", "epp_id", name="uq_cargo_epp_catalogo"),
    )


class EPPEntrega(Base):
    __tablename__ = "epp_entregas"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id", ondelete="CASCADE"), nullable=False, index=True)
    epp_id = Column(Integer, ForeignKey("epp_catalogo.id", ondelete="RESTRICT"), nullable=False, index=True)

    cantidad = Column(Integer, default=1)
    fecha_entrega = Column(Date, nullable=False, index=True)
    fecha_reposicion = Column(Date, nullable=True, index=True)

    talla = Column(String(50), nullable=True)
    marca = Column(String(100), nullable=True)
    modelo = Column(String(100), nullable=True)
    serial = Column(String(100), nullable=True)

    estado = Column(String(40), default="ENTREGADO", index=True)
    recibido_por_empleado = Column(Boolean, default=False)
    fecha_firma = Column(DateTime(timezone=True), nullable=True)

    observaciones = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, index=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    empresa = relationship("Empresa")
    empleado = relationship("Empleado")
    epp = relationship("EPPCatalogo")

    __table_args__ = (
        UniqueConstraint("empleado_id", "epp_id", "fecha_entrega", name="uq_epp_entrega_empleado_epp_fecha"),
    )

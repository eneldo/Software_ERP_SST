# ============================================================
# MODELO SEDE - ERP SST PRO
# FASE 1.1.2.1 — SEDES SST ENTERPRISE 360°
# ============================================================

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Sede(Base):
    __tablename__ = "sedes"

    id = Column(Integer, primary_key=True, index=True)

    # ========================================================
    # RELACIÓN EMPRESA
    # ========================================================
    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ========================================================
    # DATOS GENERALES
    # ========================================================
    nombre = Column(String(255), nullable=False)
    codigo_sede = Column(String(50), nullable=True, index=True)
    tipo_sede = Column(String(50), default="PRINCIPAL")

    # ========================================================
    # UBICACIÓN
    # ========================================================
    direccion = Column(String(255), nullable=True)
    ciudad = Column(String(100), nullable=True, index=True)
    departamento = Column(String(100), nullable=True)

    # ========================================================
    # CONTACTO
    # ========================================================
    telefono = Column(String(50), nullable=True)
    correo = Column(String(255), nullable=True)

    # ========================================================
    # RESPONSABLE
    # ========================================================
    responsable_sede = Column(String(255), nullable=True)
    cargo_responsable = Column(String(255), nullable=True)

    # ========================================================
    # INFORMACIÓN OPERATIVA
    # ========================================================
    numero_empleados = Column(Integer, default=0)

    # ========================================================
    # ESTADO
    # ========================================================
    activo = Column(Boolean, default=True, index=True)

    # ========================================================
    # AUDITORÍA
    # ========================================================
    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    fecha_actualizacion = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )

    # ========================================================
    # RELACIONES
    # ========================================================
    empresa = relationship("Empresa")
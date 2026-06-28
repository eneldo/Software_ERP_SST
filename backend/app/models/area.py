# ============================================================
# MODELO ÁREA - ERP SST PRO
# FASE 1.1.3 — ÁREAS SST ENTERPRISE 360°
# ============================================================

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Area(Base):
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True, index=True)

    # ========================================================
    # RELACIONES ORGANIZACIONALES
    # Empresa -> Sede -> Área
    # ========================================================
    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    sede_id = Column(
        Integer,
        ForeignKey("sedes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ========================================================
    # DATOS GENERALES DEL ÁREA
    # ========================================================
    nombre = Column(String(150), nullable=False, index=True)
    codigo_area = Column(String(50), nullable=True, index=True)
    descripcion = Column(String(500), nullable=True)

    # ========================================================
    # CLASIFICACIÓN SST / OPERATIVA
    # ========================================================
    tipo_area = Column(String(50), default="OPERATIVA")
    nivel_riesgo = Column(String(30), default="MEDIO")
    proceso_asociado = Column(String(150), nullable=True)

    # ========================================================
    # RESPONSABLE DEL ÁREA
    # ========================================================
    responsable_area = Column(String(255), nullable=True)
    cargo_responsable = Column(String(255), nullable=True)
    correo_responsable = Column(String(255), nullable=True)
    telefono_responsable = Column(String(50), nullable=True)

    # ========================================================
    # INDICADORES BASE
    # ========================================================
    numero_empleados = Column(Integer, default=0)

    # ========================================================
    # ESTADO
    # ========================================================
    activo = Column(Boolean, default=True, index=True)

    # ========================================================
    # AUDITORÍA
    # ========================================================
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    # ========================================================
    # RELACIONES
    # ========================================================
    empresa = relationship("Empresa")
    sede = relationship("Sede")

# ============================================================
# MODELO CARGO - ERP SST PRO
# FASE 1.1.4.1 — CARGOS SST ANALYTICS PRO
# ============================================================

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Cargo(Base):
    __tablename__ = "cargos"

    id = Column(Integer, primary_key=True, index=True)

    # Relaciones organizacionales
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="SET NULL"), nullable=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id", ondelete="SET NULL"), nullable=True, index=True)

    # Datos generales del cargo
    nombre = Column(String(180), nullable=False, index=True)
    codigo_cargo = Column(String(60), nullable=True, index=True)
    descripcion = Column(String(700), nullable=True)
    tipo_cargo = Column(String(80), default="OPERATIVO", index=True)
    proceso_asociado = Column(String(180), nullable=True)

    # Variables SST
    nivel_riesgo = Column(String(40), default="MEDIO", index=True)
    exposicion = Column(String(700), nullable=True)
    requiere_epp = Column(Boolean, default=False, index=True)
    epp_requerido = Column(String(700), nullable=True)
    examenes_medicos = Column(String(700), nullable=True)
    requiere_vigilancia_medica = Column(Boolean, nullable=False, default=False, server_default="false",index=True)
    capacitaciones_requeridas = Column(String(700), nullable=True)
    perfil_sst = Column(String(700), nullable=True)
    competencias = Column(String(700), nullable=True)
    funciones = Column(String(2000), nullable=True)
    responsabilidades = Column(String(2000), nullable=True)
    habilidades = Column(String(1000), nullable=True)
    requisitos_tecnicos = Column(String(1000), nullable=True)
    requisitos_fisicos = Column(String(1000), nullable=True)
    requisitos_mentales = Column(String(1000), nullable=True)
    riesgos_asociados = Column(String(700), nullable=True)

    # Indicadores base
    numero_empleados = Column(Integer, default=0)

    # Estado
    activo = Column(Boolean, default=True, index=True)

    # Auditoría
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    empresa = relationship("Empresa")
    sede = relationship("Sede")
    area = relationship("Area")
    epp_asociaciones = relationship(
        "CargoEPPCatalogo",
        back_populates="cargo",
        cascade="all, delete-orphan",
    )

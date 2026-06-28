# ============================================================
# MODELO INDICADOR SST - ERP SST PRO
# FASE 1.1.18.1 — NÚCLEO INDICADORES SST BI EXECUTIVE
# Archivo: backend/app/models/indicador_sst.py
# ============================================================

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class IndicadorSST(Base):
    __tablename__ = "indicadores_sst"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="SET NULL"), nullable=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id", ondelete="SET NULL"), nullable=True, index=True)
    cargo_id = Column(Integer, ForeignKey("cargos.id", ondelete="SET NULL"), nullable=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)

    codigo = Column(String(80), nullable=False, index=True)
    nombre = Column(String(255), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)

    categoria = Column(String(80), nullable=False, default="GESTION", index=True)
    tipo_indicador = Column(String(80), nullable=False, default="RESULTADO", index=True)
    origen_dato = Column(String(80), nullable=False, default="MANUAL", index=True)
    frecuencia = Column(String(50), nullable=False, default="MENSUAL", index=True)

    formula = Column(Text, nullable=True)
    unidad = Column(String(40), nullable=False, default="%")
    meta = Column(Numeric(12, 2), nullable=False, default=100)
    valor_actual = Column(Numeric(12, 2), nullable=False, default=0)
    resultado = Column(Numeric(12, 2), nullable=False, default=0)
    semaforo = Column(String(30), nullable=False, default="ROJO", index=True)
    tendencia = Column(String(30), nullable=True, default="ESTABLE")

    periodo_inicio = Column(Date, nullable=True, index=True)
    periodo_fin = Column(Date, nullable=True, index=True)
    responsable = Column(String(255), nullable=True)
    fuente = Column(String(255), nullable=True)
    observaciones = Column(Text, nullable=True)

    activo = Column(Boolean, nullable=False, default=True, index=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    empresa = relationship("Empresa")
    sede = relationship("Sede")
    area = relationship("Area")
    cargo = relationship("Cargo")
    usuario = relationship("Usuario")

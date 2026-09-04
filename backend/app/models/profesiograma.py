from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class TipoEvaluacionMedica(Base):
    __tablename__ = "tipos_evaluacion_medica"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, server_default=func.now())

    evaluaciones = relationship("ProfesiogramaEvaluacion", back_populates="tipo_evaluacion")


class ExamenEvaluacionCatalogo(Base):
    __tablename__ = "examenes_evaluacion_catalogo"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, server_default=func.now())


class Profesiograma(Base):
    __tablename__ = "profesiograma"

    id = Column(Integer, primary_key=True, index=True)
    cargo_id = Column(Integer, ForeignKey("cargos.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    riesgos_asociados = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now(), onupdate=func.now())

    cargo = relationship("Cargo")
    empresa = relationship("Empresa")
    evaluaciones = relationship("ProfesiogramaEvaluacion", back_populates="profesiograma", cascade="all, delete-orphan")


class ProfesiogramaEvaluacion(Base):
    __tablename__ = "profesiograma_evaluacion"

    id = Column(Integer, primary_key=True, index=True)
    profesiograma_id = Column(Integer, ForeignKey("profesiograma.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo_evaluacion_id = Column(Integer, ForeignKey("tipos_evaluacion_medica.id", ondelete="CASCADE"), nullable=False)
    examenes_requeridos = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)

    profesiograma = relationship("Profesiograma", back_populates="evaluaciones")
    tipo_evaluacion = relationship("TipoEvaluacionMedica", back_populates="evaluaciones")

    __table_args__ = (
        UniqueConstraint("profesiograma_id", "tipo_evaluacion_id", name="uq_profesiograma_tipo_eval"),
    )

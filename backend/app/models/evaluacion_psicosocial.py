# ============================================================
# MODELO: EVALUACIÓN PSICOSOCIAL SST
# Resolución 2646/2008 — Factores de riesgo psicosocial
# ============================================================

from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float
)
from sqlalchemy.orm import relationship

from app.database import Base


class EvaluacionPsicosocialSST(Base):
    __tablename__ = "evaluaciones_psicosociales_sst"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id"), nullable=False, index=True)

    fecha_evaluacion = Column(DateTime, nullable=False, default=datetime.utcnow)
    periodo = Column(String(20), nullable=True)  # "2026-Q1"
    evaluador = Column(String(200), nullable=True)

    # Resultados globales
    puntaje_total = Column(Float, nullable=True)
    nivel_riesgo = Column(String(30), nullable=True)  # BAJO/MODERADO/ALTO/MUY_ALTO

    # Conclusiones y recomendaciones
    conclusiones = Column(Text, nullable=True)
    recomendaciones = Column(Text, nullable=True)

    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    empresa = relationship("Empresa")
    empleado = relationship("Empleado")
    factores = relationship("FactorPsicosocialSST", back_populates="evaluacion", cascade="all, delete-orphan")


class FactorPsicosocialSST(Base):
    __tablename__ = "factores_psicosociales_sst"

    id = Column(Integer, primary_key=True, index=True)
    evaluacion_id = Column(Integer, ForeignKey("evaluaciones_psicosociales_sst.id"), nullable=False, index=True)

    # Factor (Res. 2646/2008)
    factor = Column(String(100), nullable=False)  # Ej: "Contenido del trabajo", "Carga de trabajo"
    dominio = Column(String(50), nullable=True)  # "CONTRATO", "REMUNERACION", "CAPACITACION", etc.

    # Puntuación
    puntuacion = Column(Float, nullable=True)  # 1-5 escala Likert
    nivel_riesgo = Column(String(30), nullable=True)  # BAJO/MODERADO/ALTO/MUY_ALTO
    observacion = Column(Text, nullable=True)

    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    evaluacion = relationship("EvaluacionPsicosocialSST", back_populates="factores")


# Factores predefinidos Resolución 2646/2008
FACTORES_PSICOSOCIALES = [
    {"factor": "Contenido del trabajo", "dominio": "CONTENIDO_TRABAJO"},
    {"factor": "Carga de trabajo", "dominio": "CONTENIDO_TRABAJO"},
    {"factor": "Participación en la toma de decisiones", "dominio": "CONTENIDO_TRABAJO"},
    {"factor": "Flexibilidad horaria", "dominio": "CONTENIDO_TRABAJO"},
    {"factor": "Variabilidad de funciones", "dominio": "CONTENIDO_TRABAJO"},
    {"factor": "Claridad de funciones", "dominio": "CONTENIDO_TRABAJO"},
    {"factor": "Autonomía", "dominio": "CONTENIDO_TRABAJO"},
    {"factor": "Política organizacional", "dominio": "ORGANIZACION"},
    {"factor": "Oportunidades de ascenso", "dominio": "ORGANIZACION"},
    {"factor": "Compensaciones", "dominio": "ORGANIZACION"},
    {"factor": "Nivel de responsabilidad", "dominio": "ORGANIZACION"},
    {"factor": "Calidad del liderazgo", "dominio": "RELACIONES"},
    {"factor": "Relaciones interpersonales", "dominio": "RELACIONES"},
    {"factor": "Comunicación", "dominio": "RELACIONES"},
    {"factor": "Participación en grupos", "dominio": "RELACIONES"},
    {"factor": "Apoyo del supervisor", "dominio": "RELACIONES"},
    {"factor": "Capacitación", "dominio": "CONDICIONES"},
    {"factor": "Trabajo en turnos", "dominio": "CONDICIONES"},
    {"factor": "Exposición a riesgos", "dominio": "CONDICIONES"},
    {"factor": "Condiciones físicas del ambiente", "dominio": "CONDICIONES"},
    {"factor": "Jornada de trabajo", "dominio": "CONDICIONES"},
    {"factor": "Inseguridad laboral", "dominio": "CONDICIONES"},
    {"factor": "Entorno familiar", "dominio": "TRABAJO_VIDA"},
    {"factor": "Conflictos familiares", "dominio": "TRABAJO_VIDA"},
    {"factor": "Equilibrio vida-trabajo", "dominio": "TRABAJO_VIDA"},
]

NIVELES_RIESGO_PSICOSOCIAL = ["BAJO", "MODERADO", "ALTO", "MUY_ALTO"]

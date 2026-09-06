# ============================================================
# MODELO: HISTORIA CLÍNICA OCUPACIONAL (HCO)
# Resolución 1843/2025 Art. 12 — Separada de concepto médico
# ============================================================

from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Text
)
from sqlalchemy.orm import relationship

from app.database import Base


class HistoriaClinicaOcupacional(Base):
    __tablename__ = "historias_clinicas_ocupacionales"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id"), nullable=False, index=True)
    examen_medico_id = Column(Integer, ForeignKey("examenes_medicos.id"), nullable=True, index=True)

    fecha_elaboracion = Column(DateTime, nullable=False, default=datetime.utcnow)
    medico_cargo = Column(String(200), nullable=True)
    profesiograma_id = Column(Integer, nullable=True)

    # ── ANAMNESIS ─────────────────────────────────────────────
    motivo_consulta = Column(Text, nullable=True)
    antecedentes_personales = Column(Text, nullable=True)
    antecedentes_familiares = Column(Text, nullable=True)
    antecedentes_ocupacionales = Column(Text, nullable=True)
    antecedentes_patologicos = Column(Text, nullable=True)

    # ── REVISIÓN POR SISTEMAS ─────────────────────────────────
    revision_cabeza = Column(Text, nullable=True)
    revision_ojos = Column(Text, nullable=True)
    revision_oidos = Column(Text, nullable=True)
    revision_nariz = Column(Text, nullable=True)
    revision_garganta = Column(Text, nullable=True)
    revision_cardiovascular = Column(Text, nullable=True)
    revision_respiratorio = Column(Text, nullable=True)
    revision_digestivo = Column(Text, nullable=True)
    revision_genitourinario = Column(Text, nullable=True)
    revision_musculoesqueletico = Column(Text, nullable=True)
    revision_neurologico = Column(Text, nullable=True)
    revision_piel = Column(Text, nullable=True)
    revision_psiquiatrico = Column(Text, nullable=True)

    # ── EXAMEN FÍSICO ────────────────────────────────────────
    signos_vitales = Column(Text, nullable=True)  # TA, FC, FR, Temp, Peso, Talla, IMC
    examen_fisico_general = Column(Text, nullable=True)
    examen_cabeza_cuello = Column(Text, nullable=True)
    examen_torax = Column(Text, nullable=True)
    examen_abdomen = Column(Text, nullable=True)
    examen_extremidades = Column(Text, nullable=True)
    examen_neurologico = Column(Text, nullable=True)

    # ── HISTORIA LABORAL ─────────────────────────────────────
    cargo_actual = Column(String(200), nullable=True)
    fecha_ingreso = Column(DateTime, nullable=True)
    tiempo_exposicion = Column(String(50), nullable=True)
    factores_riesgo = Column(Text, nullable=True)  # JSON array de factores
    controles_expuestos = Column(Text, nullable=True)
    elementos_proteccion = Column(Text, nullable=True)

    # ── IMPRESIÓN DIAGNÓSTICA ─────────────────────────────────
    diagnostico = Column(Text, nullable=True)
    cie10 = Column(String(20), nullable=True)
    plan_accion = Column(Text, nullable=True)

    # ── CONCEPTO MÉDICO (RESERVADO — solo médico) ────────────
    concepto_medico = Column(Text, nullable=True)
    aptitud = Column(String(50), nullable=True)  # APTO/NO_APTO/APTO_CON_RESTRICCIONES
    restricciones_laborales = Column(Text, nullable=True)
    recomendaciones = Column(Text, nullable=True)

    # ── SEGUIMIENTO ──────────────────────────────────────────
    proximo_control = Column(DateTime, nullable=True)
    observaciones_seguimiento = Column(Text, nullable=True)

    # ── CONSENTIMIENTO (Ley 1581/2012) ───────────────────────
    consentimiento_obtenido = Column(Boolean, default=False)
    fecha_consentimiento = Column(DateTime, nullable=True)

    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    empresa = relationship("Empresa")
    empleado = relationship("Empleado")
    examen_medico = relationship("ExamenMedico")

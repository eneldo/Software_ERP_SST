# ============================================================
# TESTS: H-011 Evaluación Psicosocial + Historia Clínica Ocupacional
# ============================================================

import pytest
from unittest.mock import MagicMock

from app.models.evaluacion_psicosocial import (
    EvaluacionPsicosocialSST,
    FactorPsicosocialSST,
    FACTORES_PSICOSOCIALES,
    NIVELES_RIESGO_PSICOSOCIAL,
)
from app.models.historia_clinica_ocupacional import HistoriaClinicaOcupacional


class TestH011Psicosocial:
    def test_evaluacion_psicosocial_model_fields(self):
        columns = {c.name for c in EvaluacionPsicosocialSST.__table__.columns}
        required = [
            "empresa_id", "empleado_id", "fecha_evaluacion", "periodo",
            "evaluador", "puntaje_total", "nivel_riesgo",
            "conclusiones", "recomendaciones", "activo",
        ]
        for field in required:
            assert field in columns, f"Campo {field} no encontrado"

    def test_factor_psicosocial_model_fields(self):
        columns = {c.name for c in FactorPsicosocialSST.__table__.columns}
        required = ["evaluacion_id", "factor", "dominio", "puntuacion", "nivel_riesgo"]
        for field in required:
            assert field in columns, f"Campo {field} no encontrado"

    def test_factores_catalogo_has_25_items(self):
        assert len(FACTORES_PSICOSOCIALES) == 25

    def test_factores_cover_all_dominios(self):
        dominios = {f["dominio"] for f in FACTORES_PSICOSOCIALES}
        assert dominios == {
            "CONTENIDO_TRABAJO", "ORGANIZACION", "RELACIONES",
            "CONDICIONES", "TRABAJO_VIDA",
        }

    def test_niveles_riesgo_has_4_values(self):
        assert len(NIVELES_RIESGO_PSICOSOCIAL) == 4
        assert "BAJO" in NIVELES_RIESGO_PSICOSOCIAL
        assert "MUY_ALTO" in NIVELES_RIESGO_PSICOSOCIAL


class TestH011HCO:
    def test_hco_model_fields(self):
        columns = {c.name for c in HistoriaClinicaOcupacional.__table__.columns}
        required = [
            "empresa_id", "empleado_id", "examen_medico_id",
            "fecha_elaboracion", "medico_cargo",
            "motivo_consulta", "antecedentes_personales",
            "antecedentes_familiares", "antecedentes_ocupacionales",
            "diagnostico", "cie10",
            "concepto_medico", "aptitud", "restricciones_laborales",
            "consentimiento_obtenido", "activo",
        ]
        for field in required:
            assert field in columns, f"Campo {field} no encontrado"

    def test_hco_has_review_systems_fields(self):
        columns = {c.name for c in HistoriaClinicaOcupacional.__table__.columns}
        systems = [
            "revision_cabeza", "revision_ojos", "revision_oidos",
            "revision_cardiovascular", "revision_respiratorio",
            "revision_musculoesqueletico", "revision_neurologico",
            "revision_piel", "revision_psiquiatrico",
        ]
        for field in systems:
            assert field in columns, f"Campo {field} no encontrado"

    def test_hco_has_physical_exam_fields(self):
        columns = {c.name for c in HistoriaClinicaOcupacional.__table__.columns}
        exams = [
            "signos_vitales", "examen_fisico_general",
            "examen_cabeza_cuello", "examen_torax",
            "examen_abdomen", "examen_extremidades",
        ]
        for field in exams:
            assert field in columns, f"Campo {field} no encontrado"

    def test_hco_has_consent_fields(self):
        columns = {c.name for c in HistoriaClinicaOcupacional.__table__.columns}
        assert "consentimiento_obtenido" in columns
        assert "fecha_consentimiento" in columns

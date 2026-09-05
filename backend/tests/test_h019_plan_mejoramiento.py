# ============================================================
# TESTS: H-019 Plan Mejoramiento - Tenant Seguimientos/Evidencias
# ============================================================

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from app.models.plan_mejoramiento import PlanMejoramientoSST
from app.models.plan_mejoramiento_seguimiento import PlanMejoramientoSeguimientoSST
from app.models.plan_mejoramiento_evidencia import PlanMejoramientoEvidenciaSST


class TestH019PlanMejoramientoTenant:
    def test_plan_model_has_origen_hallazgo(self):
        columns = {c.name for c in PlanMejoramientoSST.__table__.columns}
        assert "origen_hallazgo" in columns
        assert "origen_id" in columns

    def test_plan_model_has_verificacion(self):
        columns = {c.name for c in PlanMejoramientoSST.__table__.columns}
        assert "verificado_por" in columns
        assert "fecha_verificacion" in columns
        assert "resultado_verificacion" in columns

    def test_plan_model_has_evidencia(self):
        columns = {c.name for c in PlanMejoramientoSST.__table__.columns}
        assert "evidencia" in columns
        assert "fecha_cierre" in columns

    def test_seguimiento_model_has_empresa_id(self):
        columns = {c.name for c in PlanMejoramientoSeguimientoSST.__table__.columns}
        assert "empresa_id" in columns
        assert "plan_id" in columns

    def test_evidencia_model_has_empresa_id(self):
        columns = {c.name for c in PlanMejoramientoEvidenciaSST.__table__.columns}
        assert "empresa_id" in columns
        assert "plan_id" in columns
        assert "tipo_evidencia" in columns

    def test_seguimiento_model_has_usuario_id(self):
        columns = {c.name for c in PlanMejoramientoSeguimientoSST.__table__.columns}
        assert "usuario_id" in columns

    def test_evidencia_model_has_archivo_id(self):
        columns = {c.name for c in PlanMejoramientoEvidenciaSST.__table__.columns}
        assert "archivo_id" in columns

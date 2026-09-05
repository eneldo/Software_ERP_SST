# ============================================================
# TESTS: H-017 Estándares Mínimos + Historial
# ============================================================

import pytest
from unittest.mock import MagicMock

from app.models.estandar_minimo_criterio import EstandarMinimoCriterio
from app.models.estandar_minimo_historial import EstandarMinimoHistorial
from app.schemas.estandar_minimo_schema import (
    EstandarMinimoCriterioCreate,
    EstandarMinimoCriterioResponse,
    EstandarMinimoHistorialResponse,
)


class TestH017Estandares:
    def test_model_estandar_has_fields(self):
        columns = {c.name for c in EstandarMinimoCriterio.__table__.columns}
        required = [
            "id", "tipo_estandares", "estandar", "numeral",
            "criterio", "puntaje", "version_norma", "activo",
        ]
        for field in required:
            assert field in columns, f"Campo {field} no encontrado"

    def test_model_historial_has_fields(self):
        columns = {c.name for c in EstandarMinimoHistorial.__table__.columns}
        required = [
            "id", "estandar_criterio_id", "empresa_id", "usuario_id",
            "tipo_cambio", "descripcion_cambio", "valor_anterior", "valor_nuevo",
        ]
        for field in required:
            assert field in columns, f"Campo {field} no encontrado"

    def test_historial_has_required_columns(self):
        columns = {c.name for c in EstandarMinimoHistorial.__table__.columns}
        assert "estandar_criterio_id" in columns
        assert "empresa_id" in columns

    def test_schema_create_fields(self):
        data = EstandarMinimoCriterioCreate(
            estandar="Estándar 1",
            numeral="1.1",
            criterio="Criterio de prueba",
        )
        assert data.tipo_estandares == "7"
        assert data.puntaje == 1
        assert data.version_norma == "0312-2019"

    def test_schema_response_fields(self):
        fields = set(EstandarMinimoCriterioResponse.model_fields.keys())
        assert "estandar" in fields
        assert "numeral" in fields
        assert "criterio" in fields
        assert "puntaje" in fields

    def test_historial_response_fields(self):
        fields = set(EstandarMinimoHistorialResponse.model_fields.keys())
        assert "tipo_cambio" in fields
        assert "descripcion_cambio" in fields
        assert "valor_anterior" in fields
        assert "valor_nuevo" in fields

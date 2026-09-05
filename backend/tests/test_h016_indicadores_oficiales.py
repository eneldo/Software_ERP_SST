# ============================================================
# TESTS: H-016 Indicadores Oficiales SST
# TF, TG, TI, Mortalidad, Ausentismo
# ============================================================

import pytest
from datetime import date
from unittest.mock import MagicMock, patch, PropertyMock

from app.services.indicadores_oficiales_service import (
    calcular_tasa_frecuencia,
    calcular_tasa_gravedad,
    calcular_tasa_incapacidad,
    calcular_tasa_mortalidad,
    calcular_tasa_ausentismo,
    calcular_indicadores_oficiales,
    _obtener_empleados_activos,
)


class TestH016IndicadoresOficiales:
    def test_tasa_frecuencia_zero(self):
        db = MagicMock()
        mock_query = MagicMock()
        db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 0

        result = calcular_tasa_frecuencia(db, 1, date(2026, 1, 1), date(2026, 1, 31))

        assert result["indicador"] == "TF"
        assert result["nombre"] == "Tasa de Frecuencia"
        assert result["resultado"] == 0
        assert result["accidentes"] == 0

    def test_tasa_gravedad_structure(self):
        db = MagicMock()
        mock_query = MagicMock()
        db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.scalar.return_value = 0

        result = calcular_tasa_gravedad(db, 1, date(2026, 1, 1), date(2026, 1, 31))

        assert result["indicador"] == "TG"
        assert result["nombre"] == "Tasa de Gravedad"
        assert "unidad" in result
        assert "formula" in result
        assert "periodo" in result

    def test_tasa_incapacidad_structure(self):
        db = MagicMock()
        mock_query = MagicMock()
        db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.scalar.return_value = 0

        result = calcular_tasa_incapacidad(db, 1, date(2026, 1, 1), date(2026, 1, 31))

        assert result["indicador"] == "TI"
        assert result["unidad"] == "%"
        assert "periodo" in result

    def test_tasa_mortalidad_structure(self):
        db = MagicMock()
        mock_query = MagicMock()
        db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.scalar.return_value = 0

        result = calcular_tasa_mortalidad(db, 1, date(2026, 1, 1), date(2026, 12, 31))

        assert result["indicador"] == "MORTALIDAD"
        assert result["unidad"] == "por 1000 empleados"
        assert "periodo" in result

    def test_tasa_ausentismo_structure(self):
        db = MagicMock()
        mock_query = MagicMock()
        db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 0

        result = calcular_tasa_ausentismo(db, 1, date(2026, 1, 1), date(2026, 1, 31))

        assert result["indicador"] == "AUSENTISMO"
        assert result["unidad"] == "%"
        assert "periodo" in result

    def test_indicadores_oficiales_returns_all_five(self):
        db = MagicMock()
        mock_query = MagicMock()
        db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.scalar.return_value = 0

        result = calcular_indicadores_oficiales(db, 1, date(2026, 1, 1), date(2026, 12, 31))

        assert "tasa_frecuencia" in result
        assert "tasa_gravedad" in result
        assert "tasa_incapacidad" in result
        assert "mortalidad" in result
        assert "ausentismo" in result

    def test_empleado_model_has_jornada(self):
        from app.models.empleado import Empleado
        columns = {c.name for c in Empleado.__table__.columns}
        assert "jornada_laboral_diaria" in columns

    def test_ausentismo_model_exists(self):
        from app.models.ausentismo_sst import AusentismoSST
        assert AusentismoSST.__tablename__ == "ausentismo_sst"
        columns = {c.name for c in AusentismoSST.__table__.columns}
        assert "tipo_ausentismo" in columns
        assert "dias_ausentismo" in columns
        assert "fecha_inicio" in columns
        assert "empresa_id" in columns

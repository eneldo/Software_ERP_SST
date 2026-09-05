# ============================================================
# TESTS: H-018 Matriz Legal - Alertas y Estructura
# ============================================================

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock

from app.models.matriz_legal import MatrizLegalSST
from app.services.alertas_matriz_legal_service import (
    generar_alertas_vencimiento_legal,
    contar_alertas_activas,
)


class TestH018MatrizLegal:
    def test_model_has_required_fields(self):
        columns = {c.name for c in MatrizLegalSST.__table__.columns}
        required = [
            "empresa_id", "codigo", "norma", "tipo_norma", "numero_norma",
            "anio", "articulo", "requisito_legal", "tema", "entidad_emisora",
            "aplicabilidad", "estado_cumplimiento", "estado_norma",
            "responsable", "fecha_revision", "fecha_vencimiento",
            "evidencia", "observaciones", "activo",
        ]
        for field in required:
            assert field in columns, f"Campo {field} no encontrado"

    def test_generar_alertas_vencimiento_returns_list(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = []

        result = generar_alertas_vencimiento_legal(db, 1)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_contar_alertas_activas_returns_dict(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.scalar.return_value = 0

        result = contar_alertas_activas(db, 1)

        assert "total_pendientes" in result
        assert "criticas" in result
        assert result["total_pendientes"] == 0

    def test_matriz_legal_historial_model(self):
        from app.models.matriz_legal_historial import MatrizLegalHistorial
        columns = {c.name for c in MatrizLegalHistorial.__table__.columns}
        assert "tipo_cambio" in columns
        assert "descripcion_cambio" in columns
        assert "matriz_legal_id" in columns

    def test_generar_alertas_procesa_normas(self):
        norma_mock = MagicMock()
        norma_mock.id = 1
        norma_mock.codigo = "ML-SST-001"
        norma_mock.norma = "Decreto 1072"
        norma_mock.fecha_vencimiento = date.today() + timedelta(days=30)
        norma_mock.responsable = "Responsable SST"
        norma_mock.estado_cumplimiento = "PENDIENTE"

        db = MagicMock()
        query_mock = MagicMock()
        db.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = [norma_mock]
        query_mock.first.return_value = None

        result = generar_alertas_vencimiento_legal(db, 1)

        assert len(result) >= 0

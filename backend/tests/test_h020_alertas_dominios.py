# ============================================================
# TESTS: H-020 Alertas 11 dominios + Plantillas
# ============================================================

import pytest
from unittest.mock import MagicMock

from app.models.notificacion_sst import NotificacionSST, ConfiguracionNotificacionSST
from app.models.plantilla_notificacion_sst import PlantillaNotificacionSST
from app.services.alertas_inteligentes_service import (
    DOMAINS,
    generar_alertas_inteligentes,
    _crear_notificacion,
)


class TestH020AlertasDominios:
    def test_domains_has_11_items(self):
        assert len(DOMAINS) == 11

    def test_domains_include_all_sst_modules(self):
        required = [
            "CAPA", "INSPECCIONES", "HALLAZGOS", "INCIDENTES",
            "EXAMENES", "EPP", "CAPACITACIONES", "AUDITORIAS",
            "PLAN_MEJORAMIENTO", "MATRIZ_LEGAL", "PORTAL_EMPLEADO",
        ]
        for domain in required:
            assert domain in DOMAINS

    def test_notificacion_sst_model_fields(self):
        columns = {c.name for c in NotificacionSST.__table__.columns}
        assert "modulo" in columns
        assert "referencia_id" in columns
        assert "clave_unica" in columns
        assert "prioridad" in columns
        assert "tipo" in columns

    def test_configuracion_notificacion_fields(self):
        columns = {c.name for c in ConfiguracionNotificacionSST.__table__.columns}
        assert "canal_sistema" in columns
        assert "canal_email" in columns
        assert "canal_whatsapp" in columns
        assert "dias_alerta_vencimiento" in columns

    def test_plantilla_notificacion_fields(self):
        columns = {c.name for c in PlantillaNotificacionSST.__table__.columns}
        required = [
            "empresa_id", "codigo", "nombre", "modulo", "tipo_evento",
            "asunto", "cuerpo_html", "cuerpo_plano",
            "canal_sistema", "canal_email", "canal_whatsapp",
            "prioridad_default", "variables_disponibles",
        ]
        for field in required:
            assert field in columns, f"Campo {field} no encontrado"

    def test_plantilla_has_empresa_id(self):
        columns = {c.name for c in PlantillaNotificacionSST.__table__.columns}
        assert "empresa_id" in columns

    def test_generar_alertas_returns_dict(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = []
        db.query.return_value.filter.return_value.first.return_value = None

        result = generar_alertas_inteligentes(db, 1)

        assert "total_generadas" in result
        assert "dominios" in result
        assert isinstance(result["dominios"], list)

    def test_crear_notificacion_dedup(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = MagicMock()

        result = _crear_notificacion(
            db, 1, "CAPA", "TEST", "Test", "Desc",
        )

        assert result is None

from datetime import date
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from app.core.default_permissions import PERM_CONCEPTO_MEDICO, PERM_HISTORIA_CLINICA
from app.routers.examenes_medicos import _sanitizar_respuesta_medica
from app.schemas.examen_medico_schema import ExamenMedicoResponse


def _respuesta():
    return ExamenMedicoResponse(
        id=1, empleado_id=5, tipo_examen="INGRESO",
        fecha_examen=date(2026, 1, 1), concepto="APTO",
        restricciones="R", observaciones="O",
        medico_ocupacional="Dr. X", entidad_salud="IPS",
    )


def _permisos(historia: bool, concepto: bool):
    def _tiene(_db, _usuario, permiso):
        if permiso == PERM_HISTORIA_CLINICA:
            return historia
        if permiso == PERM_CONCEPTO_MEDICO:
            return concepto
        return False
    return _tiene


class ConceptoMedicoTest(TestCase):
    @patch("app.routers.examenes_medicos.user_has_permission")
    def test_historia_subsume_concepto(self, mock_perm):
        mock_perm.side_effect = _permisos(historia=True, concepto=False)
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        resp = _sanitizar_respuesta_medica(_respuesta(), usuario, MagicMock())

        self.assertEqual(resp.concepto, "APTO")
        self.assertEqual(resp.restricciones, "R")

    @patch("app.routers.examenes_medicos.user_has_permission")
    def test_sin_ambos_oculta_todo(self, mock_perm):
        mock_perm.side_effect = _permisos(historia=False, concepto=False)
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        resp = _sanitizar_respuesta_medica(_respuesta(), usuario, MagicMock())

        self.assertNotEqual(resp.concepto, "APTO")
        self.assertNotEqual(resp.restricciones, "R")
        self.assertIsNone(resp.examenes_aplicados)

    @patch("app.routers.examenes_medicos.user_has_permission")
    def test_con_ambos_muestra_todo(self, mock_perm):
        mock_perm.side_effect = _permisos(historia=True, concepto=True)
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        resp = _sanitizar_respuesta_medica(_respuesta(), usuario, MagicMock())

        self.assertEqual(resp.concepto, "APTO")
        self.assertEqual(resp.restricciones, "R")


if __name__ == "__main__":
    import unittest
    unittest.main()

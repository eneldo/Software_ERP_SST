from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from app.routers import plan_mejoramiento as router


def _usuario():
    return SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")


class PlanMejoramientoTenantTest(TestCase):
    @patch.object(router, "listar_planes", return_value=[])
    def test_listar_rechaza_empresa_ajena(self, mock_listar):
        db = MagicMock()

        with self.assertRaises(HTTPException) as ctx:
            router.listar_acciones_mejoramiento(empresa_id=2, db=db, usuario=_usuario())

        self.assertEqual(ctx.exception.status_code, 403)
        mock_listar.assert_not_called()

    @patch.object(router, "dashboard_plan_mejoramiento")
    def test_dashboard_rechaza_empresa_ajena(self, mock_dash):
        mock_dash.return_value = MagicMock()
        db = MagicMock()

        with self.assertRaises(HTTPException) as ctx:
            router.dashboard_plan(empresa_id=2, db=db, usuario=_usuario())

        self.assertEqual(ctx.exception.status_code, 403)
        mock_dash.assert_not_called()

    @patch.object(router, "obtener_plan_o_404")
    def test_obtener_rechaza_plan_ajeno(self, mock_obtener):
        mock_obtener.return_value = SimpleNamespace(id=3, empresa_id=2)
        db = MagicMock()

        with self.assertRaises(HTTPException) as ctx:
            router.obtener_accion_mejoramiento(plan_id=3, db=db, usuario=_usuario())

        self.assertEqual(ctx.exception.status_code, 404)


if __name__ == "__main__":
    import unittest
    unittest.main()

from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from app.routers.examenes_medicos import dashboard_examenes_medicos


class DashboardConceptoTest(TestCase):
    @patch("app.routers.examenes_medicos.user_has_permission", return_value=False)
    @patch("app.routers.examenes_medicos._query_examenes_filtrada")
    def test_empleado_sin_concepto_rechaza_403(self, mock_query, mock_perm):
        mock_query.return_value.all.return_value = []
        db = MagicMock()
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as ctx:
            dashboard_examenes_medicos(empleado_id=5, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 403)

    @patch("app.routers.examenes_medicos.user_has_permission")
    @patch("app.routers.examenes_medicos._query_examenes_filtrada")
    def test_empleado_con_concepto_permite(self, mock_query, mock_perm):
        from app.core.default_permissions import PERM_CONCEPTO_MEDICO

        def _tiene(_db, _usuario, permiso):
            return permiso == PERM_CONCEPTO_MEDICO

        mock_perm.side_effect = _tiene
        mock_query.return_value.all.return_value = []
        db = MagicMock()
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        resp = dashboard_examenes_medicos(empleado_id=5, db=db, usuario=usuario)

        self.assertIn("kpis", resp)


if __name__ == "__main__":
    import unittest
    unittest.main()

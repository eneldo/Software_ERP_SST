# ============================================================
# TEST H-008 — Exportaciones ownership (tenant validation)
# Cobertura: exportaciones_sst.py (politica, evaluacion-inicial)
#             reporte_evidencias.py (todos los endpoints)
# ============================================================

import unittest
from unittest.mock import MagicMock, patch


class FakeUsuario:
    def __init__(self, id=1, empresa_id=1, rol="ADMIN_EMPRESA"):
        self.id = id
        self.empresa_id = empresa_id
        self.rol = rol


class FakeSuperAdmin:
    def __init__(self, id=99, empresa_id=None, rol="SUPER_ADMIN"):
        self.id = id
        self.empresa_id = empresa_id
        self.rol = rol


class ExportacionesTenantTest(unittest.TestCase):
    """Valida que exportaciones_sst.py rechaza acceso cross-tenant."""

    def setUp(self):
        from app.routers.exportaciones_sst import _empresa_id_autorizada
        self._check = _empresa_id_autorizada

    def test_empresa_diferente_rechazada(self):
        usuario = FakeUsuario(empresa_id=1)
        with self.assertRaises(Exception) as ctx:
            self._check(usuario, empresa_id=2)
        self.assertIn("403", str(ctx.exception.status_code))

    def test_super_admin_accede_cualquier_empresa(self):
        admin = FakeSuperAdmin()
        resultado = self._check(admin, empresa_id=999)
        self.assertEqual(resultado, 999)

    def test_usuario_sin_empresa_rechazado(self):
        usuario = FakeUsuario(empresa_id=None)
        with self.assertRaises(Exception) as ctx:
            self._check(usuario, empresa_id=1)
        self.assertIn("403", str(ctx.exception.status_code))

    def test_misma_empresa_permitida(self):
        usuario = FakeUsuario(empresa_id=5)
        resultado = self._check(usuario, empresa_id=5)
        self.assertEqual(resultado, 5)


class ReporteEvidenciasTenantTest(unittest.TestCase):
    """Valida que reporte_evidencias.py valida tenant en _obtener_reporte."""

    def setUp(self):
        from app.routers.reporte_evidencias import _obtener_reporte, _empresa_id_autorizada
        self._obtener = _obtener_reporte
        self._check = _empresa_id_autorizada

    def test_check_rechaza_otra_empresa(self):
        usuario = FakeUsuario(empresa_id=1)
        with self.assertRaises(Exception) as ctx:
            self._check(usuario, empresa_id=2)
        self.assertEqual(ctx.exception.status_code, 403)

    @patch("app.database.get_db")
    def test_obtener_reporte_rechaza_otro_tenant(self, _mock_db):
        from sqlalchemy.orm import Session
        mock_db = MagicMock(spec=Session)
        fake_reporte = MagicMock()
        fake_reporte.empresa_id = 2
        mock_db.query.return_value.filter.return_value.first.return_value = fake_reporte

        usuario = FakeUsuario(empresa_id=1)
        with self.assertRaises(Exception) as ctx:
            self._obtener(mock_db, 1, usuario)
        self.assertEqual(ctx.exception.status_code, 403)

    @patch("app.database.get_db")
    def test_obtener_reporte_sin_usuario_no_valida(self, _mock_db):
        from sqlalchemy.orm import Session
        mock_db = MagicMock(spec=Session)
        fake_reporte = MagicMock()
        fake_reporte.empresa_id = 2
        mock_db.query.return_value.filter.return_value.first.return_value = fake_reporte

        result = self._obtener(mock_db, 1, None)
        self.assertEqual(result.empresa_id, 2)


class NotificacionesTenantTest(unittest.TestCase):
    """Valida que notificaciones_sst.py valida tenant en obtener y configuración."""

    def setUp(self):
        from app.routers.notificaciones_sst import _empresa_id_autorizada
        self._check = _empresa_id_autorizada

    def test_empresa_diferente_rechazada(self):
        usuario = FakeUsuario(empresa_id=1)
        with self.assertRaises(Exception) as ctx:
            self._check(usuario, empresa_id=2)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_super_admin_accede(self):
        admin = FakeSuperAdmin()
        result = self._check(admin, empresa_id=50)
        self.assertEqual(result, 50)


if __name__ == "__main__":
    unittest.main()

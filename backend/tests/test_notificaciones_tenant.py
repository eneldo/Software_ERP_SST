from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock

from fastapi import HTTPException

from app.routers.notificaciones_sst import dashboard_notificaciones, listar_notificaciones


def _q(items):
    q = MagicMock()
    q.options.return_value = q
    q.filter.return_value = q
    q.order_by.return_value = q
    q.limit.return_value = q
    q.all.return_value = items
    return q


class NotificacionesTenantTest(TestCase):
    def test_listar_rechaza_empresa_ajena(self):
        db = MagicMock()
        db.query.return_value = _q([])
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as ctx:
            listar_notificaciones(empresa_id=2, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 403)

    def test_dashboard_rechaza_empresa_ajena(self):
        db = MagicMock()
        db.query.return_value = _q([])
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as ctx:
            dashboard_notificaciones(empresa_id=2, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 403)


if __name__ == "__main__":
    import unittest
    unittest.main()

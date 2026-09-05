from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock

from fastapi import HTTPException

from app.routers.dashboard_ejecutivo import dashboard_ejecutivo_sst


def _query_mock(count_value=0, all_value=None):
    q = MagicMock()
    q.filter.return_value = q
    q.filter_by.return_value = q
    q.count.return_value = count_value
    q.order_by.return_value = q
    q.limit.return_value = q
    q.all.return_value = all_value if all_value is not None else []
    q.first.return_value = SimpleNamespace(id=1, nombre="Empresa 1")
    return q


class DashboardTenantTest(TestCase):
    def test_no_superadmin_sin_empresa_rechaza_403(self):
        db = MagicMock()
        db.query.side_effect = lambda *a, **k: _query_mock()
        usuario = SimpleNamespace(id=10, empresa_id=None, rol="ADMIN_EMPRESA")

        with self.assertRaises(HTTPException) as ctx:
            dashboard_ejecutivo_sst(empresa_id=None, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 403)

    def test_no_superadmin_otra_empresa_rechaza_403(self):
        db = MagicMock()
        db.query.side_effect = lambda *a, **k: _query_mock()
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as ctx:
            dashboard_ejecutivo_sst(empresa_id=2, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 403)

    def test_kpis_reflejan_datos_reales(self):
        from app.models.capacitacion import CapacitacionSST
        from app.models.inspeccion import InspeccionSST
        from app.models.incidente import IncidenteAccidenteSST
        from app.models.plan_mejoramiento import PlanMejoramientoSST

        conteos = {
            "capacitacion": 3,
            "inspeccion": 5,
            "accidente": 2,
            "plan": 7,
        }

        def _query_por_modelo(modelo, *a, **k):
            if modelo is CapacitacionSST:
                return _query_mock(conteos["capacitacion"])
            if modelo is InspeccionSST:
                return _query_mock(conteos["inspeccion"])
            if modelo is IncidenteAccidenteSST:
                return _query_mock(conteos["accidente"])
            if modelo is PlanMejoramientoSST:
                return _query_mock(conteos["plan"])
            return _query_mock(1)

        db = MagicMock()
        db.query.side_effect = _query_por_modelo
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="ADMIN_EMPRESA")

        resp = dashboard_ejecutivo_sst(empresa_id=1, db=db, usuario=usuario)
        kpis = {k["codigo"]: k["valor"] for k in resp["kpis"]}

        self.assertEqual(kpis["CAP"], conteos["capacitacion"])
        self.assertEqual(kpis["INS"], conteos["inspeccion"])
        self.assertEqual(kpis["ACC"], conteos["accidente"])
        self.assertEqual(kpis["ACP"], conteos["plan"])


if __name__ == "__main__":
    import unittest
    unittest.main()

from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock

from fastapi import HTTPException

from app.routers.inspecciones_exportaciones import excel_general, hallazgos_excel


class InspeccionesExportTenantTest(TestCase):
    def test_excel_general_rechaza_empresa_ajena(self):
        db = MagicMock()
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as ctx:
            excel_general(empresa_id=2, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 403)

    def test_hallazgos_excel_rechaza_empresa_ajena(self):
        db = MagicMock()
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as ctx:
            hallazgos_excel(empresa_id=2, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 403)


if __name__ == "__main__":
    import unittest
    unittest.main()

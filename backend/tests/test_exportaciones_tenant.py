from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from app.routers.exportaciones_sst import (
    _empresa_id_autorizada,
    exportar_objetivos_pdf,
)


class ExportacionesTenantTest(TestCase):
    def test_helper_rechaza_empresa_ajena(self):
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="ADMIN_EMPRESA")

        with self.assertRaises(HTTPException) as ctx:
            _empresa_id_autorizada(usuario, 2)

        self.assertEqual(ctx.exception.status_code, 403)

    @patch("app.routers.exportaciones_sst.generar_pdf_corporativo")
    def test_export_objetivos_rechaza_empresa_ajena(self, mock_pdf):
        mock_pdf.return_value = MagicMock()
        db = MagicMock()
        db.query.return_value.filter.return_value.first.side_effect = [
            SimpleNamespace(id=2, nombre="Empresa 2"),
            None,
        ]
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="ADMIN_EMPRESA")

        with self.assertRaises(HTTPException) as ctx:
            exportar_objetivos_pdf(empresa_id=2, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 403)
        mock_pdf.assert_not_called()


if __name__ == "__main__":
    import unittest
    unittest.main()

from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from app.routers.inspecciones_exportaciones_platinum import (
    exportar_inspeccion_pdf_platinum,
)


class PlatinumExportTenantTest(TestCase):
    @patch(
        "app.routers.inspecciones_exportaciones_platinum"
        ".generar_reporte_inspeccion_platinum_pdf"
    )
    def test_export_rechaza_inspeccion_ajena(self, mock_generar):
        mock_generar.return_value = b"%PDF-1.4"
        db = MagicMock()
        # La BD, con filtro (id, empresa_id), no devuelve la inspección ajena.
        db.query.return_value.filter.return_value.first.return_value = None
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="AUDITOR")

        with self.assertRaises(HTTPException) as ctx:
            exportar_inspeccion_pdf_platinum(
                inspeccion_id=9, db=db, usuario_actual=usuario
            )

        self.assertEqual(ctx.exception.status_code, 404)
        mock_generar.assert_not_called()
        filtros = db.query.return_value.filter.call_args.args
        self.assertEqual(len(filtros), 2)


if __name__ == "__main__":
    import unittest
    unittest.main()

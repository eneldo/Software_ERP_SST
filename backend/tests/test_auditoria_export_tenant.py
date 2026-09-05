from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from app.routers.auditoria_pdf import exportar_pdf_auditoria_sst


class AuditoriaExportTenantTest(TestCase):
    @patch("app.routers.auditoria_pdf.generar_pdf_auditoria")
    def test_export_rechaza_auditoria_ajena(self, mock_generar):
        mock_generar.return_value = b"%PDF-1.4"
        db = MagicMock()
        # La BD, con filtro (id, empresa_id), no devuelve la auditoría ajena.
        db.query.return_value.filter.return_value.first.return_value = None
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="AUDITOR")

        with self.assertRaises(HTTPException) as ctx:
            exportar_pdf_auditoria_sst(auditoria_id=9, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 404)
        mock_generar.assert_not_called()
        # El filtro debe incluir id + empresa_id (2 condiciones de tenant).
        filtros = db.query.return_value.filter.call_args.args
        self.assertEqual(len(filtros), 2)


if __name__ == "__main__":
    import unittest
    unittest.main()

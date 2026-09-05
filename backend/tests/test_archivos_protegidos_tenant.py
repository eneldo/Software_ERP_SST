from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock

from fastapi import HTTPException

from app.routers.archivos_protegidos import servir_archivo_protegido


class ArchivosProtegidosTenantTest(TestCase):
    def test_servir_rechaza_archivo_ajeno(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(
            id=5, empresa_id=2, url="/uploads/evidencias/abc.pdf",
        )
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as ctx:
            servir_archivo_protegido(
                relative_path="evidencias/abc.pdf", usuario=usuario, db=db
            )

        self.assertEqual(ctx.exception.status_code, 403)


if __name__ == "__main__":
    import unittest
    unittest.main()

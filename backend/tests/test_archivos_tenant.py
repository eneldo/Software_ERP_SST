from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from app.routers.archivos_sst import (
    eliminar_archivo_sst,
    listar_archivos_sst,
    obtener_archivo_sst,
    subir_archivo_sst,
)


def _q(items):
    q = MagicMock()
    q.filter.return_value = q
    q.order_by.return_value = q
    q.all.return_value = items
    q.first.return_value = items[0] if items else None
    return q


def _archivo(empresa_id=2):
    return SimpleNamespace(
        id=5, empresa_id=empresa_id, usuario_id=10, tipo="EVIDENCIA",
        nombre_original="ev.pdf", nombre_archivo="abc.pdf", ruta="/tmp/abc.pdf",
        url="/uploads/evidencias/abc.pdf", extension=".pdf",
        mime_type="application/pdf", tamano_bytes=10, modulo="EPP",
        referencia_id=1, descripcion="x", activo=True,
    )


class ArchivosTenantTest(TestCase):
    @patch("app.routers.archivos_sst.validate_upload")
    def test_subir_rechaza_empresa_ajena(self, mock_validate):
        mock_validate.return_value = SimpleNamespace(
            extension=".pdf", content=b"%PDF", safe_filename="ev.pdf",
            mime_type="application/pdf",
        )
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(id=2)
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")
        archivo = MagicMock()
        archivo.filename = "ev.pdf"

        with self.assertRaises(HTTPException) as ctx:
            subir_archivo_sst(
                empresa_id=2, tipo="EVIDENCIA", modulo="EPP",
                referencia_id=1, descripcion="x", file=archivo,
                db=db, usuario=usuario,
            )

        self.assertEqual(ctx.exception.status_code, 403)
        db.add.assert_not_called()

    def test_listar_rechaza_empresa_ajena(self):
        db = MagicMock()
        db.query.return_value = _q([])
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as ctx:
            listar_archivos_sst(empresa_id=2, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 403)

    def test_obtener_rechaza_archivo_ajeno(self):
        db = MagicMock()
        # La BD, con filtro (id, empresa_id), no devuelve el archivo ajeno.
        db.query.return_value = _q([])
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as ctx:
            obtener_archivo_sst(archivo_id=5, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 404)
        filtros = db.query.return_value.filter.call_args.args
        self.assertEqual(len(filtros), 2)

    def test_eliminar_rechaza_archivo_ajeno(self):
        db = MagicMock()
        db.query.return_value = _q([])
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as ctx:
            eliminar_archivo_sst(archivo_id=5, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 404)
        filtros = db.query.return_value.filter.call_args.args
        self.assertEqual(len(filtros), 2)


if __name__ == "__main__":
    import unittest
    unittest.main()

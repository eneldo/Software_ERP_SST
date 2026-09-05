import csv
import io
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from app.routers.exportaciones_sst import exportar_objetivos_csv
from app.services.export_csv_service import generar_csv_corporativo


def _empresa():
    return SimpleNamespace(id=2, nombre="Empresa 2", nit="900123456")


class CsvMetadatosTest(TestCase):
    def test_servicio_incluye_metadatos(self):
        buf = generar_csv_corporativo(
            titulo="Objetivos SST",
            codigo="OBJ-001",
            empresa=_empresa(),
            columnas=["Objetivo"],
            filas=[["Reducir AT"]],
            metadatos={
                "usuario_generador": "Ana Pérez",
                "filtros": {"empresa_id": 2},
            },
        )
        contenido = buf.getvalue().decode("utf-8-sig")

        self.assertIn("Ana Pérez", contenido)
        self.assertIn("empresa_id", contenido)

    @patch("app.routers.exportaciones_sst.generar_csv_corporativo")
    def test_endpoint_pasa_metadatos(self, mock_csv):
        mock_csv.return_value = MagicMock()
        objetivo = SimpleNamespace(
            id=1, objetivo="Reducir AT", meta="0%", indicador="I",
            responsable="SST", estado="ACTIVO", cumplimiento=100,
            fecha_inicio=None, fecha_fin=None, observaciones=None,
        )
        q_items = MagicMock()
        q_items.filter.return_value.order_by.return_value.all.return_value = [objetivo]
        q_empresa = MagicMock()
        q_empresa.filter.return_value.first.return_value = _empresa()
        q_config = MagicMock()
        q_config.filter.return_value.first.return_value = None
        db = MagicMock()
        db.query.side_effect = [q_empresa, q_config, q_items]
        usuario = SimpleNamespace(
            id=10, empresa_id=2, rol="ADMIN_EMPRESA",
            nombres="Ana", apellidos="Pérez",
        )

        exportar_objetivos_csv(empresa_id=2, db=db, usuario=usuario)

        _, kwargs = mock_csv.call_args
        generador = kwargs["metadatos"]["usuario"]
        self.assertEqual(f"{generador.nombres} {generador.apellidos}", "Ana Pérez")
        self.assertEqual(kwargs["metadatos"]["filtros"], {"empresa_id": 2})


if __name__ == "__main__":
    import unittest
    unittest.main()

import csv
import io
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock

from fastapi import HTTPException

from app.routers.exportaciones_sst import exportar_objetivos_csv
from app.services.export_csv_service import generar_csv_corporativo


def _empresa():
    return SimpleNamespace(id=2, nombre="Empresa 2", nit="900123456")


class ExportCsvTest(TestCase):
    def test_servicio_genera_csv(self):
        buf = generar_csv_corporativo(
            titulo="Objetivos SST",
            codigo="OBJ-001",
            empresa=_empresa(),
            columnas=["Objetivo", "Meta"],
            filas=[["Reducir AT", "0%"]],
        )
        contenido = buf.getvalue().decode("utf-8-sig")
        filas = list(csv.reader(io.StringIO(contenido), delimiter=";"))

        self.assertIn("Empresa 2", filas[0][0])
        self.assertIn("Objetivo", filas[4])
        self.assertIn("Reducir AT", filas[5])

    def test_export_rechaza_empresa_ajena(self):
        db = MagicMock()
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="ADMIN_EMPRESA")

        with self.assertRaises(HTTPException) as ctx:
            exportar_objetivos_csv(empresa_id=2, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 403)

    def test_export_devuelve_csv(self):
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
        usuario = SimpleNamespace(id=10, empresa_id=2, rol="ADMIN_EMPRESA")

        resp = exportar_objetivos_csv(empresa_id=2, db=db, usuario=usuario)

        self.assertEqual(resp.media_type, "text/csv")


if __name__ == "__main__":
    import unittest
    unittest.main()

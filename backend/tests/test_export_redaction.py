from datetime import date
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from app.routers.examenes_medicos import (
    _crear_excel_examenes,
    exportar_examenes_medicos_excel,
)


def _examen():
    empleado = SimpleNamespace(
        nombres="Juan", apellidos="Perez", documento="123",
        empresa=SimpleNamespace(nombre="E1"), sede=SimpleNamespace(nombre="S1"),
        area=SimpleNamespace(nombre="A1"), cargo=SimpleNamespace(nombre="C1"),
    )
    return SimpleNamespace(
        id=1, empleado=empleado, tipo_examen="INGRESO", concepto="APTO",
        medico_ocupacional="Dr. X", entidad_salud="IPS",
        fecha_examen=date(2026, 1, 1), fecha_vencimiento=date(2027, 1, 1),
        restricciones="Restricción real", observaciones="Observación real",
    )


class ExportRedactionTest(TestCase):
    def test_excel_redacta_concepto_sin_permiso(self):
        wb = _crear_excel_examenes([_examen()], mostrar_concepto=False)
        ws = wb.active
        concepto = ws.cell(row=5, column=9).value

        self.assertNotIn("Apto", str(concepto))
        # Los campos administrativos siguen visibles.
        self.assertEqual(ws.cell(row=5, column=3).value, "Juan Perez")

    def test_excel_redacta_historia_sin_permiso(self):
        wb = _crear_excel_examenes([_examen()], mostrar_historia=False)
        ws = wb.active

        self.assertEqual(ws.cell(row=5, column=16).value, "")
        self.assertEqual(ws.cell(row=5, column=17).value, "")

    @patch("app.routers.examenes_medicos.user_has_permission", return_value=False)
    @patch("app.routers.examenes_medicos._stream_excel", return_value="XLSX")
    @patch("app.routers.examenes_medicos._examenes_exportables", return_value=[])
    @patch("app.routers.examenes_medicos._crear_excel_examenes")
    def test_endpoint_pasa_flags(self, mock_crear, mock_exp, mock_stream, mock_perm):
        db = MagicMock()
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        exportar_examenes_medicos_excel(db=db, usuario=usuario)

        _, kwargs = mock_crear.call_args
        self.assertFalse(kwargs["mostrar_concepto"])
        self.assertFalse(kwargs["mostrar_historia"])


if __name__ == "__main__":
    import unittest
    unittest.main()

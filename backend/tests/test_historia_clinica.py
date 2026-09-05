from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from app.routers.examenes_medicos import (
    eliminar_evidencia_examen_medico,
    exportar_ficha_examen_medico_pdf,
    exportar_reporte_restricciones_pdf,
    listar_evidencias_examen_medico,
)


def _usuario_sin_historia():
    return SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")


def _examen_completo():
    empleado = SimpleNamespace(
        id=5, empresa_id=1, nombres="Juan", apellidos="Perez",
        documento="123", correo="j@p.com", empresa_id_=1,
        empresa=SimpleNamespace(nombre="E1"), sede=SimpleNamespace(nombre="S1"),
        area=SimpleNamespace(nombre="A1"), cargo=SimpleNamespace(nombre="C1"),
        sede_id=1, area_id=1, cargo_id=1,
    )
    return SimpleNamespace(
        id=7, empleado_id=5, empleado=empleado, tipo_examen="INGRESO",
        fecha_examen="2026-01-01", fecha_vencimiento="2027-01-01",
        concepto="APTO", medico_ocupacional="Dr. X", entidad_salud="IPS",
        restricciones="R", observaciones="O", examenes_aplicados=None,
    )


class HistoriaClinicaTest(TestCase):
    @patch("app.routers.examenes_medicos.user_has_permission", return_value=False)
    @patch("app.routers.examenes_medicos._examenes_exportables", return_value=[])
    def test_restricciones_exige_historia_clinica(self, mock_exp, mock_perm):
        db = MagicMock()
        usuario = _usuario_sin_historia()

        with self.assertRaises(HTTPException) as ctx:
            exportar_reporte_restricciones_pdf(db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 403)

    @patch("app.routers.examenes_medicos.user_has_permission", return_value=False)
    @patch("app.routers.examenes_medicos._stream_pdf", return_value="PDF")
    def test_ficha_exige_historia_clinica(self, mock_stream, mock_perm):
        db = MagicMock()
        q = MagicMock()
        q.options.return_value.filter.return_value.first.return_value = _examen_completo()
        db.query.return_value = q
        usuario = _usuario_sin_historia()

        with self.assertRaises(HTTPException) as ctx:
            exportar_ficha_examen_medico_pdf(examen_id=7, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 403)
        mock_stream.assert_not_called()

    @patch("app.routers.examenes_medicos.user_has_permission", return_value=False)
    @patch("app.routers.examenes_medicos._obtener_examen_base")
    def test_evidencias_exigen_historia_clinica(self, mock_base, mock_perm):
        mock_base.return_value = _examen_completo()
        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        usuario = _usuario_sin_historia()

        with self.assertRaises(HTTPException) as ctx:
            listar_evidencias_examen_medico(examen_id=7, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 403)

    @patch("app.routers.examenes_medicos.user_has_permission", return_value=False)
    @patch("app.routers.examenes_medicos._obtener_examen_base")
    def test_eliminar_evidencia_exige_historia_clinica(self, mock_base, mock_perm):
        mock_base.return_value = _examen_completo()
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="ADMIN_EMPRESA")

        with self.assertRaises(HTTPException) as ctx:
            eliminar_evidencia_examen_medico(
                examen_id=7, archivo_id=3, db=db, usuario=usuario
            )

        self.assertEqual(ctx.exception.status_code, 403)


if __name__ == "__main__":
    import unittest
    unittest.main()

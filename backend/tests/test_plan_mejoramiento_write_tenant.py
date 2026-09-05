from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from app.routers import plan_mejoramiento as router
from app.schemas.plan_mejoramiento_schema import (
    PlanMejoramientoCreate,
    PlanMejoramientoUpdate,
)


def _usuario():
    return SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")


class PlanMejoramientoWriteTenantTest(TestCase):
    @patch.object(router, "serializar_plan", return_value="OK")
    @patch.object(router, "crear_plan_manual", return_value="OK")
    def test_crear_rechaza_empresa_ajena(self, mock_crear, mock_serializar):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(
            id=2, estado=True
        )
        data = PlanMejoramientoCreate(
            empresa_id=2, titulo="Plan", accion_correctiva="Acción",
        )

        with self.assertRaises(HTTPException) as ctx:
            router.crear_accion_mejoramiento(data=data, db=db, usuario=_usuario())

        self.assertEqual(ctx.exception.status_code, 403)
        mock_crear.assert_not_called()

    @patch.object(router, "serializar_plan", return_value="OK")
    @patch.object(router, "actualizar_plan", return_value="OK")
    def test_actualizar_rechaza_plan_ajeno(self, mock_actualizar, mock_serializar):
        db = MagicMock()
        # La BD, con filtro (id, empresa_id), no devuelve el plan ajeno.
        db.query.return_value.filter.return_value.first.return_value = None
        data = PlanMejoramientoUpdate(titulo="Nuevo título")

        with self.assertRaises(HTTPException) as ctx:
            router.actualizar_accion_mejoramiento(
                plan_id=3, data=data, db=db, usuario=_usuario()
            )

        self.assertEqual(ctx.exception.status_code, 404)
        mock_actualizar.assert_not_called()
        filtros = db.query.return_value.filter.call_args.args
        self.assertEqual(len(filtros), 2)


if __name__ == "__main__":
    import unittest
    unittest.main()

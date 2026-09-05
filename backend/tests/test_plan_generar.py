from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from app.models.evaluacion_inicial import EvaluacionInicialSST
from app.models.plan_mejoramiento import PlanMejoramientoSST
from app.routers import plan_mejoramiento as router
from app.services.plan_mejoramiento_service import generar_desde_evaluacion


def _item():
    return SimpleNamespace(
        id=11, activo=True, respuesta="NO_CUMPLE", criterio="Criterio X",
        observaciones=None, responsable="SST", evidencia=None,
        numeral="1.1.1", estandar="Recursos",
    )


def _evaluacion():
    return SimpleNamespace(
        id=5, empresa_id=1, responsable="Jefe SST", items=[_item()],
    )


def _q_plan(first_value):
    q = MagicMock()
    q.filter.return_value = q
    q.order_by.return_value = q
    q.first.return_value = first_value
    return q


class PlanGenerarTest(TestCase):
    @patch.object(router, "generar_desde_evaluacion", return_value={"ok": True})
    def test_generar_rechaza_evaluacion_ajena(self, mock_generar):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as ctx:
            router.generar_plan_automatico_desde_evaluacion(
                data=SimpleNamespace(evaluacion_id=5), db=db, usuario=usuario
            )

        self.assertEqual(ctx.exception.status_code, 404)
        mock_generar.assert_not_called()

    def test_generar_registra_origen_estandar(self):
        q_eval = MagicMock()
        q_eval.options.return_value.filter.return_value.first.return_value = _evaluacion()
        q_plan = _q_plan(None)
        db = MagicMock()

        def _query(modelo, *a, **k):
            if modelo is EvaluacionInicialSST:
                return q_eval
            if modelo is PlanMejoramientoSST:
                return q_plan
            return MagicMock()

        db.query.side_effect = _query

        resp = generar_desde_evaluacion(db=db, evaluacion_id=5, usuario_id=10)

        self.assertEqual(resp["creados"], 1)
        plan = db.add.call_args.args[0]
        self.assertEqual(plan.origen_hallazgo, "ESTANDAR_MINIMO")
        self.assertEqual(plan.origen_id, 11)
        self.assertEqual(plan.empresa_id, 1)


if __name__ == "__main__":
    import unittest
    unittest.main()

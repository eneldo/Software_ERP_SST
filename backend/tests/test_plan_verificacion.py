from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock

from fastapi import HTTPException
from pydantic import ValidationError

from app.models.plan_mejoramiento import PlanMejoramientoSST
from app.models.plan_mejoramiento_evidencia import PlanMejoramientoEvidenciaSST
from app.schemas.plan_mejoramiento_schema import VerificarPlanRequest
from app.services.plan_mejoramiento_service import verificar_plan


def _db_con_plan_y_evidencias(plan, total_evidencias: int) -> MagicMock:
    q_plan = MagicMock()
    q_plan.filter.return_value.first.return_value = plan
    q_ev = MagicMock()
    q_ev.filter.return_value.count.return_value = total_evidencias
    db = MagicMock()

    def _query(modelo, *a, **k):
        if modelo is PlanMejoramientoSST:
            return q_plan
        if modelo is PlanMejoramientoEvidenciaSST:
            return q_ev
        return MagicMock()

    db.query.side_effect = _query
    return db


def _plan(**extras):
    base = dict(
        id=3, empresa_id=1, estado="EN_PROCESO", porcentaje_avance=100,
        fecha_cierre=None, observaciones=None, verificado_por=None,
        fecha_verificacion=None, resultado_verificacion=None,
    )
    base.update(extras)
    return SimpleNamespace(**base)


class PlanVerificacionTest(TestCase):
    def test_verificar_sin_evidencia_rechaza_400(self):
        db = _db_con_plan_y_evidencias(_plan(), 0)
        data = VerificarPlanRequest(resultado="APROBADO")

        with self.assertRaises(HTTPException) as ctx:
            verificar_plan(db=db, plan_id=3, data=data, usuario_id=10)

        self.assertEqual(ctx.exception.status_code, 400)

    def test_verificar_resultado_invalido_rechaza(self):
        with self.assertRaises(ValidationError):
            VerificarPlanRequest(resultado="TAL_VEZ")

    def test_verificar_ok_registra_verificacion(self):
        db = _db_con_plan_y_evidencias(_plan(), 2)
        data = VerificarPlanRequest(resultado="APROBADO")

        plan = verificar_plan(db=db, plan_id=3, data=data, usuario_id=10)

        self.assertEqual(plan.resultado_verificacion, "APROBADO")
        self.assertEqual(plan.verificado_por, 10)
        self.assertIsNotNone(plan.fecha_verificacion)


if __name__ == "__main__":
    import unittest
    unittest.main()

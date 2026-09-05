from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock

from fastapi import HTTPException

from app.models.plan_mejoramiento import PlanMejoramientoSST
from app.models.plan_mejoramiento_evidencia import PlanMejoramientoEvidenciaSST
from app.services.plan_mejoramiento_service import cerrar_plan


def _db_con_plan_y_evidencias(total_evidencias: int, verificado: bool = False) -> MagicMock:
    plan = SimpleNamespace(
        id=3, empresa_id=1, estado="EN_PROCESO", porcentaje_avance=80,
        fecha_cierre=None, observaciones=None,
        verificado_por=10 if verificado else None,
        fecha_verificacion=None,
        resultado_verificacion="APROBADO" if verificado else None,
    )
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


class PlanCierreTest(TestCase):
    def test_cerrar_sin_evidencia_rechaza_400(self):
        db = _db_con_plan_y_evidencias(0)

        with self.assertRaises(HTTPException) as ctx:
            cerrar_plan(db=db, plan_id=3)

        self.assertEqual(ctx.exception.status_code, 400)

    def test_cerrar_sin_verificacion_rechaza_400(self):
        db = _db_con_plan_y_evidencias(2, verificado=False)

        with self.assertRaises(HTTPException) as ctx:
            cerrar_plan(db=db, plan_id=3)

        self.assertEqual(ctx.exception.status_code, 400)

    def test_cerrar_con_evidencia_ok(self):
        db = _db_con_plan_y_evidencias(2, verificado=True)

        plan = cerrar_plan(db=db, plan_id=3, observaciones="Cierre verificado")

        self.assertEqual(plan.estado, "FINALIZADO")
        self.assertEqual(plan.porcentaje_avance, 100)
        self.assertIsNotNone(plan.fecha_cierre)


if __name__ == "__main__":
    import unittest
    unittest.main()

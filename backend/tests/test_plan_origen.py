from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock

from pydantic import ValidationError

from app.models.plan_mejoramiento import PlanMejoramientoSST
from app.schemas.plan_mejoramiento_schema import PlanMejoramientoCreate
from app.services.plan_mejoramiento_service import crear_plan_manual


def _data(origen="AUDITORIA", origen_id=9):
    return SimpleNamespace(
        empresa_id=1, evaluacion_id=None, item_evaluacion_id=None,
        titulo="Cerrar hallazgo", descripcion=None, causa="Causa raíz",
        accion_correctiva="Acción", responsable="SST", prioridad="ALTA",
        estado="PENDIENTE", fecha_apertura=None, fecha_compromiso=None,
        fecha_cierre=None, porcentaje_avance=0, evidencia=None,
        observaciones=None, origen_hallazgo=origen, origen_id=origen_id,
    )


class PlanOrigenTest(TestCase):
    def test_modelo_acepta_origen(self):
        plan = PlanMejoramientoSST(
            empresa_id=1, codigo="PM-SST-0001", titulo="T",
            accion_correctiva="A", origen_hallazgo="AUDITORIA", origen_id=9,
        )

        self.assertEqual(plan.origen_hallazgo, "AUDITORIA")
        self.assertEqual(plan.origen_id, 9)

    def test_schema_rechaza_origen_invalido(self):
        with self.assertRaises(ValidationError):
            PlanMejoramientoCreate(
                empresa_id=1, titulo="T", accion_correctiva="A",
                origen_hallazgo="INVENTADO",
            )

    def test_crear_persiste_origen(self):
        db = MagicMock()
        db.refresh.side_effect = lambda plan: setattr(plan, "id", 1)

        plan = crear_plan_manual(db=db, data=_data(), usuario_id=10)

        self.assertEqual(plan.origen_hallazgo, "AUDITORIA")
        self.assertEqual(plan.origen_id, 9)


if __name__ == "__main__":
    import unittest
    unittest.main()

from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock

from fastapi import HTTPException

from app.routers.plan_anual import (
    crear_actividad,
    listar_plan_anual,
    obtener_actividad,
    resumen_plan_anual,
)
from app.schemas.plan_anual import PlanAnualCreate


def _q_all(items):
    q = MagicMock()
    q.options.return_value = q
    q.filter.return_value = q
    q.order_by.return_value = q
    q.all.return_value = items
    q.first.return_value = items[0] if items else None
    return q


def _item_plan_anual(empresa_id=2):
    return SimpleNamespace(
        id=7, empresa_id=empresa_id, usuario_id=10, archivo_id=None,
        codigo="PA-SST-001", actividad="Capacitación", objetivo=None,
        responsable="SST", recurso_humano=None, recurso_fisico=None,
        recurso_financiero=None, presupuesto=0, indicador=None, meta=None,
        fecha_inicio=None, fecha_fin=None, estado="PLANIFICADO",
        porcentaje_avance=0, evidencia=None, observaciones=None, archivo=None,
        alcance=None, objetivo_general=None, vigencia=None,
        representante_legal_nombre=None, representante_legal_cargo=None,
        responsable_sst_nombre=None, responsable_sst_cargo=None,
        activo=True, fecha_creacion=None, fecha_actualizacion=None,
    )


class PlanAnualTenantTest(TestCase):
    def test_listar_rechaza_empresa_ajena(self):
        db = MagicMock()
        db.query.return_value = _q_all([])
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as ctx:
            listar_plan_anual(empresa_id=2, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 403)

    def test_resumen_rechaza_empresa_ajena(self):
        db = MagicMock()
        db.query.return_value = _q_all([])
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as ctx:
            resumen_plan_anual(empresa_id=2, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 403)

    def test_obtener_rechaza_actividad_ajena(self):
        db = MagicMock()
        # La BD, con filtro (id, empresa_id) aplicado, no devuelve la actividad ajena.
        db.query.return_value = _q_all([])
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as ctx:
            obtener_actividad(item_id=7, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 404)
        # El filtro debe incluir id + empresa_id (2 condiciones de tenant).
        q = db.query.return_value
        filtros = q.options.return_value.filter.call_args.args
        self.assertEqual(len(filtros), 2)

    def test_crear_rechaza_empresa_ajena(self):
        q_empresa = MagicMock()
        q_empresa.filter.return_value.first.return_value = SimpleNamespace(id=2)
        q_item = MagicMock()
        q_item.options.return_value.filter.return_value.first.return_value = _item_plan_anual(empresa_id=2)
        db = MagicMock()
        db.query.side_effect = [q_empresa, q_item]
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")
        data = PlanAnualCreate(empresa_id=2, actividad="Capacitación anual")

        with self.assertRaises(HTTPException) as ctx:
            crear_actividad(data=data, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 403)
        db.add.assert_not_called()


if __name__ == "__main__":
    import unittest
    unittest.main()

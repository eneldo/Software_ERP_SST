from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from app.routers.plan_anual import (
    crear_actividad,
    dashboard_plan_anual,
    listar_actividades,
    listar_plan_anual,
    obtener_actividad,
    resumen_plan_anual,
    serializar_cabecera,
    subir_evidencia_plan_anual,
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
        plan_anual_cabecera_id=1,
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
        q_empresa.filter.return_value.first.return_value = SimpleNamespace(id=2, empresa_id=2)
        q_item = MagicMock()
        q_item.options.return_value.filter.return_value.first.return_value = _item_plan_anual(empresa_id=2)
        db = MagicMock()
        db.query.side_effect = [q_empresa, q_item]
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")
        data = PlanAnualCreate(actividad="Capacitación anual")

        with self.assertRaises(HTTPException) as ctx:
            crear_actividad(cabecera_id=2, data=data, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 403)
        db.add.assert_not_called()

    def test_cabecera_cuenta_solo_actividades_activas(self):
        cabecera = SimpleNamespace(
            id=1, empresa_id=1, usuario_id=10, vigencia="2026", alcance=None,
            objetivo_general=None, meta_general=None, representante_legal_nombre=None,
            representante_legal_cargo=None, responsable_sst_nombre=None,
            responsable_sst_cargo=None, activo=True, fecha_creacion=None,
            fecha_actualizacion=None,
            actividades=[SimpleNamespace(activo=True), SimpleNamespace(activo=False)],
        )

        self.assertEqual(serializar_cabecera(cabecera)["actividades_count"], 1)

    def test_listado_get_no_hace_commit(self):
        db = MagicMock()
        db.query.return_value = _q_all([_item_plan_anual(empresa_id=1)])
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        listar_plan_anual(empresa_id=1, db=db, usuario=usuario)

        db.commit.assert_not_called()

    def test_resumen_excluye_huerfanas_y_filtra_por_vigencia(self):
        db = MagicMock()
        db.query.return_value = _q_all([])
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        resumen_plan_anual(empresa_id=1, vigencia="2026", db=db, usuario=usuario)

        filtros = db.query.return_value.filter.call_args.args
        self.assertEqual(len(filtros), 4)
        db.commit.assert_not_called()

    def test_dashboard_excluye_huerfanas_y_filtra_por_cabecera(self):
        db = MagicMock()
        db.query.return_value = _q_all([])
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        resultado = dashboard_plan_anual(
            empresa_id=1, cabecera_id=8, db=db, usuario=usuario
        )

        filtros = db.query.return_value.filter.call_args.args
        self.assertEqual(len(filtros), 4)
        self.assertEqual(resultado["total_actividades"], 0)
        db.commit.assert_not_called()

    @patch("app.routers.plan_anual.guardar_evidencia_sst")
    def test_upload_revierte_y_elimina_archivo_si_falla_flush(self, guardar):
        item = _item_plan_anual(empresa_id=1)
        db = MagicMock()
        db.query.return_value = _q_all([item])
        db.flush.side_effect = RuntimeError("fallo db")
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")
        ruta = MagicMock()
        ruta.exists.return_value = True
        guardar.return_value = {
            "nombre_archivo": "evidencia.pdf", "ruta_fisica": str(ruta),
            "url": "/uploads/plan-anual/evidencia.pdf", "extension": ".pdf",
            "mime_type": "application/pdf", "tamano_bytes": 10,
        }
        archivo_fisico = MagicMock()

        with patch("app.routers.plan_anual.Path", return_value=archivo_fisico):
            with self.assertRaises(RuntimeError):
                subir_evidencia_plan_anual(
                    item_id=7, descripcion=None,
                    file=SimpleNamespace(filename="evidencia.pdf"), db=db,
                    usuario=usuario,
                )

        db.rollback.assert_called_once()
        archivo_fisico.unlink.assert_called_once_with(missing_ok=True)
        db.commit.assert_not_called()

    def test_migracion_reparadora_es_forward_y_downgrade_irreversible(self):
        ruta = (
            Path(__file__).parents[1]
            / "alembic" / "versions"
            / "20261004_0001_repair_plan_anual_legacy.py"
        )
        spec = spec_from_file_location("repair_plan_anual_legacy", ruta)
        modulo = module_from_spec(spec)
        spec.loader.exec_module(modulo)

        self.assertEqual(modulo.down_revision, "l4m5n6o7p8q9")
        with self.assertRaises(RuntimeError, msg="irreversible"):
            modulo.downgrade()


if __name__ == "__main__":
    import unittest
    unittest.main()

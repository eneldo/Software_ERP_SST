from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock

from fastapi import HTTPException

from app.routers.auditoria_hallazgo_evidencias import (
    eliminar_evidencia_hallazgo,
    listar_evidencias_auditoria,
    obtener_hallazgo_o_404,
)
from app.routers.permisos import (
    actualizar_permiso,
    asignar_permisos_usuario,
    crear_permiso,
    permisos_por_usuario,
)
from app.routers.profesiograma import (
    crear_o_actualizar_profesiograma,
    crear_tipo_evaluacion,
    listar_profesiogramas,
)
from app.schemas.permiso_schema import (
    AsignarPermisosUsuario,
    PermisoCreate,
    PermisoUpdate,
)
from app.schemas.profesiograma_schema import (
    ProfesiogramaCreate,
    TipoEvaluacionMedicaCreate,
)


class ProfesiogramaTenantTest(TestCase):
    def test_listado_no_superadmin_fuerza_su_empresa(self):
        db = MagicMock()
        query = MagicMock()
        db.query.return_value.options.return_value.filter.return_value = query
        query.filter.return_value = query
        query.order_by.return_value.all.return_value = []
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="ADMIN_EMPRESA")

        listar_profesiogramas(empresa_id=None, db=db, usuario=usuario)

        self.assertEqual(query.filter.call_count, 1)
        self.assertIn("empresa_id", str(query.filter.call_args.args[0]))

    def test_creacion_rechaza_empresa_distinta_al_cargo(self):
        db = MagicMock()
        cargo = SimpleNamespace(id=7, empresa_id=1)
        db.query.return_value.filter.return_value.first.return_value = cargo
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="ADMIN_EMPRESA")
        data = ProfesiogramaCreate(cargo_id=7, empresa_id=2, evaluaciones=[])

        with self.assertRaises(HTTPException) as contexto:
            crear_o_actualizar_profesiograma(7, data, db, usuario)

        self.assertEqual(contexto.exception.status_code, 403)
        db.add.assert_not_called()

    def test_catalogo_global_solo_lo_muta_superadmin(self):
        db = MagicMock()
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="ADMIN_EMPRESA")
        data = TipoEvaluacionMedicaCreate(codigo="NUEVO", nombre="Nuevo")

        with self.assertRaises(HTTPException) as contexto:
            crear_tipo_evaluacion(data, db, usuario)

        self.assertEqual(contexto.exception.status_code, 403)
        db.add.assert_not_called()


class AuditoriaEvidenciasTenantTest(TestCase):
    def test_hallazgo_ajeno_no_es_visible(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="AUDITOR")

        with self.assertRaises(HTTPException) as contexto:
            obtener_hallazgo_o_404(db, 9, usuario)

        self.assertEqual(contexto.exception.status_code, 404)
        filtros = db.query.return_value.filter.call_args.args
        self.assertEqual(len(filtros), 3)
        self.assertIn("empresa_id", str(filtros[2]))

    def test_listado_por_auditoria_valida_recurso_padre_del_tenant(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="AUDITOR")

        with self.assertRaises(HTTPException) as contexto:
            listar_evidencias_auditoria(8, db, usuario)

        self.assertEqual(contexto.exception.status_code, 404)

    def test_eliminacion_no_encuentra_evidencia_ajena(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="AUDITOR")

        with self.assertRaises(HTTPException) as contexto:
            eliminar_evidencia_hallazgo(11, db, usuario)

        self.assertEqual(contexto.exception.status_code, 404)
        filtros = db.query.return_value.filter.call_args.args
        self.assertEqual(len(filtros), 3)
        self.assertIn("empresa_id", str(filtros[2]))


class PermisosTenantTest(TestCase):
    def test_crud_global_rechaza_admin_empresa_aunque_tenga_permiso(self):
        db = MagicMock()
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="ADMIN_EMPRESA")
        data = PermisoCreate(codigo="PRUEBA", nombre="Prueba", modulo="SST")

        with self.assertRaises(HTTPException) as contexto:
            crear_permiso(data, db, usuario)

        self.assertEqual(contexto.exception.status_code, 403)
        db.add.assert_not_called()

    def test_actualizacion_global_rechaza_admin_empresa(self):
        db = MagicMock()
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="ADMIN_EMPRESA")

        with self.assertRaises(HTTPException) as contexto:
            actualizar_permiso(1, PermisoUpdate(nombre="Cambio"), db, usuario)

        self.assertEqual(contexto.exception.status_code, 403)
        db.commit.assert_not_called()

    def test_asignacion_rechaza_usuario_de_otro_tenant(self):
        db = MagicMock()
        objetivo = SimpleNamespace(id=20, empresa_id=2)
        db.query.return_value.filter.return_value.first.return_value = objetivo
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="ADMIN_EMPRESA")
        data = AsignarPermisosUsuario(usuario_id=20, permisos_ids=[])

        with self.assertRaises(HTTPException) as contexto:
            asignar_permisos_usuario(data, db, usuario)

        self.assertEqual(contexto.exception.status_code, 404)
        db.commit.assert_not_called()

    def test_consulta_rechaza_usuario_de_otro_tenant(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="ADMIN_EMPRESA")

        with self.assertRaises(HTTPException) as contexto:
            permisos_por_usuario(20, db, usuario)

        self.assertEqual(contexto.exception.status_code, 404)
        filtros = db.query.return_value.filter.call_args.args
        self.assertEqual(len(filtros), 2)
        self.assertIn("empresa_id", str(filtros[1]))


if __name__ == "__main__":
    import unittest

    unittest.main()

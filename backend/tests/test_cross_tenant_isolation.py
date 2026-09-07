from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch
from datetime import datetime

from fastapi import HTTPException

from app.routers.exportaciones_sst import (
    exportar_politica_pdf,
    _empresa_id_autorizada,
)
from app.routers.reporte_evidencias import (
    _obtener_reporte,
    eliminar_evidencia_reporte,
    dashboard_evidencias_reportes,
    timeline_reporte,
)
from app.routers.notificaciones_sst import (
    obtener_notificacion,
    actualizar_notificacion,
    marcar_leida,
    archivar_notificacion,
    eliminar_notificacion,
    obtener_configuracion,
    actualizar_configuracion,
)
from app.routers.kirkpatrick import (
    listar_evaluaciones,
    obtener_evaluacion,
    actualizar_evaluacion,
    eliminar_evaluacion,
    resumen_kirkpatrick,
)


def _q(items=None):
    q = MagicMock()
    q.filter.return_value = q
    q.filter_by.return_value = q
    q.join.return_value = q
    q.options.return_value = q
    q.order_by.return_value = q
    q.offset.return_value = q
    q.limit.return_value = q
    q.all.return_value = items or []
    q.first.return_value = items[0] if items else None
    q.count.return_value = len(items) if items else 0
    return q


def _usuario(empresa_id=1, rol="ADMIN_EMPRESA"):
    return SimpleNamespace(id=10, empresa_id=empresa_id, rol=rol)


class EmpresaAutorizadaTest(TestCase):
    def test_superadmin_accede_cualquier_empresa(self):
        usuario = _usuario(empresa_id=None, rol="SUPER_ADMIN")
        result = _empresa_id_autorizada(usuario, empresa_id=99)
        self.assertEqual(result, 99)

    def test_usuario_misma_empresa(self):
        usuario = _usuario(empresa_id=5, rol="ADMIN_EMPRESA")
        result = _empresa_id_autorizada(usuario, empresa_id=5)
        self.assertEqual(result, 5)

    def test_usuario_otra_empresa_rechaza_403(self):
        usuario = _usuario(empresa_id=1, rol="ADMIN_EMPRESA")
        with self.assertRaises(HTTPException) as ctx:
            _empresa_id_autorizada(usuario, empresa_id=2)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_usuario_sin_empresa_rechaza_403(self):
        usuario = _usuario(empresa_id=None, rol="ADMIN_EMPRESA")
        with self.assertRaises(HTTPException) as ctx:
            _empresa_id_autorizada(usuario, empresa_id=1)
        self.assertEqual(ctx.exception.status_code, 403)


class ExportacionesTenantTest(TestCase):
    def test_politica_pdf_rechaza_empresa_ajena(self):
        db = MagicMock()
        db.query.return_value = _q([SimpleNamespace(id=1, empresa_id=2)])
        usuario = _usuario(empresa_id=1)

        with self.assertRaises(HTTPException) as ctx:
            exportar_politica_pdf(politica_id=1, db=db, usuario=usuario)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_politica_pdf_no_encontrada_404(self):
        db = MagicMock()
        db.query.return_value = _q([])
        usuario = _usuario(empresa_id=1)

        with self.assertRaises(HTTPException) as ctx:
            exportar_politica_pdf(politica_id=999, db=db, usuario=usuario)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_politica_pdf_genera_response(self):
        db = MagicMock()
        politica = SimpleNamespace(
            id=1, empresa_id=1, titulo="P", codigo="POL-001",
            version="1.0", estado="VIGENTE", fecha_aprobacion=None,
            fecha_vigencia=None, responsable_sst=None, representante_legal=None,
            contenido="Contenido", observaciones=None,
        )
        db.query.return_value = _q([politica])
        usuario = _usuario(empresa_id=1)

        with patch("app.routers.exportaciones_sst.generar_pdf_corporativo", return_value=iter([b"%PDF"])):
            with patch("app.routers.exportaciones_sst.obtener_empresa_y_configuracion", return_value=(MagicMock(), MagicMock())):
                resp = exportar_politica_pdf(politica_id=1, db=db, usuario=usuario)
                self.assertIsNotNone(resp)


class ReporteEvidenciaTenantTest(TestCase):
    def _mock_reporte(self, reporte_id=1, empresa_id=1):
        return SimpleNamespace(
            id=reporte_id, empresa_id=empresa_id, titulo="Reporte Test",
            fecha_creacion=datetime.now(), activo=True,
            codigo="REP-001", descripcion="Desc", ubicacion="Bogota",
            fecha_reporte=datetime.now(), responsable_asignado=None,
            inspeccion_id=None, capa_id=None, estado="ABIERTO",
            trazabilidad=None, archivo_url=None,
        )

    def test_obtener_reporte_rechaza_empresa_ajena(self):
        db = MagicMock()
        db.query.return_value = _q([self._mock_reporte(empresa_id=2)])
        usuario = _usuario(empresa_id=1)

        with self.assertRaises(HTTPException) as ctx:
            _obtener_reporte(db, reporte_id=1, usuario=usuario)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_obtener_reporte_no_encontrado_404(self):
        db = MagicMock()
        db.query.return_value = _q([])
        usuario = _usuario(empresa_id=1)

        with self.assertRaises(HTTPException) as ctx:
            _obtener_reporte(db, reporte_id=999, usuario=usuario)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_eliminar_rechaza_empresa_ajena(self):
        ev_mock = SimpleNamespace(id=1, reporte_id=1, activo=True)
        reporte_mock = SimpleNamespace(id=1, empresa_id=2, trazabilidad=None)
        db = MagicMock()
        query_results = [ev_mock, reporte_mock]
        call_count = [0]

        def side_effect(*args, **kwargs):
            idx = min(call_count[0], len(query_results) - 1)
            call_count[0] += 1
            return _q([query_results[idx]])

        db.query.side_effect = side_effect
        usuario = _usuario(empresa_id=1)

        with self.assertRaises(HTTPException) as ctx:
            eliminar_evidencia_reporte(evidencia_id=1, db=db, usuario=usuario)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_dashboard_sin_empresa_param(self):
        db = MagicMock()
        db.query.return_value = _q([])
        usuario = _usuario(empresa_id=1, rol="SUPER_ADMIN")

        with patch("app.routers.reporte_evidencias._empresa_id_autorizada", return_value=1):
            resp = dashboard_evidencias_reportes(db=db, usuario=usuario)
        self.assertEqual(resp.total, 0)

    def test_timeline_rechaza_empresa_ajena(self):
        db = MagicMock()
        db.query.return_value = _q([self._mock_reporte(empresa_id=2)])
        usuario = _usuario(empresa_id=1)

        with self.assertRaises(HTTPException) as ctx:
            timeline_reporte(reporte_id=1, db=db, usuario=usuario)
        self.assertEqual(ctx.exception.status_code, 403)


class NotificacionesTenantTest(TestCase):
    def _mock_notif(self, notif_id=1, empresa_id=1):
        m = SimpleNamespace()
        m.id = notif_id
        m.empresa_id = empresa_id
        m.titulo = "Notif"
        m.mensaje = "msg"
        m.leida = False
        m.archivada = False
        m.activa = True
        m.modulo = "TEST"
        m.clave_unica = "key"
        m.tipo = "INFO"
        m.prioridad = "MEDIA"
        m.estado = "PENDIENTE"
        m.descripcion = "desc"
        m.accion_recomendada = None
        m.url_destino = None
        m.fecha_evento = datetime.now()
        m.fecha_vencimiento = None
        m.origen_generacion = "SISTEMA"
        m.metadata_json = "{}"
        m.fecha_creacion = datetime.now()
        m.fecha_actualizacion = datetime.now()
        m.fecha_lectura = None
        m.fecha_archivo = None
        m.empleado_id = None
        return m

    def test_obtener_rechaza_empresa_ajena(self):
        item = self._mock_notif(empresa_id=2)
        db = MagicMock()
        db.query.return_value = _q([item])
        usuario = _usuario(empresa_id=1)

        with self.assertRaises(HTTPException) as ctx:
            obtener_notificacion(notificacion_id=1, db=db, usuario=usuario)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_actualizar_rechaza_empresa_ajena(self):
        item = self._mock_notif(empresa_id=2)
        db = MagicMock()
        db.query.return_value = _q([item])
        usuario = _usuario(empresa_id=1)

        data_mock = MagicMock()
        data_mock.model_dump.return_value = {}

        with self.assertRaises(HTTPException) as ctx:
            actualizar_notificacion(notificacion_id=1, data=data_mock, db=db, usuario=usuario)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_marcar_leida_rechaza_empresa_ajena(self):
        item = self._mock_notif(empresa_id=2)
        db = MagicMock()
        db.query.return_value = _q([item])
        usuario = _usuario(empresa_id=1)

        with self.assertRaises(HTTPException) as ctx:
            marcar_leida(notificacion_id=1, db=db, usuario=usuario)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_archivar_rechaza_empresa_ajena(self):
        item = self._mock_notif(empresa_id=2)
        db = MagicMock()
        db.query.return_value = _q([item])
        usuario = _usuario(empresa_id=1)

        with self.assertRaises(HTTPException) as ctx:
            archivar_notificacion(notificacion_id=1, db=db, usuario=usuario)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_eliminar_rechaza_empresa_ajena(self):
        item = self._mock_notif(empresa_id=2)
        db = MagicMock()
        db.query.return_value = _q([item])
        usuario = _usuario(empresa_id=1)

        with self.assertRaises(HTTPException) as ctx:
            eliminar_notificacion(notificacion_id=1, db=db, usuario=usuario)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_config_obtener_rechaza_empresa_ajena(self):
        cfg = SimpleNamespace(id=1, empresa_id=2)
        db = MagicMock()
        db.query.return_value = _q([cfg])
        usuario = _usuario(empresa_id=1)

        with self.assertRaises(HTTPException) as ctx:
            obtener_configuracion(empresa_id=2, db=db, usuario=usuario)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_config_actualizar_rechaza_empresa_ajena(self):
        cfg = SimpleNamespace(id=1, empresa_id=2)
        db = MagicMock()
        db.query.return_value = _q([cfg])
        usuario = _usuario(empresa_id=1)

        data_mock = MagicMock()
        data_mock.model_dump.return_value = {}

        with self.assertRaises(HTTPException) as ctx:
            actualizar_configuracion(empresa_id=2, data=data_mock, db=db, usuario=usuario)
        self.assertEqual(ctx.exception.status_code, 403)


class KirkpatrickTenantTest(TestCase):
    def _mock_kirkpatrick(self, kirk_id=1, empresa_id=1):
        return SimpleNamespace(
            id=kirk_id, empresa_id=empresa_id, capacitacion_id=1,
            empleado_id=None, nivel1_satisfaccion=4, nivel2_aprobado=True,
            estado="COMPLETADO", activo=True,
        )

    def _mock_cap(self, cap_id=1, empresa_id=1):
        return SimpleNamespace(id=cap_id, empresa_id=empresa_id)

    def test_listar_filtra_empresa(self):
        db = MagicMock()
        db.query.return_value = _q([])
        usuario = _usuario(empresa_id=1)

        listar_evaluaciones(
            capacitacion_id=None, nivel=None, empresa_id=1,
            db=db, usuario=usuario,
        )

        textos = []
        for llamada in db.query.return_value.filter.call_args_list:
            for arg in llamada.args:
                textos.append(str(arg))
        self.assertTrue(any("empresa_id" in t for t in textos))

    def test_obtener_rechaza_empresa_ajena(self):
        db = MagicMock()
        db.query.return_value = _q([self._mock_kirkpatrick(empresa_id=2)])
        usuario = _usuario(empresa_id=1)

        with self.assertRaises(HTTPException) as ctx:
            obtener_evaluacion(evaluacion_id=1, db=db, usuario=usuario)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_actualizar_rechaza_empresa_ajena(self):
        db = MagicMock()
        db.query.return_value = _q([self._mock_kirkpatrick(empresa_id=2)])
        usuario = _usuario(empresa_id=1)

        data_mock = MagicMock()
        data_mock.model_dump.return_value = {}

        with self.assertRaises(HTTPException) as ctx:
            actualizar_evaluacion(evaluacion_id=1, data=data_mock, db=db, usuario=usuario)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_eliminar_rechaza_empresa_ajena(self):
        db = MagicMock()
        db.query.return_value = _q([self._mock_kirkpatrick(empresa_id=2)])
        usuario = _usuario(empresa_id=1)

        with self.assertRaises(HTTPException) as ctx:
            eliminar_evaluacion(evaluacion_id=1, db=db, usuario=usuario)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_resumen_rechaza_empresa_ajena(self):
        db = MagicMock()
        db.query.return_value = _q([self._mock_cap(empresa_id=2)])
        usuario = _usuario(empresa_id=1)

        with self.assertRaises(HTTPException) as ctx:
            resumen_kirkpatrick(capacitacion_id=1, db=db, usuario=usuario)
        self.assertEqual(ctx.exception.status_code, 403)


class CrossTenantLeakTest(TestCase):
    def test_kirkpatrick_listar_filtra_empresa_en_query(self):
        db = MagicMock()
        db.query.return_value = _q([])
        usuario = _usuario(empresa_id=5)

        listar_evaluaciones(
            capacitacion_id=None, nivel=None, empresa_id=5,
            db=db, usuario=usuario,
        )

        textos = []
        for llamada in db.query.return_value.filter.call_args_list:
            for arg in llamada.args:
                textos.append(str(arg))
        self.assertTrue(any("empresa_id" in t for t in textos))


if __name__ == "__main__":
    import unittest
    unittest.main()

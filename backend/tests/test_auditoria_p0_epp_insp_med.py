from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from app.routers.epp import (
    listar_catalogo,
    obtener_entrega,
    listar_evidencias_entrega,
    crear_catalogo,
    crear_entregas_lote,
)
from app.routers.inspecciones import (
    listar_inspecciones,
    obtener_inspeccion,
    listar_hallazgos,
    listar_evidencias,
)
from app.routers.inspeccion_seguimientos import listar_seguimientos_hallazgo
from app.routers.examenes_medicos import (
    listar_examenes_medicos,
    obtener_examen_medico,
    listar_evidencias_examen_medico,
    crear_examen_medico,
    actualizar_examen_medico,
    _validar_empleado,
)
from app.schemas.epp_schema import EPPCatalogoCreate, EPPEntregaLoteCreate, EPPEntregaItemLote
from app.schemas.examen_medico_schema import ExamenMedicoCreate, ExamenMedicoUpdate
from datetime import date


def _mock_empresa_query(db, empresa_id):
    """Mock para query que filtra por empresa_id"""
    empresa = SimpleNamespace(id=empresa_id)
    query_mock = MagicMock()
    query_mock.filter.return_value.first.return_value = empresa
    return query_mock


def _mock_query_with_tenant_check(db, tenant_id, model_cls, record_id=None):
    """Mock que simula query con validación de tenant"""
    query_mock = MagicMock()
    
    if record_id:
        # Simular búsqueda por ID + tenant
        record = SimpleNamespace(id=record_id, empresa_id=tenant_id)
        # La cadena: query.filter(...).filter(...).first()
        first_mock = MagicMock()
        first_mock.first.return_value = record
        query_mock.filter.return_value = first_mock
    else:
        # Simular listado
        record = SimpleNamespace(id=1, empresa_id=tenant_id)
        all_mock = MagicMock()
        all_mock.all.return_value = [record]
        query_mock.filter.return_value = all_mock
    
    return query_mock


class EPPAislamientoTest(TestCase):
    def test_listar_catalogo_superadmin_sin_empresa_lista_todas(self):
        db = MagicMock()
        query = MagicMock()
        db.query.return_value.options.return_value = query
        query.order_by.return_value.all.return_value = []
        usuario = SimpleNamespace(id=1, empresa_id=None, rol="SUPER_ADMIN")

        resultado = listar_catalogo(empresa_id=None, estado=None, q=None, db=db, usuario=usuario)

        self.assertEqual(resultado, [])
        query.filter.assert_not_called()
        query.order_by.assert_called_once()

    def test_crear_catalogo_asigna_empresa_autorizada_sin_duplicarla(self):
        db = MagicMock()
        empresa = SimpleNamespace(id=1)
        query_empresa = MagicMock()
        query_empresa.filter.return_value.first.return_value = empresa
        query_catalogo = MagicMock()
        query_catalogo.filter.return_value.first.return_value = None
        db.query.side_effect = [query_empresa, query_catalogo]
        db.refresh.side_effect = lambda item: setattr(item, "id", 1)
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")
        data = EPPCatalogoCreate(empresa_id=1, codigo="EPP-001", nombre="Casco")

        resultado = crear_catalogo(data=data, db=db, usuario=usuario)

        self.assertEqual(resultado.empresa_id, 1)
        self.assertEqual(resultado.codigo, "EPP-001")
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_listar_catalogo_rechaza_empresa_ajena(self):
        db = MagicMock()
        db.query.return_value = _mock_empresa_query(db, 2)
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as contexto:
            listar_catalogo(empresa_id=2, db=db, usuario=usuario)

        self.assertEqual(contexto.exception.status_code, 403)

    def test_obtener_entrega_rechaza_entrega_ajena(self):
        db = MagicMock()
        # La BD, con filtro (id, empresa_id), no devuelve la entrega ajena.
        query_mock = MagicMock()
        options_mock = MagicMock()
        filter_mock = MagicMock()
        filter_mock.first.return_value = None
        options_mock.filter.return_value = filter_mock
        query_mock.options.return_value = options_mock
        db.query.return_value = query_mock

        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as contexto:
            obtener_entrega(entrega_id=7, db=db, usuario=usuario)

        self.assertEqual(contexto.exception.status_code, 404)
        self.assertEqual(len(options_mock.filter.call_args.args), 2)

    def test_listar_evidencias_entrega_rechaza_entrega_ajena(self):
        db = MagicMock()
        query_mock = MagicMock()
        filter_mock = MagicMock()
        filter_mock.first.return_value = None
        query_mock.filter.return_value = filter_mock
        db.query.return_value = query_mock
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as contexto:
            listar_evidencias_entrega(entrega_id=7, db=db, usuario=usuario)

        self.assertEqual(contexto.exception.status_code, 404)

    def test_crear_entregas_lote_rechaza_empresa_ajena(self):
        db = MagicMock()
        # Mock empresa validation
        empresa = SimpleNamespace(id=2)
        query_empresa = MagicMock()
        query_empresa.filter.return_value.first.return_value = empresa
        # Mock empleado validation
        empleado = SimpleNamespace(id=1, empresa_id=2)
        query_empleado = MagicMock()
        query_empleado.filter.return_value.first.return_value = empleado
        # Mock epp validation
        epp = SimpleNamespace(id=1, empresa_id=2, nombre="Casco", requiere_reposicion=False)
        query_epp = MagicMock()
        query_epp.filter.return_value.first.return_value = epp
        # Mock entregas creadas
        entrega_creada = SimpleNamespace(
            id=1, empresa_id=2, empleado_id=1, epp_id=1,
            cantidad=1, fecha_entrega=date(2026, 9, 4), 
            estado="ENTREGADO", activo=True,
            empresa=SimpleNamespace(nombre="Empresa 2"),
            empleado=SimpleNamespace(nombres="Juan", apellidos="Perez", documento="123", correo="j@p.com", sede_id=None, area_id=None, cargo_id=None, sede=None, area=None, cargo=None),
            epp=SimpleNamespace(codigo="EPP-001", nombre="Casco", categoria="CABEZA", vida_util_dias=365)
        )
        query_entregas = MagicMock()
        options_mock = MagicMock()
        filter_mock = MagicMock()
        filter_mock.first.return_value = entrega_creada
        options_mock.filter.return_value = filter_mock
        query_entregas.options.return_value = options_mock
        
        db.query.side_effect = [query_empresa, query_empleado, query_epp, query_entregas]
        db.refresh.side_effect = lambda x: setattr(x, 'id', 1) if not getattr(x, 'id', None) else None
        
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")
        data = EPPEntregaLoteCreate(
            empresa_id=2,
            empleado_id=1,
            fecha_entrega=date(2026, 9, 4),
            items=[EPPEntregaItemLote(epp_id=1, cantidad=1)],
        )

        with self.assertRaises(HTTPException) as contexto:
            crear_entregas_lote(data=data, db=db, usuario=usuario)

        self.assertEqual(contexto.exception.status_code, 403)


class InspeccionesAislamientoTest(TestCase):
    def test_listar_inspecciones_rechaza_empresa_ajena(self):
        db = MagicMock()
        db.query.return_value = _mock_empresa_query(db, 2)
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as contexto:
            listar_inspecciones(empresa_id=2, db=db, usuario=usuario)

        self.assertEqual(contexto.exception.status_code, 403)

    def test_obtener_inspeccion_rechaza_inspeccion_ajena(self):
        db = MagicMock()
        # La BD, con filtro de tenant, no devuelve la inspección ajena.
        query_mock = MagicMock()
        query_mock.options.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.first.return_value = None
        db.query.return_value = query_mock

        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as contexto:
            obtener_inspeccion(inspeccion_id=7, db=db, usuario=usuario)

        self.assertEqual(contexto.exception.status_code, 404)

    def test_listar_hallazgos_rechaza_inspeccion_ajena(self):
        db = MagicMock()
        query_mock = MagicMock()
        filter_mock = MagicMock()
        filter_mock.first.return_value = None
        query_mock.filter.return_value = filter_mock
        db.query.return_value = query_mock
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as contexto:
            listar_hallazgos(inspeccion_id=7, db=db, usuario=usuario)

        self.assertEqual(contexto.exception.status_code, 404)

    def test_listar_evidencias_rechaza_inspeccion_ajena(self):
        db = MagicMock()
        query_mock = MagicMock()
        filter_mock = MagicMock()
        filter_mock.first.return_value = None
        query_mock.filter.return_value = filter_mock
        db.query.return_value = query_mock
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as contexto:
            listar_evidencias(inspeccion_id=7, db=db, usuario=usuario)

        self.assertEqual(contexto.exception.status_code, 404)


class SeguimientosAislamientoTest(TestCase):
    def test_listar_seguimientos_rechaza_hallazgo_ajeno(self):
        db = MagicMock()
        query_mock = MagicMock()
        options_mock = MagicMock()
        filter_mock = MagicMock()
        filter_mock.first.return_value = None
        options_mock.filter.return_value = filter_mock
        query_mock.options.return_value = options_mock
        db.query.return_value = query_mock
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as contexto:
            listar_seguimientos_hallazgo(hallazgo_id=7, db=db, usuario=usuario)

        self.assertEqual(contexto.exception.status_code, 404)


class EvaluacionesMedicasAislamientoTest(TestCase):
    def test_actualizar_examen_superadmin_sin_empresa_busca_solo_por_id(self):
        db = MagicMock()
        examen = SimpleNamespace(
            id=1,
            empleado_id=5,
            fecha_vencimiento=None,
            fecha_actualizacion=None,
        )
        query = MagicMock()
        query.filter.return_value = query
        query.first.return_value = examen
        db.query.return_value = query
        usuario = SimpleNamespace(id=1, empresa_id=None, rol="SUPER_ADMIN")
        data = ExamenMedicoUpdate(observaciones="Control actualizado")

        with patch("app.routers.examenes_medicos._examen_to_response", return_value=SimpleNamespace()):
            actualizar_examen_medico(examen_id=1, data=data, db=db, usuario=usuario)

        self.assertEqual(query.filter.call_count, 1)
        self.assertEqual(examen.observaciones, "Control actualizado")
        db.commit.assert_called_once()

    def test_crear_examen_asigna_empleado_sin_duplicarlo(self):
        db = MagicMock()
        empleado = SimpleNamespace(id=5, empresa_id=1)
        query = MagicMock()
        query.options.return_value = query
        query.filter.return_value = query
        query.first.return_value = empleado
        db.query.return_value = query
        db.refresh.side_effect = lambda examen: setattr(examen, "id", 1)
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")
        data = ExamenMedicoCreate(
            empleado_id=5,
            tipo_examen="INGRESO",
            fecha_examen=date(2026, 9, 10),
            concepto="APTO",
            activo=True,
        )

        resultado = crear_examen_medico(data=data, db=db, usuario=usuario)

        self.assertEqual(resultado.empleado_id, 5)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_listar_examenes_rechaza_empresa_ajena(self):
        db = MagicMock()
        db.query.return_value = _mock_empresa_query(db, 2)
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as contexto:
            listar_examenes_medicos(empresa_id=2, db=db, usuario=usuario)

        self.assertEqual(contexto.exception.status_code, 403)

    def test_obtener_examen_rechaza_examen_ajeno(self):
        db = MagicMock()
        empleado = SimpleNamespace(
            id=5, empresa_id=2, nombres="Juan", apellidos="Perez", 
            documento="123", correo="j@p.com",
            empresa=SimpleNamespace(nombre="Empresa 2"),
            sede=SimpleNamespace(nombre="Sede 1"),
            area=SimpleNamespace(nombre="Area 1"),
            cargo=SimpleNamespace(nombre="Cargo 1")
        )
        # La BD, con filtro de tenant, no devuelve el examen ajeno.
        query_mock = MagicMock()
        options_mock = MagicMock()
        filter_mock = MagicMock()
        filter_mock.first.return_value = None
        options_mock.filter.return_value = filter_mock
        query_mock.options.return_value = options_mock
        db.query.return_value = query_mock

        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as contexto:
            obtener_examen_medico(examen_id=7, db=db, usuario=usuario)

        self.assertEqual(contexto.exception.status_code, 404)

    def test_listar_evidencias_examen_rechaza_examen_ajeno(self):
        db = MagicMock()
        query_mock = MagicMock()
        query_mock.options.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        db.query.return_value = query_mock
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as contexto:
            listar_evidencias_examen_medico(examen_id=7, db=db, usuario=usuario)

        self.assertEqual(contexto.exception.status_code, 404)

    def test_validar_empleado_rechaza_empleado_ajeno(self):
        db = MagicMock()
        query_mock = MagicMock()
        query_mock.options.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        db.query.return_value = query_mock

        with self.assertRaises(HTTPException) as contexto:
            _validar_empleado(db, empleado_id=5, empresa_id=1)

        self.assertEqual(contexto.exception.status_code, 404)
        # El filtro de empresa debe aplicarse (id + empresa_id).
        textos = [str(c.args[0]) for c in query_mock.filter.call_args_list]
        self.assertTrue(any("empresa_id" in t for t in textos))


if __name__ == "__main__":
    import unittest
    unittest.main()
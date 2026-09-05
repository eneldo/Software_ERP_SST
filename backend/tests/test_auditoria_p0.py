from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock

from fastapi import HTTPException

from app.models.capa import CapaSST, CapaSeguimientoSST
from app.routers.incidentes import listar_evidencias, listar_lesionados
from app.routers.matriz_iper import _calcular_campos_riesgo, crear_fila_iper
from app.schemas.matriz_iper_schema import MatrizIPERCreate
from app.schemas.medidas_correctivas_schema import (
    MedidaCorrectivaCreate,
    MedidaCorrectivaSeguimientoCreate,
)


class AlineacionCapaTest(TestCase):
    def test_modelo_acepta_campos_expuestos_por_schema(self):
        data = MedidaCorrectivaCreate(
            empresa_id=1,
            codigo="MC-001",
            titulo="Control de hallazgo",
            descripcion="Corregir condición insegura",
            ishikawa_json='{"metodo": "Sin procedimiento"}',
            costo_estimado=150000,
            costo_real=100000,
            requiere_aprobacion=True,
        )

        item = CapaSST(**data.model_dump())

        self.assertEqual(item.ishikawa_json, '{"metodo": "Sin procedimiento"}')
        self.assertEqual(item.costo_estimado, 150000)
        self.assertTrue(item.requiere_aprobacion)

    def test_modelo_seguimiento_acepta_proxima_accion_y_fecha(self):
        data = MedidaCorrectivaSeguimientoCreate(
            comentario="Se instaló el control",
            proxima_accion="Verificar eficacia",
            fecha_proximo_seguimiento="2026-09-10",
        )

        item = CapaSeguimientoSST(capa_id=1, empresa_id=1, **data.model_dump())

        self.assertEqual(item.proxima_accion, "Verificar eficacia")
        self.assertEqual(str(item.fecha_proximo_seguimiento), "2026-09-10")


class AislamientoIncidentesTest(TestCase):
    def test_listar_lesionados_rechaza_incidente_de_otro_tenant(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(
            id=7, empresa_id=2
        )
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as contexto:
            listar_lesionados(incidente_id=7, db=db, usuario=usuario)

        self.assertEqual(contexto.exception.status_code, 403)

    def test_listar_evidencias_rechaza_incidente_de_otro_tenant(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(
            id=7, empresa_id=2
        )
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as contexto:
            listar_evidencias(incidente_id=7, db=db, usuario=usuario)

        self.assertEqual(contexto.exception.status_code, 403)


class SeguridadIperTest(TestCase):
    def test_creacion_rechaza_empresa_de_otro_tenant(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(id=2)
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")
        data = MatrizIPERCreate(
            empresa_id=2,
            proceso="Operación",
            clasificacion_peligro="FISICO",
            descripcion_peligro="Ruido",
            efectos_posibles="Hipoacusia",
        )

        with self.assertRaises(HTTPException) as contexto:
            crear_fila_iper(data=data, db=db, usuario=usuario)

        self.assertEqual(contexto.exception.status_code, 403)
        db.add.assert_not_called()

    def test_recalculo_parcial_conserva_valores_almacenados(self):
        payload = _calcular_campos_riesgo(
            {"proceso": "Operación actualizada"},
            valores_base={"nd": 10, "ne": 2, "nc": 25},
        )

        self.assertEqual(payload["np"], 20)
        self.assertEqual(payload["nr"], 500)

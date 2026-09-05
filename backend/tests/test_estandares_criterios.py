from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock

from app.models.estandar_minimo_criterio import EstandarMinimoCriterio
from app.routers.evaluacion_inicial import listar_criterios
from app.services.estandares_evaluacion_sst import obtener_criterios_parametrizados


def _q(items):
    q = MagicMock()
    q.filter.return_value = q
    q.all.return_value = items
    return q


def _fila(tipo="7"):
    return SimpleNamespace(
        id=1, tipo_estandares=tipo, estandar="Recursos",
        numeral="1.1.1", criterio="Asignar responsable.",
        puntaje=1, version_norma="0312-2019", activo=True,
    )


class EstandaresCriteriosTest(TestCase):
    def test_modelo_acepta_campos(self):
        item = EstandarMinimoCriterio(
            tipo_estandares="7", estandar="Recursos", numeral="1.1.1",
            criterio="Asignar responsable.", puntaje=1,
            version_norma="0312-2019",
        )

        self.assertEqual(item.numeral, "1.1.1")
        self.assertEqual(item.version_norma, "0312-2019")

    def test_endpoint_devuelve_bd_primero(self):
        db = MagicMock()
        db.query.return_value = _q([_fila("7"), _fila("7")])
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="AUDITOR")

        resp = listar_criterios(tipo="7", db=db, usuario=usuario)

        self.assertEqual(len(resp), 2)
        self.assertEqual(resp[0]["numeral"], "1.1.1")
        self.assertEqual(resp[0]["origen"], "BD")

    def test_endpoint_recurre_a_constantes(self):
        db = MagicMock()
        db.query.return_value = _q([])
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="AUDITOR")

        resp = listar_criterios(tipo="7", db=db, usuario=usuario)

        self.assertEqual(len(resp), 7)
        self.assertEqual(resp[0]["origen"], "BASE")
        self.assertTrue(all("numeral" in c for c in resp))


if __name__ == "__main__":
    import unittest
    unittest.main()

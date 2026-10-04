from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock

from fastapi import HTTPException

from app.routers.areas import listar_areas, obtener_area
from app.routers.objetivos_sst import listar_objetivos, actualizar_objetivo
from app.schemas.objetivo_sst_schema import ObjetivoSSTUpdate


def _query(items):
    query = MagicMock()
    query.join.return_value = query
    query.outerjoin.return_value = query
    query.filter.return_value = query
    query.order_by.return_value = query
    query.first.return_value = items[0] if items else None
    query.all.return_value = items
    return query


class AreasObjetivosTenantTest(TestCase):
    def test_listar_areas_rechaza_empresa_ajena(self):
        db = MagicMock()
        usuario = SimpleNamespace(empresa_id=1, rol="ADMIN_EMPRESA")

        with self.assertRaises(HTTPException) as ctx:
            listar_areas(empresa_id=2, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 403)
        db.query.assert_not_called()

    def test_obtener_area_ajena_responde_no_encontrada(self):
        db = MagicMock()
        db.query.return_value = _query([])
        usuario = SimpleNamespace(empresa_id=1, rol="ADMIN_EMPRESA")

        with self.assertRaises(HTTPException) as ctx:
            obtener_area(area_id=7, db=db, usuario=usuario)

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(db.query.return_value.filter.call_count, 2)

    def test_listar_objetivos_filtra_tenant_del_usuario(self):
        db = MagicMock()
        db.query.return_value = _query([])
        usuario = SimpleNamespace(empresa_id=1, rol="AUDITOR")

        listar_objetivos(empresa_id=None, db=db, usuario=usuario)

        self.assertEqual(db.query.return_value.filter.call_count, 1)

    def test_actualizar_objetivo_ajeno_responde_no_encontrado(self):
        db = MagicMock()
        db.query.return_value = _query([])
        usuario = SimpleNamespace(empresa_id=1, rol="RESPONSABLE_SST")

        with self.assertRaises(HTTPException) as ctx:
            actualizar_objetivo(
                objetivo_id=9,
                data=ObjetivoSSTUpdate(objetivo="Actualizado"),
                db=db,
                usuario=usuario,
            )

        self.assertEqual(ctx.exception.status_code, 404)
        db.commit.assert_not_called()


if __name__ == "__main__":
    import unittest

    unittest.main()

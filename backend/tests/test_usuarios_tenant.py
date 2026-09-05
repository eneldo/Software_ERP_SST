from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock

from fastapi import HTTPException

from app.routers.usuarios_sistema import (
    estadisticas_usuarios,
    listar_usuarios_sistema,
    obtener_usuario_sistema,
)


def _q_list(items):
    q = MagicMock()
    q.filter.return_value = q
    q.order_by.return_value = q
    q.offset.return_value = q
    q.limit.return_value = q
    q.all.return_value = items
    q.first.return_value = items[0] if items else None
    q.count.return_value = len(items)
    return q


def _filtros_texto(q):
    textos = []
    for llamada in q.filter.call_args_list:
        for arg in llamada.args:
            textos.append(str(arg))
    return textos


class UsuariosTenantTest(TestCase):
    def test_listar_filtra_empresa_usuario(self):
        db = MagicMock()
        db.query.return_value = _q_list([])
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="ADMIN_EMPRESA")

        listar_usuarios_sistema(
            buscar=None, rol=None, activo=None, skip=0, limit=100,
            db=db, usuario_actual=usuario,
        )

        textos = _filtros_texto(db.query.return_value)
        self.assertTrue(
            any("empresa_id" in t for t in textos),
            f"El listado debe filtrar por empresa_id. Filtros: {textos}",
        )

    def test_obtener_rechaza_usuario_ajeno(self):
        db = MagicMock()
        # La BD, con filtro (id, empresa_id), no devuelve el usuario ajeno.
        db.query.return_value = _q_list([])
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="ADMIN_EMPRESA")

        with self.assertRaises(HTTPException) as ctx:
            obtener_usuario_sistema(usuario_id=7, db=db, usuario_actual=usuario)

        self.assertEqual(ctx.exception.status_code, 404)
        textos = _filtros_texto(db.query.return_value)
        self.assertTrue(any("empresa_id" in t for t in textos))

    def test_stats_solo_empresa_usuario(self):
        db = MagicMock()
        db.query.return_value = _q_list([])
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="ADMIN_EMPRESA")

        estadisticas_usuarios(db=db, usuario_actual=usuario)

        # Los conteos deben filtrar por empresa_id del usuario.
        todos = _filtros_texto(db.query.return_value)
        self.assertTrue(
            any("empresa_id" in t for t in todos),
            f"Las estadísticas deben filtrar por empresa_id. Filtros: {todos}",
        )


if __name__ == "__main__":
    import unittest
    unittest.main()

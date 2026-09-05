from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock

from fastapi import HTTPException

from app.routers.empleados import _empresa_id_autorizada, eliminar_empleado


class SeguridadEmpleadosTest(TestCase):
    def test_listado_fuerza_empresa_del_usuario(self):
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="ADMIN_EMPRESA")

        self.assertEqual(_empresa_id_autorizada(usuario, None), 1)

    def test_listado_rechaza_empresa_distinta(self):
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="ADMIN_EMPRESA")

        with self.assertRaises(HTTPException) as contexto:
            _empresa_id_autorizada(usuario, 2)

        self.assertEqual(contexto.exception.status_code, 403)

    def test_admin_empresa_no_desactiva_empleado_de_otro_tenant(self):
        empleado = SimpleNamespace(
            id=20,
            empresa_id=2,
            activo=True,
            estado_laboral="ACTIVO",
        )
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = empleado
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="ADMIN_EMPRESA")

        with self.assertRaises(HTTPException) as contexto:
            eliminar_empleado(empleado_id=20, db=db, usuario=usuario)

        self.assertEqual(contexto.exception.status_code, 403)
        self.assertTrue(empleado.activo)
        db.commit.assert_not_called()

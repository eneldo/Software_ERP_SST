from datetime import date
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock

from fastapi import HTTPException

from app.routers.comites_sst import crear_comite
from app.routers.emergencias_sst import crear_amenaza, crear_brigada
from app.schemas.comite_sst_schema import ComiteCreate
from app.schemas.emergencia_sst_schema import AmenazaCreate, BrigadaCreate


def _db_con_empresa(empresa_id: int = 1) -> MagicMock:
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(
        id=empresa_id
    )

    def refrescar(registro):
        registro.id = 1
        if getattr(registro, "activo", None) is None:
            registro.activo = True

    db.refresh.side_effect = refrescar
    return db


class CreacionEmergenciasTest(TestCase):
    def test_crear_brigada_no_duplica_empresa_id(self):
        db = _db_con_empresa()
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")
        data = BrigadaCreate(
            empresa_id=1,
            nombre="Brigada integral",
            tipo_brigada="EVACUACION",
            fecha_conformacion=date(2026, 9, 4),
        )

        crear_brigada(data=data, db=db, usuario=usuario)

        brigada = db.add.call_args.args[0]
        self.assertEqual(brigada.empresa_id, 1)
        self.assertEqual(brigada.usuario_id, 10)

    def test_crear_amenaza_calcula_nivel_de_riesgo(self):
        db = _db_con_empresa()
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")
        data = AmenazaCreate(
            empresa_id=1,
            nombre="Sismo",
            tipo_amenaza="NATURAL",
            probabilidad="ALTA",
            impacto="ALTO",
        )

        crear_amenaza(data=data, db=db, usuario=usuario)

        amenaza = db.add.call_args.args[0]
        self.assertEqual(amenaza.nivel_riesgo, "CRITICO")


class AislamientoEmpresasTest(TestCase):
    def test_responsable_no_puede_crear_comite_en_otra_empresa(self):
        db = _db_con_empresa(empresa_id=2)
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")
        data = ComiteCreate(
            empresa_id=2,
            tipo_comite="COPASST",
            nombre="COPASST sede externa",
        )

        with self.assertRaises(HTTPException) as contexto:
            crear_comite(data=data, db=db, usuario=usuario)

        self.assertEqual(contexto.exception.status_code, 403)

    def test_responsable_no_puede_crear_emergencia_en_otra_empresa(self):
        db = _db_con_empresa(empresa_id=2)
        usuario = SimpleNamespace(id=10, empresa_id=1, rol="RESPONSABLE_SST")
        data = BrigadaCreate(
            empresa_id=2,
            nombre="Brigada externa",
            tipo_brigada="INCENDIO",
        )

        with self.assertRaises(HTTPException) as contexto:
            crear_brigada(data=data, db=db, usuario=usuario)

        self.assertEqual(contexto.exception.status_code, 403)

# ============================================================
# TESTS: Matriz IPER - GTC 45
# Identificacion de Peligros, Evaluacion y Valoracion de Riesgos
# ============================================================

import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from app.routers.matriz_iper import (
    _calcular_np_ne,
    _calcular_nr,
    _interpretar_np,
    _interpretar_nr,
    _aceptabilidad,
    _nivel_riesgo_romano,
    _calcular_campos_riesgo,
    _empresa_id_autorizada,
    serializar,
)
from app.models.matriz_iper import MatrizIPER
from app.schemas.matriz_iper_schema import MatrizIPERCreate, MatrizIPERUpdate


# --- 1. CALCULOS GTC45 ---


class TestCalculosGTC45:
    def test_calcular_np_ne(self):
        assert _calcular_np_ne(10, 4) == 40
        assert _calcular_np_ne(6, 3) == 18
        assert _calcular_np_ne(2, 1) == 2
        assert _calcular_np_ne(0, 1) == 0
        assert _calcular_np_ne(0, 0) == 0

    def test_calcular_nr(self):
        assert _calcular_nr(40, 100) == 4000
        assert _calcular_nr(18, 25) == 450
        assert _calcular_nr(2, 10) == 20
        assert _calcular_nr(0, 10) == 0
        assert _calcular_nr(6, 60) == 360

    def test_interpretar_np(self):
        assert _interpretar_np(40) == "Muy Alto"
        assert _interpretar_np(24) == "Muy Alto"
        assert _interpretar_np(23) == "Alto"
        assert _interpretar_np(10) == "Alto"
        assert _interpretar_np(9) == "Medio"
        assert _interpretar_np(6) == "Medio"
        assert _interpretar_np(5) == "Bajo"
        assert _interpretar_np(0) == "Bajo"

    def test_interpretar_nr(self):
        assert _interpretar_nr(4000) == "No Aceptable"
        assert _interpretar_nr(600) == "No Aceptable"
        assert _interpretar_nr(599) == "No Aceptable / Control Específico"
        assert _interpretar_nr(150) == "No Aceptable / Control Específico"
        assert _interpretar_nr(149) == "Aceptable Mejorable"
        assert _interpretar_nr(40) == "Aceptable Mejorable"
        assert _interpretar_nr(39) == "Aceptable"
        assert _interpretar_nr(0) == "Aceptable"

    def test_aceptabilidad(self):
        assert _aceptabilidad(4000) == "NO ACEPTABLE"
        assert _aceptabilidad(600) == "NO ACEPTABLE"
        assert _aceptabilidad(599) == "CON CONTROL ESPECÍFICO"
        assert _aceptabilidad(150) == "CON CONTROL ESPECÍFICO"
        assert _aceptabilidad(149) == "MEJORABLE"
        assert _aceptabilidad(40) == "MEJORABLE"
        assert _aceptabilidad(39) == "ACEPTABLE"
        assert _aceptabilidad(0) == "ACEPTABLE"

    def test_nivel_riesgo_romano(self):
        assert _nivel_riesgo_romano(4000) == "I"
        assert _nivel_riesgo_romano(600) == "I"
        assert _nivel_riesgo_romano(599) == "II"
        assert _nivel_riesgo_romano(150) == "II"
        assert _nivel_riesgo_romano(149) == "III"
        assert _nivel_riesgo_romano(40) == "III"
        assert _nivel_riesgo_romano(39) == "IV"
        assert _nivel_riesgo_romano(0) == "IV"


# --- 2. CALCULO COMPLETO DE RIESGO ---


class TestCalcularCamposRiesgo:
    def test_calculo_completo_maximo(self):
        data = {"nd": 10, "ne": 4, "nc": 100}
        result = _calcular_campos_riesgo(data)
        assert result["np"] == 40
        assert result["nr"] == 4000
        assert result["interpretacion_np"] == "Muy Alto"
        assert result["interpretacion_nr"] == "No Aceptable"
        assert result["nivel_riesgo"] == "I"
        assert result["aceptabilidad"] == "NO ACEPTABLE"

    def test_calculo_valores_por_defecto(self):
        data = {}
        result = _calcular_campos_riesgo(data)
        assert result["np"] == 0
        assert result["nr"] == 0
        assert result["interpretacion_np"] == "Bajo"
        assert result["interpretacion_nr"] == "Aceptable"
        assert result["nivel_riesgo"] == "IV"
        assert result["aceptabilidad"] == "ACEPTABLE"

    def test_calculo_con_valores_base(self):
        data = {"nc": 60}
        base = {"nd": 6, "ne": 3}
        result = _calcular_campos_riesgo(data, valores_base=base)
        assert result["np"] == 18
        assert result["nr"] == 1080
        assert result["nivel_riesgo"] == "I"
        assert result["aceptabilidad"] == "NO ACEPTABLE"

    def test_calculo_medio(self):
        data = {"nd": 2, "ne": 2, "nc": 10}
        result = _calcular_campos_riesgo(data)
        assert result["np"] == 4
        assert result["nr"] == 40
        assert result["interpretacion_np"] == "Bajo"
        assert result["nivel_riesgo"] == "III"
        assert result["aceptabilidad"] == "MEJORABLE"


# --- 3. MODELO ---


class TestMatrizIPERModel:
    def test_model_has_required_fields(self):
        columns = {c.name for c in MatrizIPER.__table__.columns}
        required = [
            "id", "empresa_id", "usuario_id",
            "proceso", "zona_lugar", "actividades", "tareas", "rutinaria",
            "clasificacion_peligro", "descripcion_peligro", "riesgo", "efectos_posibles",
            "fuente", "medio", "individuo",
            "nd", "ne", "np", "interpretacion_np",
            "nc", "nr", "interpretacion_nr", "nivel_riesgo", "aceptabilidad",
            "expuestos_hombres", "expuestos_mujeres", "expuestos_gestantes",
            "peor_consecuencia",
            "eliminacion", "control_ingenieria", "sustitucion",
            "senalizacion_admin", "epp", "responsable",
            "fecha_proyectada", "fecha_ejecucion", "evidencias", "realizado",
            "activo", "fecha_creacion", "fecha_actualizacion",
        ]
        for field in required:
            assert field in columns, f"Campo {field} no encontrado en MatrizIPER"


# --- 4. SCHEMAS ---


class TestMatrizIPERSchemas:
    def test_schema_create_campos_obligatorios(self):
        data = {
            "empresa_id": 1,
            "proceso": "Administrativo",
            "clasificacion_peligro": "FISICO",
            "descripcion_peligro": "Ruido excesivo",
            "efectos_posibles": "Hipoacusia",
        }
        schema = MatrizIPERCreate(**data)
        assert schema.empresa_id == 1
        assert schema.proceso == "Administrativo"
        assert schema.clasificacion_peligro == "FISICO"
        assert schema.nd == 0
        assert schema.ne == 1
        assert schema.nc == 10

    def test_schema_create_falta_empresa_id(self):
        with pytest.raises(Exception):
            MatrizIPERCreate(
                proceso="Test",
                clasificacion_peligro="FISICO",
                descripcion_peligro="Test",
                efectos_posibles="Test",
            )

    def test_schema_update_todos_opcionales(self):
        schema = MatrizIPERUpdate()
        assert schema.proceso is None
        assert schema.nd is None
        assert schema.ne is None
        assert schema.nc is None
        assert schema.activo is None


# --- 5. AUTORIZACION ---


class TestAutorizacion:
    def test_empresa_id_autorizada_super_admin(self):
        usuario = MagicMock()
        usuario.rol = "SUPER_ADMIN"
        result = _empresa_id_autorizada(usuario, 99)
        assert result == 99

    def test_empresa_id_autorizada_super_admin_none(self):
        usuario = MagicMock()
        usuario.rol = "SUPER_ADMIN"
        result = _empresa_id_autorizada(usuario, None)
        assert result is None

    def test_empresa_id_autorizada_usuario_empresa(self):
        usuario = MagicMock()
        usuario.rol = "ADMIN_EMPRESA"
        usuario.empresa_id = 5
        result = _empresa_id_autorizada(usuario, 5)
        assert result == 5

    def test_empresa_id_autorizada_usuario_sin_permiso(self):
        usuario = MagicMock()
        usuario.rol = "ADMIN_EMPRESA"
        usuario.empresa_id = 5
        with pytest.raises(HTTPException) as exc_info:
            _empresa_id_autorizada(usuario, 99)
        assert exc_info.value.status_code == 403

    def test_empresa_id_autorizada_usuario_sin_empresa(self):
        usuario = MagicMock()
        usuario.rol = "ADMIN_EMPRESA"
        usuario.empresa_id = None
        with pytest.raises(HTTPException) as exc_info:
            _empresa_id_autorizada(usuario, 1)
        assert exc_info.value.status_code == 403


# --- 6. VALIDACION ---


class TestValidacion:
    def test_crear_lote_vacio_lanza_error(self):
        from app.routers.matriz_iper import crear_lote_iper
        db = MagicMock()
        usuario = MagicMock()
        usuario.rol = "SUPER_ADMIN"
        with pytest.raises(HTTPException) as exc_info:
            crear_lote_iper([], db=db, usuario=usuario)
        assert exc_info.value.status_code == 400


# --- 7. SERIALIZACION ---


class TestSerializar:
    def test_serializar_campos_completos(self):
        item = MagicMock(spec=MatrizIPER)
        item.id = 1
        item.empresa_id = 9
        item.usuario_id = 1
        item.proceso = "Administrativo"
        item.zona_lugar = "Oficina"
        item.actividades = "Digitacion"
        item.tareas = "Ingresar datos"
        item.rutinaria = "SI"
        item.clasificacion_peligro = "BIOMECANICO"
        item.descripcion_peligro = "Movimientos repetitivos"
        item.riesgo = "Fatiga"
        item.efectos_posibles = "Tendinitis"
        item.fuente = "Ninguno"
        item.medio = "Ergonomia"
        item.individuo = "EPP"
        item.nd = 6
        item.ne = 3
        item.np = 18
        item.interpretacion_np = "Alto"
        item.nc = 25
        item.nr = 450
        item.interpretacion_nr = "No Aceptable / Control Específico"
        item.nivel_riesgo = "II"
        item.aceptabilidad = "CON CONTROL ESPECÍFICO"
        item.expuestos_hombres = 5
        item.expuestos_mujeres = 3
        item.expuestos_gestantes = 1
        item.peor_consecuencia = "ILT"
        item.eliminacion = "N.A"
        item.control_ingenieria = "N.A"
        item.sustitucion = "N.A"
        item.senalizacion_admin = "Pausas activas"
        item.epp = "Guantes"
        item.responsable = "Ing. SST"
        item.fecha_proyectada = None
        item.fecha_ejecucion = None
        item.evidencias = "Foto"
        item.realizado = "NO"
        item.activo = True
        item.fecha_creacion = None
        item.fecha_actualizacion = None

        result = serializar(item)

        assert result["id"] == 1
        assert result["empresa_id"] == 9
        assert result["proceso"] == "Administrativo"
        assert result["nd"] == 6
        assert result["ne"] == 3
        assert result["np"] == 18
        assert result["nc"] == 25
        assert result["nr"] == 450
        assert result["nivel_riesgo"] == "II"
        assert result["aceptabilidad"] == "CON CONTROL ESPECÍFICO"
        assert result["activo"] is True
        assert len(result) == 41

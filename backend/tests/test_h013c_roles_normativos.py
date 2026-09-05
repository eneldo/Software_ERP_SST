# ============================================================
# TESTS: H-013c Matriz de Roles Normativos
# ============================================================

import pytest

from app.routers.roles_normativos import MATRIZ_ROLES


class TestMatrizRolesNormativos:
    def test_matriz_roles_has_required_keys(self):
        required_roles = [
            "SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST",
            "COORDINADOR_SST", "AUDITOR_INT", "MEDICO", "COPASST",
            "OPERARIO", "APRENDIZ",
        ]
        for rol in required_roles:
            assert rol in MATRIZ_ROLES, f"Rol {rol} no encontrado en matriz"

    def test_cada_rol_tiene_campos_requeridos(self):
        required_fields = [
            "nombre", "descripcion", "empresa_requerida",
            "acceso_global", "normatividad", "responsabilidades",
            "permisos_especiales",
        ]
        for rol, info in MATRIZ_ROLES.items():
            for field in required_fields:
                assert field in info, f"Campo {field} no encontrado en rol {rol}"

    def test_super_admin_acceso_global(self):
        assert MATRIZ_ROLES["SUPER_ADMIN"]["acceso_global"] is True
        assert MATRIZ_ROLES["SUPER_ADMIN"]["empresa_requerida"] is False

    def test_admin_empresa_requiere_empresa(self):
        assert MATRIZ_ROLES["ADMIN_EMPRESA"]["empresa_requerida"] is True
        assert MATRIZ_ROLES["ADMIN_EMPRESA"]["acceso_global"] is False

    def test_responsable_sst_normatividad(self):
        normatividad = MATRIZ_ROLES["RESPONSABLE_SST"]["normatividad"]
        assert len(normatividad) >= 2
        assert any("Decreto 1072" in n for n in normatividad)

    def test_medico_permisos_especiales(self):
        permisos = MATRIZ_ROLES["MEDICO"]["permisos_especiales"]
        assert "EXAMENES_MEDICOS" in permisos
        assert "HISTORIA_CLINICA_WRITE" in permisos

    def test_copasst_normatividad(self):
        normatividad = MATRIZ_ROLES["COPASST"]["normatividad"]
        assert any("Comité Paritario" in n for n in normatividad)

    def test_todos_los_roles_tienen_nombre_humano(self):
        for rol, info in MATRIZ_ROLES.items():
            assert len(info["nombre"]) > 5, f"Nombre muy corto para {rol}"
            assert len(info["descripcion"]) > 10, f"Descripción muy corta para {rol}"

    def test_roles_jerarquicos_acceso_progresivo(self):
        assert MATRIZ_ROLES["SUPER_ADMIN"]["acceso_global"] is True
        assert MATRIZ_ROLES["ADMIN_EMPRESA"]["acceso_global"] is False
        assert MATRIZ_ROLES["RESPONSABLE_SST"]["acceso_global"] is False
        assert MATRIZ_ROLES["OPERARIO"]["acceso_global"] is False

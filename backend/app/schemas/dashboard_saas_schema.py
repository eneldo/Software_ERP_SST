# ============================================================
# SCHEMA DASHBOARD SAAS PRO
# ERP SST PRO
# ============================================================

from pydantic import BaseModel


class DashboardSaaSResponse(BaseModel):
    total_empresas: int
    total_sedes: int
    total_areas: int
    total_cargos: int
    total_empleados: int
    total_usuarios: int
    total_roles: int
    total_permisos: int
    total_auditorias: int
    total_logins: int

    empleados_activos: int
    empleados_inactivos: int

    empresas_activas: int
    sedes_activas: int
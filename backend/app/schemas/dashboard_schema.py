from pydantic import BaseModel


class DashboardAdminResponse(BaseModel):
    total_empresas: int
    total_sedes: int
    total_areas: int
    total_cargos: int
    total_empleados: int
    total_usuarios: int
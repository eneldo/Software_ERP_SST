# ============================================================
# SCHEMAS
# DASHBOARD SST INTELIGENTE
# FASE 1.5.4
# ERP SST PRO
# ============================================================

from pydantic import BaseModel


# ============================================================
# EMPRESA SST
# ============================================================

class DashboardEmpresaSST(BaseModel):
    empresa_id: int
    empresa: str

    total_estandares: int

    cumplen: int
    no_cumplen: int
    no_aplican: int

    porcentaje: float

    nivel: str


# ============================================================
# DASHBOARD SST GLOBAL
# ============================================================

class DashboardSSTResponse(BaseModel):

    # --------------------------------------------------------
    # EMPRESAS
    # --------------------------------------------------------

    total_empresas: int

    empresas_aceptables: int
    empresas_moderadas: int
    empresas_criticas: int

    promedio_general: float

    # --------------------------------------------------------
    # PLAN DE MEJORAMIENTO SST
    # --------------------------------------------------------

    total_acciones: int

    acciones_pendientes: int

    acciones_en_proceso: int

    acciones_vencidas: int

    acciones_finalizadas: int

    cumplimiento_plan_mejoramiento: float

    # --------------------------------------------------------
    # DETALLE
    # --------------------------------------------------------

    ranking: list[DashboardEmpresaSST]

    alertas: list[str]
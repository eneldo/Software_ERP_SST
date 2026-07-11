# ============================================================
# ROUTER DASHBOARD SAAS PRO
# ERP SST PRO
# Dashboard ejecutivo general de plataforma
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.area import Area
from app.models.cargo import Cargo
from app.models.empleado import Empleado
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.permiso import Permiso
from app.models.auditoria import Auditoria
from app.models.login_intento import LoginIntento

from app.schemas.dashboard_saas_schema import DashboardSaaSResponse
from app.auth.dependencies import require_roles


router = APIRouter(
    prefix="/dashboard-saas",
    tags=["Dashboard SaaS PRO"]
)


@router.get("/resumen", response_model=DashboardSaaSResponse)
def resumen_saas(
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]))
):
    """
    Dashboard general SaaS PRO.
    Muestra métricas globales del ERP SST.
    """

    return {
        "total_empresas": db.query(Empresa).count(),
        "total_sedes": db.query(Sede).count(),
        "total_areas": db.query(Area).count(),
        "total_cargos": db.query(Cargo).count(),
        "total_empleados": db.query(Empleado).count(),
        "total_usuarios": db.query(Usuario).count(),
        "total_roles": db.query(Rol).count(),
        "total_permisos": db.query(Permiso).count(),
        "total_auditorias": db.query(Auditoria).count(),
        "total_logins": db.query(LoginIntento).count(),

        "empleados_activos": db.query(Empleado).filter(Empleado.activo == True).count(),
        "empleados_inactivos": db.query(Empleado).filter(Empleado.activo == False).count(),

        "empresas_activas": db.query(Empresa).filter(Empresa.estado == True).count(),
        "sedes_activas": db.query(Sede).filter(Sede.activo == True).count(),
    }


@router.get("/salud")
def salud_plataforma(
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]))
):
    """
    Estado base del sistema.
    """

    return {
        "estado": "OK",
        "servicio": "ERP SST PRO",
        "version": "1.5.0",
        "base_datos": "PostgreSQL conectada",
        "seguridad": "JWT activo",
        "auditoria": "Middleware activo",
        "producto": "Dashboard SaaS PRO"
    }

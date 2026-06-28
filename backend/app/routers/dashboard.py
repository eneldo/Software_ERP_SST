from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.area import Area
from app.models.cargo import Cargo
from app.models.empleado import Empleado
from app.models.usuario import Usuario
from app.schemas.dashboard_schema import DashboardAdminResponse
from app.auth.dependencies import require_roles


router = APIRouter(prefix="/dashboard", tags=["Dashboard Administrativo PRO"])


@router.get("/admin", response_model=DashboardAdminResponse)
def dashboard_admin(
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]))
):
    return {
        "total_empresas": db.query(Empresa).count(),
        "total_sedes": db.query(Sede).count(),
        "total_areas": db.query(Area).count(),
        "total_cargos": db.query(Cargo).count(),
        "total_empleados": db.query(Empleado).count(),
        "total_usuarios": db.query(Usuario).count(),
    }
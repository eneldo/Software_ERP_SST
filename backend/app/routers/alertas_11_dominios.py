# ============================================================
# ROUTER ALERTAS 11 DOMINIOS
# H-020: Consolidador de alertas para todos los módulos SST
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_roles
from app.models.usuario import Usuario

from app.services.alertas_11_dominios_service import (
    generar_alertas_consolidadas,
    resumen_alertas_11_dominios,
)


router = APIRouter(
    prefix="/alertas-11-dominios",
    tags=["H-020: Alertas 11 Dominios"],
)

ROLES_SST = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "COORDINADOR_SST", "AUDITOR_INT"]


@router.post("/generar/{empresa_id}")
def generar_alertas(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles(ROLES_SST)),
):
    resultado = generar_alertas_consolidadas(db, empresa_id)
    return {
        "ok": True,
        "total_nuevas": resultado["total_nuevas"],
        "dominios": resultado["dominios"],
    }


@router.get("/resumen/{empresa_id}")
def resumen_alertas(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles(ROLES_SST)),
):
    return resumen_alertas_11_dominios(db, empresa_id)

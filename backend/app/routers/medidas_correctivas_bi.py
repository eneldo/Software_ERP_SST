# ============================================================
# ROUTER DASHBOARD BI MEDIDAS CORRECTIVAS
# ERP SST PRO
# FASE 1.1.8.7.5.4 — Dashboard Ejecutivo BI
# Archivo: backend/app/routers/medidas_correctivas_bi.py
# ============================================================

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database import get_db
from app.schemas.medidas_correctivas_bi_schema import MedidasCorrectivasBIResponse
from app.services.medidas_correctivas_bi_service import construir_bi_medidas_correctivas


router = APIRouter(
    prefix="/medidas-correctivas-bi",
    tags=["Medidas Correctivas BI Executive"],
)

ROLES_SST = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"]


def _validar_empresa_usuario(usuario, empresa_id: int | None):
    if not empresa_id:
        return
    if getattr(usuario, "rol", None) == "SUPER_ADMIN":
        return
    usuario_empresa_id = getattr(usuario, "empresa_id", None)
    if usuario_empresa_id and int(usuario_empresa_id) == int(empresa_id):
        return
    raise HTTPException(status_code=403, detail="No tiene permisos sobre esta empresa")


@router.get("/dashboard", response_model=MedidasCorrectivasBIResponse)
def dashboard_bi_medidas_correctivas(
    empresa_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    _validar_empresa_usuario(usuario, empresa_id)
    return construir_bi_medidas_correctivas(db=db, empresa_id=empresa_id)

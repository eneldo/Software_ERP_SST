# ============================================================
# ROUTER EVIDENCIAS INTELIGENTES + TRAZABILIDAD VISUAL
# ERP SST PRO
# FASE 1.1.8.7.5
# Archivo: backend/app/routers/medidas_evidencias_inteligentes.py
# ============================================================

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database import get_db
from app.models.capa import CapaSST
from app.schemas.medidas_evidencias_inteligentes_schema import EvidenciasInteligentesResponse
from app.services.medidas_evidencias_service import construir_paquete_inteligente


router = APIRouter(
    prefix="/medidas-correctivas-inteligentes",
    tags=["Medidas Correctivas Evidencias Inteligentes"],
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


@router.get("/{medida_id}", response_model=EvidenciasInteligentesResponse)
def obtener_evidencias_inteligentes_medida(
    medida_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    medida = db.query(CapaSST).filter(CapaSST.id == medida_id, CapaSST.activo.is_(True)).first()

    if not medida:
        raise HTTPException(status_code=404, detail="Medida correctiva no encontrada")

    _validar_empresa_usuario(usuario, medida.empresa_id)

    return construir_paquete_inteligente(db, medida)

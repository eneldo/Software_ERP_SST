# ============================================================
# ROUTER
# PLAN DE MEJORAMIENTO SST - EVIDENCIAS
# FASE 1.5.7
# ERP SST PRO
# ============================================================

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles

from app.schemas.plan_mejoramiento_evidencia_schema import (
    PlanMejoramientoEvidenciaResponse,
)

from app.services.plan_mejoramiento_evidencia_service import (
    subir_evidencia_plan,
    listar_evidencias_plan,
    obtener_evidencia,
    eliminar_evidencia,
)


router = APIRouter(
    prefix="/planear/plan-mejoramiento-evidencias",
    tags=["PLANEAR - Evidencias Plan Mejoramiento SST"],
)


ROLES_LECTURA = [
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "RESPONSABLE_SST",
    "AUDITOR",
]

ROLES_ESCRITURA = [
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "RESPONSABLE_SST",
]


# ============================================================
# SUBIR EVIDENCIA A UNA ACCIÓN DE MEJORAMIENTO
# ============================================================

@router.post(
    "/{plan_id}/upload",
    response_model=PlanMejoramientoEvidenciaResponse,
)
def subir_evidencia_accion_correctiva(
    plan_id: int,
    descripcion: str | None = Form(None),
    tipo_evidencia: str = Form("CIERRE"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    return subir_evidencia_plan(
        db=db,
        plan_id=plan_id,
        usuario_id=usuario.id,
        file=file,
        descripcion=descripcion,
        tipo_evidencia=tipo_evidencia,
    )


# ============================================================
# LISTAR EVIDENCIAS POR ACCIÓN
# ============================================================

@router.get(
    "/{plan_id}",
    response_model=list[PlanMejoramientoEvidenciaResponse],
)
def listar_evidencias_accion(
    plan_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    return listar_evidencias_plan(
        db=db,
        plan_id=plan_id,
    )


# ============================================================
# OBTENER DETALLE DE UNA EVIDENCIA
# IMPORTANTE: esta ruta debe ir antes de DELETE /{evidencia_id}
# ============================================================

@router.get(
    "/detalle/{evidencia_id}",
    response_model=PlanMejoramientoEvidenciaResponse,
)
def obtener_detalle_evidencia(
    evidencia_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    return obtener_evidencia(
        db=db,
        evidencia_id=evidencia_id,
    )


# ============================================================
# ELIMINAR EVIDENCIA
# ============================================================

@router.delete("/{evidencia_id}")
def eliminar_evidencia_accion(
    evidencia_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    return eliminar_evidencia(
        db=db,
        evidencia_id=evidencia_id,
    )
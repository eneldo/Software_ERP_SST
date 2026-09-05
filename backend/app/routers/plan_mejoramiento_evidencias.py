# ============================================================
# ROUTER EVIDENCIAS PLAN MEJORAMIENTO
# H-019: Fix tenant validation
# ============================================================

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.usuario import Usuario
from app.models.plan_mejoramiento import PlanMejoramientoSST

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
    "COORDINADOR_SST",
    "AUDITOR_INT",
]

ROLES_ESCRITURA = [
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "RESPONSABLE_SST",
    "COORDINADOR_SST",
]


def _empresa_id_autorizada(usuario: Usuario) -> int | None:
    if usuario.rol == "SUPER_ADMIN":
        return None
    if not usuario.empresa_id:
        raise HTTPException(status_code=403, detail="Usuario sin empresa asignada")
    return usuario.empresa_id


def _verificar_plan_pertenece_empresa(
    db: Session, plan_id: int, empresa_id: int | None
) -> PlanMejoramientoSST:
    plan = db.query(PlanMejoramientoSST).filter(PlanMejoramientoSST.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    if empresa_id and plan.empresa_id != empresa_id:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    return plan


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
    empresa_id = _empresa_id_autorizada(usuario)
    _verificar_plan_pertenece_empresa(db, plan_id, empresa_id)

    return subir_evidencia_plan(
        db=db,
        plan_id=plan_id,
        usuario_id=usuario.id,
        file=file,
        descripcion=descripcion,
        tipo_evidencia=tipo_evidencia,
    )


@router.get(
    "/{plan_id}",
    response_model=list[PlanMejoramientoEvidenciaResponse],
)
def listar_evidencias_accion(
    plan_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    empresa_id = _empresa_id_autorizada(usuario)
    _verificar_plan_pertenece_empresa(db, plan_id, empresa_id)

    return listar_evidencias_plan(
        db=db,
        plan_id=plan_id,
    )


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

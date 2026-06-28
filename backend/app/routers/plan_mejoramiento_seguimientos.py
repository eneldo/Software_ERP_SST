from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_roles

from app.schemas.plan_mejoramiento_seguimiento_schema import (
    PlanMejoramientoSeguimientoCreate,
    PlanMejoramientoSeguimientoResponse,
)

from app.services.plan_mejoramiento_seguimiento_service import (
    crear_seguimiento_plan,
    listar_seguimientos_plan,
    obtener_seguimiento_o_404,
    eliminar_seguimiento,
)


router = APIRouter(
    prefix="/planear/plan-mejoramiento-seguimientos",
    tags=["PLANEAR - Seguimientos Plan Mejoramiento SST"],
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


@router.post(
    "/{plan_id}",
    response_model=PlanMejoramientoSeguimientoResponse,
)
def crear_seguimiento(
    plan_id: int,
    data: PlanMejoramientoSeguimientoCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    return crear_seguimiento_plan(
        db=db,
        plan_id=plan_id,
        usuario_id=usuario.id,
        data=data,
    )


@router.get(
    "/{plan_id}",
    response_model=list[PlanMejoramientoSeguimientoResponse],
)
def listar_seguimientos(
    plan_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    return listar_seguimientos_plan(
        db=db,
        plan_id=plan_id,
    )


@router.get(
    "/detalle/{seguimiento_id}",
    response_model=PlanMejoramientoSeguimientoResponse,
)
def obtener_detalle_seguimiento(
    seguimiento_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    return obtener_seguimiento_o_404(
        db=db,
        seguimiento_id=seguimiento_id,
    )


@router.delete("/{seguimiento_id}")
def eliminar_seguimiento_plan(
    seguimiento_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    return eliminar_seguimiento(
        db=db,
        seguimiento_id=seguimiento_id,
    )
# ============================================================
# ROUTER
# PLAN DE MEJORAMIENTO SST INTELIGENTE
# FASE 1.5.3
# ERP SST PRO
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles

from app.models.empresa import Empresa
from app.models.plan_mejoramiento import PlanMejoramientoSST

from app.schemas.plan_mejoramiento_schema import (
    PlanMejoramientoCreate,
    PlanMejoramientoUpdate,
    PlanMejoramientoResponse,
    PlanMejoramientoDashboard,
    GenerarPlanDesdeEvaluacionRequest,
    CambioEstadoPlan,
    CambioAvancePlan,
    CerrarPlanRequest,
)

from app.services.plan_mejoramiento_service import (
    crear_plan_manual,
    listar_planes,
    obtener_plan_o_404,
    actualizar_plan,
    cerrar_plan,
    cambiar_estado_plan,
    cambiar_avance_plan,
    eliminar_plan_logico,
    generar_desde_evaluacion,
    dashboard_plan_mejoramiento,
    serializar_plan,
)


router = APIRouter(
    prefix="/planear/plan-mejoramiento",
    tags=["PLANEAR - Plan de Mejoramiento SST"],
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
# VALIDACIONES
# ============================================================

def validar_empresa(db: Session, empresa_id: int):
    empresa = (
        db.query(Empresa)
        .filter(
            Empresa.id == empresa_id,
            Empresa.estado == True,
        )
        .first()
    )

    if not empresa:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada o inactiva",
        )

    return empresa


# ============================================================
# CREAR ACCIÓN MANUAL
# ============================================================

@router.post("/", response_model=PlanMejoramientoResponse)
def crear_accion_mejoramiento(
    data: PlanMejoramientoCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    validar_empresa(db, data.empresa_id)

    plan = crear_plan_manual(
        db=db,
        data=data,
        usuario_id=usuario.id,
    )

    return serializar_plan(plan)


# ============================================================
# LISTAR ACCIONES
# ============================================================

@router.get("/", response_model=list[PlanMejoramientoResponse])
def listar_acciones_mejoramiento(
    empresa_id: int | None = Query(default=None),
    estado: str | None = Query(default=None),
    prioridad: str | None = Query(default=None),
    responsable: str | None = Query(default=None),
    buscar: str | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    planes = listar_planes(
        db=db,
        empresa_id=empresa_id,
        estado=estado,
        prioridad=prioridad,
        responsable=responsable,
        buscar=buscar,
    )

    return [serializar_plan(plan) for plan in planes]


# ============================================================
# DASHBOARD PLAN DE MEJORAMIENTO
# IMPORTANTE: debe ir antes de /{plan_id}
# ============================================================

@router.get("/dashboard", response_model=PlanMejoramientoDashboard)
def dashboard_plan(
    empresa_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    return dashboard_plan_mejoramiento(
        db=db,
        empresa_id=empresa_id,
    )


# ============================================================
# GENERAR PLAN AUTOMÁTICO DESDE EVALUACIÓN INICIAL
# ============================================================

@router.post("/generar-desde-evaluacion")
def generar_plan_automatico_desde_evaluacion(
    data: GenerarPlanDesdeEvaluacionRequest,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    return generar_desde_evaluacion(
        db=db,
        evaluacion_id=data.evaluacion_id,
        usuario_id=usuario.id,
    )


# ============================================================
# OBTENER ACCIÓN
# ============================================================

@router.get("/{plan_id}", response_model=PlanMejoramientoResponse)
def obtener_accion_mejoramiento(
    plan_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    plan = obtener_plan_o_404(
        db=db,
        plan_id=plan_id,
    )

    return serializar_plan(plan)


# ============================================================
# ACTUALIZAR ACCIÓN
# ============================================================

@router.put("/{plan_id}", response_model=PlanMejoramientoResponse)
def actualizar_accion_mejoramiento(
    plan_id: int,
    data: PlanMejoramientoUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    plan = actualizar_plan(
        db=db,
        plan_id=plan_id,
        data=data,
    )

    return serializar_plan(plan)


# ============================================================
# CAMBIAR ESTADO
# ============================================================

@router.patch("/{plan_id}/estado", response_model=PlanMejoramientoResponse)
def cambiar_estado_accion(
    plan_id: int,
    data: CambioEstadoPlan,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    plan = cambiar_estado_plan(
        db=db,
        plan_id=plan_id,
        estado=data.estado,
    )

    return serializar_plan(plan)


# ============================================================
# CAMBIAR AVANCE
# ============================================================

@router.patch("/{plan_id}/avance", response_model=PlanMejoramientoResponse)
def cambiar_avance_accion(
    plan_id: int,
    data: CambioAvancePlan,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    plan = cambiar_avance_plan(
        db=db,
        plan_id=plan_id,
        porcentaje_avance=data.porcentaje_avance,
    )

    return serializar_plan(plan)


# ============================================================
# FINALIZAR / CERRAR ACCIÓN
# ============================================================

@router.patch("/{plan_id}/cerrar", response_model=PlanMejoramientoResponse)
def cerrar_accion_mejoramiento(
    plan_id: int,
    data: CerrarPlanRequest,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    plan = cerrar_plan(
        db=db,
        plan_id=plan_id,
        observaciones=data.observaciones,
    )

    return serializar_plan(plan)


# ============================================================
# ELIMINAR LÓGICO
# ============================================================

@router.delete("/{plan_id}")
def eliminar_accion_mejoramiento(
    plan_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    return eliminar_plan_logico(
        db=db,
        plan_id=plan_id,
    )
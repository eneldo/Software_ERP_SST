# ============================================================
# ROUTER
# AUDITORÍA SST INTELIGENTE
# FASE 1.7
# ERP SST PRO
# ============================================================

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_roles

from app.schemas.auditoria_sst_schema import (
    AuditoriaCreate,
    AuditoriaUpdate,
    AuditoriaResponse,
    AuditoriaDashboard,
    AuditoriaHallazgoCreate,
    AuditoriaHallazgoUpdate,
    AuditoriaHallazgoResponse,
)

from app.services.auditoria_sst_service import (
    crear_auditoria,
    listar_auditorias,
    obtener_auditoria_o_404,
    actualizar_auditoria,
    eliminar_auditoria,
    crear_hallazgo,
    actualizar_hallazgo,
    eliminar_hallazgo,
    generar_plan_desde_hallazgo,
    dashboard_auditorias,
)


router = APIRouter(
    prefix="/verificar/auditorias-sst",
    tags=["VERIFICAR - Auditorías SST Inteligentes"],
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
    "AUDITOR",
]


@router.get("/dashboard", response_model=AuditoriaDashboard)
def dashboard(
    empresa_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    return dashboard_auditorias(db=db, empresa_id=empresa_id)


@router.post("/", response_model=AuditoriaResponse)
def crear(
    data: AuditoriaCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    return crear_auditoria(db=db, data=data, usuario_id=usuario.id)


@router.get("/", response_model=list[AuditoriaResponse])
def listar(
    empresa_id: int | None = Query(default=None),
    estado: str | None = Query(default=None),
    buscar: str | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    return listar_auditorias(
        db=db,
        empresa_id=empresa_id,
        estado=estado,
        buscar=buscar,
    )


@router.get("/{auditoria_id}", response_model=AuditoriaResponse)
def obtener(
    auditoria_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    return obtener_auditoria_o_404(db=db, auditoria_id=auditoria_id)


@router.put("/{auditoria_id}", response_model=AuditoriaResponse)
def actualizar(
    auditoria_id: int,
    data: AuditoriaUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    return actualizar_auditoria(db=db, auditoria_id=auditoria_id, data=data)


@router.delete("/{auditoria_id}")
def eliminar(
    auditoria_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    return eliminar_auditoria(db=db, auditoria_id=auditoria_id)


@router.post("/{auditoria_id}/hallazgos", response_model=AuditoriaHallazgoResponse)
def crear_hallazgo_auditoria(
    auditoria_id: int,
    data: AuditoriaHallazgoCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    return crear_hallazgo(
        db=db,
        auditoria_id=auditoria_id,
        data=data,
        usuario_id=usuario.id,
    )


@router.put("/hallazgos/{hallazgo_id}", response_model=AuditoriaHallazgoResponse)
def actualizar_hallazgo_auditoria(
    hallazgo_id: int,
    data: AuditoriaHallazgoUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    return actualizar_hallazgo(db=db, hallazgo_id=hallazgo_id, data=data)


@router.delete("/hallazgos/{hallazgo_id}")
def eliminar_hallazgo_auditoria(
    hallazgo_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    return eliminar_hallazgo(db=db, hallazgo_id=hallazgo_id)


@router.post("/hallazgos/{hallazgo_id}/generar-plan")
def generar_plan_hallazgo(
    hallazgo_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    return generar_plan_desde_hallazgo(
        db=db,
        hallazgo_id=hallazgo_id,
        usuario_id=usuario.id,
    )
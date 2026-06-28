# ============================================================
# ERP SST PRO ENTERPRISE
# MÓDULO: VERSIONADO DOCUMENTAL
# ARCHIVO: backend/app/routers/revision_version.py
#
# USO:
# Router para consultar, crear, comparar y restaurar versiones
# documentales de Revisión por la Dirección SST.
#
# Endpoints:
# - GET  /verificar/revision-direccion/{revision_id}/versiones
# - GET  /verificar/revision-direccion/versiones/{version_id}
# - POST /verificar/revision-direccion/{revision_id}/versiones/snapshot
# - POST /verificar/revision-direccion/versiones/{version_id}/restaurar
# - GET  /verificar/revision-direccion/versiones/comparar
#
# FASE 1.8.4.3 — VERSIONADO DOCUMENTAL ENTERPRISE PRO
# ============================================================

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.auth.dependencies import require_roles
from app.models.revision_direccion import RevisionDireccionSST
from app.schemas.revision_version import (
    RevisionVersionResponse,
    RevisionVersionDetalleResponse,
    RestaurarVersionRequest,
    ComparacionVersionResponse,
)
from app.services.revision_version_service import (
    crear_snapshot_revision,
    listar_versiones_revision,
    obtener_version_o_404,
    comparar_versiones,
    restaurar_version_revision,
)


router = APIRouter(
    prefix="/verificar/revision-direccion",
    tags=["Revisión Dirección Versionado"],
)


ROLES_PERMITIDOS = [
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "RESPONSABLE_SST",
    "AUDITOR",
]


def obtener_usuario_id(usuario):
    return getattr(usuario, "id", None)


@router.get(
    "/{revision_id}/versiones",
    response_model=list[RevisionVersionResponse],
)
def listar_versiones(
    revision_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PERMITIDOS)),
):
    return listar_versiones_revision(
        db=db,
        revision_id=revision_id,
    )


@router.get(
    "/versiones/{version_id}",
    response_model=RevisionVersionDetalleResponse,
)
def obtener_version(
    version_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PERMITIDOS)),
):
    return obtener_version_o_404(
        db=db,
        version_id=version_id,
    )


@router.post(
    "/{revision_id}/versiones/snapshot",
    response_model=RevisionVersionResponse,
)
def crear_snapshot_manual(
    revision_id: int,
    observacion: str | None = "Snapshot manual",
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PERMITIDOS)),
):
    revision = (
        db.query(RevisionDireccionSST)
        .options(joinedload(RevisionDireccionSST.compromisos))
        .filter(
            RevisionDireccionSST.id == revision_id,
            RevisionDireccionSST.activo == True,
        )
        .first()
    )

    if not revision:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Revisión por la Dirección no encontrada.",
        )

    return crear_snapshot_revision(
        db=db,
        revision=revision,
        usuario_id=obtener_usuario_id(usuario),
        accion="SNAPSHOT_MANUAL",
        observacion=observacion,
    )


@router.post(
    "/versiones/{version_id}/restaurar",
    response_model=RevisionVersionResponse,
)
def restaurar_version(
    version_id: int,
    data: RestaurarVersionRequest,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PERMITIDOS)),
):
    return restaurar_version_revision(
        db=db,
        version_id=version_id,
        usuario_id=obtener_usuario_id(usuario),
        observacion=data.observacion,
    )


@router.get(
    "/versiones/comparar",
    response_model=ComparacionVersionResponse,
)
def comparar_dos_versiones(
    version_origen_id: int = Query(...),
    version_destino_id: int = Query(...),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PERMITIDOS)),
):
    return comparar_versiones(
        db=db,
        version_origen_id=version_origen_id,
        version_destino_id=version_destino_id,
    )
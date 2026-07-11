# ============================================================
# ROUTER RELATION GUARD - ERP SST PRO ENTERPRISE
# FASE 37.1.1 — Motor Global de Validación de Relaciones
# Archivo: backend/app/routers/relation_guard.py
# ============================================================

from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles, require_permission
from app.core.default_permissions import PERM_REGISTROS_ELIMINAR
from app.database import get_db
from app.schemas.relation_guard_schema import (
    RelationGuardEntityResponse,
    IntegrityFrameworkMetadataResponse,
    RelationGuardResponse,
    SmartDeleteResponse,
)
from app.services.relation_guard import (
    get_registered_entities,
    execute_smart_delete,
    validate_delete_dependencies,
    get_integrity_framework_metadata,
)


router = APIRouter(
    prefix="/integridad",
    tags=["Integridad y Eliminación Inteligente"],
)
ELIMINAR_REGISTROS = require_permission(PERM_REGISTROS_ELIMINAR)


@router.get(
    "/framework/metadata",
    response_model=IntegrityFrameworkMetadataResponse,
    summary="Metadata Enterprise del Framework de Integridad",
)
def obtener_metadata_framework_integridad(
    usuario=Depends(
        require_roles(
            [
                "SUPER_ADMIN",
                "ADMIN_EMPRESA",
                "RESPONSABLE_SST",
                "COORDINADOR_SST",
            ]
        )
    ),
):
    # FASE 37.4 — Enterprise Core Framework
    # Expone metadatos centralizados: entidades, colores, iconos, severidad
    # y políticas preparadas para Papelera/Restauración futura.
    return get_integrity_framework_metadata()


@router.get(
    "/framework/metadata/{entidad}",
    summary="Metadata Enterprise de una entidad protegida",
)
def obtener_metadata_entidad_integridad(
    entidad: str = Path(..., description="Entidad registrada en el Framework"),
    usuario=Depends(
        require_roles(
            [
                "SUPER_ADMIN",
                "ADMIN_EMPRESA",
                "RESPONSABLE_SST",
                "COORDINADOR_SST",
            ]
        )
    ),
):
    metadata = get_integrity_framework_metadata()
    for item in metadata.get("entities", []):
        if item.get("entity") == entidad:
            return item
    return {
        "entity": entidad,
        "found": False,
        "message": f"La entidad '{entidad}' no está registrada en la metadata del Framework.",
        "registered_entities": [item.get("entity") for item in metadata.get("entities", [])],
    }


@router.get(
    "/entidades",
    response_model=list[RelationGuardEntityResponse],
    summary="Listar entidades protegidas por el motor",
)
def listar_entidades_protegidas(
    usuario=Depends(
        require_roles(
            [
                "SUPER_ADMIN",
                "ADMIN_EMPRESA",
                "RESPONSABLE_SST",
                "COORDINADOR_SST",
            ]
        )
    ),
):
    return get_registered_entities()


@router.get(
    "/eliminacion/{entidad}/{registro_id}",
    response_model=RelationGuardResponse,
    summary="Validar si un registro puede eliminarse físicamente",
)
def validar_eliminacion(
    entidad: str = Path(..., description="Entidad: empresa, sede, area, cargo, empleado"),
    registro_id: int = Path(..., ge=1, description="ID del registro a validar"),
    db: Session = Depends(get_db),
    usuario=Depends(
        require_roles(
            [
                "SUPER_ADMIN",
                "ADMIN_EMPRESA",
                "RESPONSABLE_SST",
                "COORDINADOR_SST",
            ]
        )
    ),
):
    return validate_delete_dependencies(
        db,
        entity=entidad,
        record_id=registro_id,
    )



@router.delete(
    "/eliminacion/{entidad}/{registro_id}",
    response_model=SmartDeleteResponse,
    summary="Ejecutar eliminación inteligente de un registro",
)
def ejecutar_eliminacion_inteligente(
    entidad: str = Path(..., description="Entidad: empresa, sede, area, cargo, empleado"),
    registro_id: int = Path(..., ge=1, description="ID del registro a eliminar o inactivar"),
    modo: str = Query(
        default="AUTO",
        description="AUTO elimina si no hay dependencias; si hay dependencias inactiva. Valores: AUTO, DELETE, INACTIVATE",
    ),
    confirmar: bool = Query(
        default=False,
        description="Debe enviarse true para ejecutar la acción. Si es false, solo solicita confirmación.",
    ),
    db: Session = Depends(get_db),
    usuario=Depends(ELIMINAR_REGISTROS),
):
    return execute_smart_delete(
        db,
        entity=entidad,
        record_id=registro_id,
        mode=modo,
        confirmed=confirmar,
    )

# ============================================================
# USO DEL ARCHIVO:
# Router encargado de exponer el endpoint para exportar el PDF
# Enterprise de Revisión por la Dirección SST.
#
# Endpoint:
# GET /verificar/revision-direccion-pdf/{revision_id}
#
# Ubicación:
# backend/app/routers/revision_direccion_pdf.py
#
# FASE 1.8.3.1 — PDF Ejecutivo Enterprise
# ============================================================

from io import BytesIO

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_roles
from app.core.roles import ROLES_LECTURA_EJECUTIVA
from app.services.revision_direccion_pdf_service import (
    generar_pdf_revision_direccion,
)
from app.routers.revision_direccion import obtener_revision_o_404


router = APIRouter(
    prefix="/verificar/revision-direccion-pdf",
    tags=["Revisión Dirección SST PDF"],
)


ROLES_PERMITIDOS = list(ROLES_LECTURA_EJECUTIVA)


@router.get("/{revision_id}")
def exportar_pdf_revision_direccion(
    revision_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PERMITIDOS)),
):
    obtener_revision_o_404(db, revision_id, usuario)
    pdf = generar_pdf_revision_direccion(
        db=db,
        revision_id=revision_id,
    )

    return StreamingResponse(
        BytesIO(pdf),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="revision_direccion_enterprise_{revision_id}.pdf"'
            )
        },
    )

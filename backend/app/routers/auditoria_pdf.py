# ============================================================
# ROUTER PDF PROFESIONAL
# AUDITORÍA SST ENTERPRISE
# FASE 1.7.4.1
# Archivo: backend/app/routers/auditoria_pdf.py
# ============================================================

from io import BytesIO

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_roles
from app.services.auditoria_pdf_service import generar_pdf_auditoria


router = APIRouter(
    prefix="/verificar/auditorias-sst-pdf",
    tags=["Auditorías SST PDF"],
)


ROLES_LECTURA = [
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "RESPONSABLE_SST",
    "AUDITOR",
]


@router.get("/{auditoria_id}")
def exportar_pdf_auditoria_sst(
    auditoria_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    pdf = generar_pdf_auditoria(
        db=db,
        auditoria_id=auditoria_id,
    )

    filename = f"auditoria_sst_{auditoria_id}.pdf"

    return StreamingResponse(
        BytesIO(pdf),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )
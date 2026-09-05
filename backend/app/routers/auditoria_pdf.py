# ============================================================
# ROUTER PDF PROFESIONAL
# AUDITORÍA SST ENTERPRISE
# FASE 1.7.4.1
# Archivo: backend/app/routers/auditoria_pdf.py
# ============================================================

from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_roles
from app.models.auditoria_sst import AuditoriaSST
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


def _empresa_id_autorizada(usuario, empresa_id: int | None) -> int | None:
    if str(getattr(usuario, "rol", "") or "").upper() == "SUPER_ADMIN":
        return empresa_id
    usuario_empresa_id = getattr(usuario, "empresa_id", None)
    if usuario_empresa_id is None:
        raise HTTPException(status_code=403, detail="Usuario sin empresa asignada")
    if empresa_id is not None and int(usuario_empresa_id) != int(empresa_id):
        raise HTTPException(status_code=403, detail="No tiene permisos sobre esta empresa")
    return int(usuario_empresa_id)


@router.get("/{auditoria_id}")
def exportar_pdf_auditoria_sst(
    auditoria_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    tenant_id = _empresa_id_autorizada(usuario, None)
    filtros = [AuditoriaSST.id == auditoria_id]
    if tenant_id is not None:
        filtros.append(AuditoriaSST.empresa_id == tenant_id)
    auditoria = db.query(AuditoriaSST).filter(*filtros).first()
    if not auditoria:
        raise HTTPException(status_code=404, detail="Auditoría SST no encontrada")
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
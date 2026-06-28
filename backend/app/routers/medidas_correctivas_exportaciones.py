# ============================================================
# ROUTER EXPORTACIONES MEDIDAS CORRECTIVAS ENTERPRISE
# ERP SST PRO
# FASE 1.1.8.7.6 / 1.1.8.7.6.1
# Archivo: backend/app/routers/medidas_correctivas_exportaciones.py
# ============================================================

from __future__ import annotations

from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database import get_db
from app.models.capa import CapaSST
from app.services.medidas_correctivas_pdf_service import generar_pdf_medida_correctiva

# Excel individual opcional. Si aún no existe el service, el PDF no se rompe.
try:
    from app.services.medidas_correctivas_excel_service import generar_excel_medida_correctiva
except Exception:
    generar_excel_medida_correctiva = None


router = APIRouter(
    prefix="/medidas-correctivas-exportaciones",
    tags=["Medidas Correctivas Exportaciones Enterprise"],
)

ROLES_SST = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"]


def _validar_empresa_usuario(usuario, empresa_id: int | None):
    if not empresa_id:
        return

    if getattr(usuario, "rol", None) == "SUPER_ADMIN":
        return

    usuario_empresa_id = getattr(usuario, "empresa_id", None)

    if usuario_empresa_id and int(usuario_empresa_id) == int(empresa_id):
        return

    raise HTTPException(status_code=403, detail="No tiene permisos sobre esta empresa")


def _get_medida(db: Session, medida_id: int, usuario):
    medida = (
        db.query(CapaSST)
        .filter(CapaSST.id == medida_id, CapaSST.activo.is_(True))
        .first()
    )

    if not medida:
        raise HTTPException(status_code=404, detail="Medida correctiva no encontrada")

    _validar_empresa_usuario(usuario, medida.empresa_id)

    return medida


@router.get("/{medida_id}/pdf")
def exportar_pdf_medida_correctiva(
    medida_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    medida = _get_medida(db, medida_id, usuario)

    try:
        pdf_bytes = generar_pdf_medida_correctiva(db, medida_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"No fue posible generar el PDF: {str(exc)}",
        )

    filename = f"medida_correctiva_{medida.codigo or medida.id}.pdf".replace(" ", "_")

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{medida_id}/excel")
def exportar_excel_medida_correctiva(
    medida_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    if generar_excel_medida_correctiva is None:
        raise HTTPException(
            status_code=501,
            detail="El servicio de Excel individual no está instalado.",
        )

    medida = _get_medida(db, medida_id, usuario)

    try:
        excel_bytes = generar_excel_medida_correctiva(db, medida_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"No fue posible generar el Excel: {str(exc)}",
        )

    filename = f"medida_correctiva_{medida.codigo or medida.id}.xlsx".replace(" ", "_")

    return StreamingResponse(
        BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

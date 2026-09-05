# ============================================================
# ERP SST ENTERPRISE
# ------------------------------------------------------------
# Módulo      : Inspecciones SST
# Fase        : 1.1.8.7.9
# Archivo     : inspecciones_exportaciones_platinum.py
# Ubicación   : backend/app/routers/
# Versión     : Platinum Final v1.0
# ------------------------------------------------------------
# Descripción:
# Router de exportación PDF Ejecutivo Platinum para Inspecciones.
# ============================================================

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.auth.dependencies import require_permission
from app.core.default_permissions import PERM_REPORTES_EXPORTAR
from app.database import get_db
from app.models.inspeccion import InspeccionSST
from app.services.pdf.inspeccion_pdf_platinum import generar_reporte_inspeccion_platinum_pdf

logger = logging.getLogger("app.exportaciones.inspecciones_platinum")

# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/inspecciones-exportaciones-platinum",
    tags=["Inspecciones SST - PDF Platinum"],
)

ROLES_SST = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "COORDINADOR_SST", "AUDITOR"]
EXPORTAR_REPORTES = require_permission(PERM_REPORTES_EXPORTAR)


def _empresa_id_autorizada(usuario, empresa_id: int | None) -> int | None:
    if str(getattr(usuario, "rol", "") or "").upper() == "SUPER_ADMIN":
        return empresa_id
    usuario_empresa_id = getattr(usuario, "empresa_id", None)
    if usuario_empresa_id is None:
        raise HTTPException(status_code=403, detail="Usuario sin empresa asignada")
    if empresa_id is not None and int(usuario_empresa_id) != int(empresa_id):
        raise HTTPException(status_code=403, detail="No tiene permisos sobre esta empresa")
    return int(usuario_empresa_id)

# ============================================================
# ENDPOINT PDF PLATINUM
# ============================================================

@router.get("/{inspeccion_id}/pdf-platinum")
def exportar_inspeccion_pdf_platinum(
    inspeccion_id: int,
    usuario_reporte: str = Query(default="Sistema", alias="usuario", description="Usuario que genera el reporte"),
    base_url: Optional[str] = Query(default=None, description="URL opcional para QR de trazabilidad"),
    db: Session = Depends(get_db),
    usuario_actual=Depends(EXPORTAR_REPORTES),
):
    """
    Genera y descarga el Reporte PDF Ejecutivo Platinum Final.

    Ruta:
    GET /inspecciones-exportaciones-platinum/{inspeccion_id}/pdf-platinum
    """
    tenant_id = _empresa_id_autorizada(usuario_actual, None)
    filtros = [InspeccionSST.id == inspeccion_id]
    if tenant_id is not None:
        filtros.append(InspeccionSST.empresa_id == tenant_id)
    inspeccion = db.query(InspeccionSST).filter(*filtros).first()
    if not inspeccion:
        raise HTTPException(status_code=404, detail="Inspeccion no encontrada o no disponible para exportacion.")
    try:
        pdf_bytes = generar_reporte_inspeccion_platinum_pdf(
            db=db,
            inspeccion_id=inspeccion_id,
            usuario=usuario_reporte,
            base_url=base_url,
        )
        filename = f"inspeccion_sst_{inspeccion_id}_reporte_platinum.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Inspeccion no encontrada o no disponible para exportacion.")
    except Exception as exc:
        logger.exception("Error generando PDF Platinum inspeccion_id=%s", inspeccion_id)
        raise HTTPException(status_code=500, detail="No fue posible generar el PDF Platinum.") from exc

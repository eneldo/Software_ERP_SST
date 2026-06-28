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

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.pdf.inspeccion_pdf_platinum import generar_reporte_inspeccion_platinum_pdf

# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/inspecciones-exportaciones-platinum",
    tags=["Inspecciones SST - PDF Platinum"],
)

# ============================================================
# ENDPOINT PDF PLATINUM
# ============================================================

@router.get("/{inspeccion_id}/pdf-platinum")
def exportar_inspeccion_pdf_platinum(
    inspeccion_id: int,
    usuario: str = Query(default="Sistema", description="Usuario que genera el reporte"),
    base_url: Optional[str] = Query(default=None, description="URL opcional para QR de trazabilidad"),
    db: Session = Depends(get_db),
):
    """
    Genera y descarga el Reporte PDF Ejecutivo Platinum Final.

    Ruta:
    GET /inspecciones-exportaciones-platinum/{inspeccion_id}/pdf-platinum
    """
    try:
        pdf_bytes = generar_reporte_inspeccion_platinum_pdf(
            db=db,
            inspeccion_id=inspeccion_id,
            usuario=usuario,
            base_url=base_url,
        )
        filename = f"inspeccion_sst_{inspeccion_id}_reporte_platinum.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error generando PDF Platinum: {str(exc)}")

# ============================================================
# ROUTER
# VALIDACIÓN DOCUMENTAL SST ENTERPRISE PRO
# FASE 1.7.4.2.5.3
# ============================================================

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.empresa import Empresa
from app.services.documento_validacion_service import (
    obtener_documento_por_codigo,
    verificar_archivo_con_codigo,
)


router = APIRouter(
    prefix="/validar/documento",
    tags=["Validación Documental SST"],
)


@router.get("/{codigo_validacion}")
def validar_documento(
    codigo_validacion: str,
    db: Session = Depends(get_db),
):
    documento = obtener_documento_por_codigo(
        db=db,
        codigo_validacion=codigo_validacion,
    )

    empresa = None

    if documento.empresa_id:
        empresa = (
            db.query(Empresa)
            .filter(Empresa.id == documento.empresa_id)
            .first()
        )

    return {
        "codigo_validacion": documento.codigo_validacion,
        "tipo_documento": documento.tipo_documento,
        "referencia_id": documento.referencia_id,

        "empresa_id": documento.empresa_id,
        "empresa_nombre": empresa.nombre if empresa else None,
        "empresa_nit": empresa.nit if empresa else None,
        "empresa_logo": empresa.logo if empresa else None,

        "usuario_id": documento.usuario_id,
        "nombre_archivo": documento.nombre_archivo,
        "hash_sha256": documento.hash_sha256,
        "url_archivo": documento.url_archivo,

        "estado": documento.estado,
        "observacion": documento.observacion,

        "fecha_generacion": documento.fecha_generacion,
        "fecha_anulacion": documento.fecha_anulacion,
    }


@router.post("/{codigo_validacion}/verificar-archivo")
async def verificar_archivo_documento(
    codigo_validacion: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    contenido = await file.read()

    return verificar_archivo_con_codigo(
        db=db,
        codigo_validacion=codigo_validacion,
        contenido_archivo=contenido,
    )
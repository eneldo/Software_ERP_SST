from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Path as ApiPath, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, user_has_permission
from app.config import settings
from app.core.default_permissions import PERM_EXAMENES_DESCARGAR
from app.database import get_db
from app.models.documento_validacion import DocumentoValidacionSST


router = APIRouter(tags=["Archivos protegidos"])


def _resolve_upload_path(relative_path: str) -> Path:
    cleaned = str(relative_path or "").strip().replace("\\", "/").lstrip("/")
    if not cleaned or cleaned.startswith("../") or "/../" in cleaned or cleaned == "..":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ruta de archivo invalida")

    upload_root = Path(settings.UPLOAD_DIR).resolve()
    file_path = (upload_root / cleaned).resolve()

    if upload_root != file_path and upload_root not in file_path.parents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ruta de archivo invalida")

    if not file_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado")

    return file_path


def _file_response(file_path: Path) -> FileResponse:
    headers = {
        "Cache-Control": "private, no-store",
        "Content-Disposition": f"inline; filename*=UTF-8''{quote(file_path.name)}",
    }
    return FileResponse(path=str(file_path), filename=file_path.name, headers=headers)


@router.get("/archivos-protegidos/{relative_path:path}")
def servir_archivo_protegido(
    relative_path: str = ApiPath(..., description="Ruta relativa dentro de UPLOAD_DIR"),
    usuario=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cleaned = str(relative_path or "").strip().replace("\\", "/").lstrip("/")
    if cleaned.lower().startswith("examenes-medicos/") and not user_has_permission(db, usuario, PERM_EXAMENES_DESCARGAR):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permisos para descargar examenes medicos")

    return _file_response(_resolve_upload_path(relative_path))


@router.get("/validar/documento/{codigo_validacion}/archivo")
def servir_archivo_validacion_publico(
    codigo_validacion: str,
    db: Session = Depends(get_db),
):
    documento = (
        db.query(DocumentoValidacionSST)
        .filter(DocumentoValidacionSST.codigo_validacion == codigo_validacion)
        .first()
    )

    if not documento or documento.estado != "VALIDO" or not documento.url_archivo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo publico no disponible")

    relative_path = str(documento.url_archivo).replace("\\", "/")
    if "/uploads/" in relative_path:
        relative_path = relative_path.split("/uploads/", 1)[1]
    relative_path = relative_path.lstrip("/")

    return _file_response(_resolve_upload_path(relative_path))


@router.get("/logos-empresa/{relative_path:path}")
def servir_logo_empresa_publico(
    relative_path: str = ApiPath(..., description="Nombre del archivo de logo dentro de uploads/logos/"),
):
    cleaned = str(relative_path or "").strip().replace("\\", "/").lstrip("/")
    if not cleaned or cleaned.startswith("../") or "/../" in cleaned:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ruta invalida")
    return _file_response(_resolve_upload_path(f"logos/{cleaned}"))

# ============================================================
# ROUTER: Versiones Documentales
# Archivo: backend/app/routers/documentos_versiones.py
# FASE 1.8.4.3.9 - Centro de Control Documental SST Enterprise
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles, require_permission
from app.core.default_permissions import PERM_REGISTROS_ELIMINAR
from app.database import get_db
from app.models.biblioteca_documental import BibliotecaDocumental
from app.models.documento_version import DocumentoVersion
from app.schemas.documento_version_schema import (
    DocumentoVersionCreate,
    DocumentoVersionResponse,
)

router = APIRouter(
    prefix="/documentos-versiones",
    tags=["Versiones Documentales"],
)
ELIMINAR_REGISTROS = require_permission(PERM_REGISTROS_ELIMINAR)


@router.get("/{documento_id}", response_model=list[DocumentoVersionResponse])
def obtener_historial(
    documento_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"])),
):
    documento = db.query(BibliotecaDocumental).filter(BibliotecaDocumental.id == documento_id).first()

    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    return (
        db.query(DocumentoVersion)
        .filter(DocumentoVersion.documento_id == documento_id)
        .order_by(DocumentoVersion.fecha_creacion.desc())
        .all()
    )


@router.post("/", response_model=DocumentoVersionResponse)
def crear_version_documental(
    data: DocumentoVersionCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    documento = db.query(BibliotecaDocumental).filter(BibliotecaDocumental.id == data.documento_id).first()

    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    nueva_version = DocumentoVersion(**data.model_dump())

    if not nueva_version.usuario:
        nueva_version.usuario = getattr(usuario, "correo", None) or getattr(usuario, "nombres", None) or "Sistema"

    db.add(nueva_version)

    # Sincroniza la versión visible en la Biblioteca Documental.
    documento.version = data.version

    db.commit()
    db.refresh(nueva_version)

    return nueva_version


@router.delete("/{version_id}")
def eliminar_version_documental(
    version_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(ELIMINAR_REGISTROS),
):
    version = db.query(DocumentoVersion).filter(DocumentoVersion.id == version_id).first()

    if not version:
        raise HTTPException(status_code=404, detail="Versión documental no encontrada")

    db.delete(version)
    db.commit()

    return {"mensaje": "Versión documental eliminada correctamente"}

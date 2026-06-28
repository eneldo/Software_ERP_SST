# ============================================================
# ROUTER
# FIRMA ELECTRÓNICA SST ENTERPRISE
# FASE 1.7.4.2.4
# ============================================================

from pathlib import Path
from uuid import uuid4
import os
import shutil

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_roles
from app.models.usuario import Usuario
from app.models.firma_digital import FirmaDigitalSST
from app.schemas.firma_digital_schema import FirmaDigitalResponse


router = APIRouter(
    prefix="/configuracion/firmas-digitales",
    tags=["Firmas Digitales SST"],
)


ROLES_PERMITIDOS = [
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "RESPONSABLE_SST",
    "AUDITOR",
]


BASE_DIR = Path(__file__).resolve().parents[1]  # backend/app
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads"))
FIRMAS_DIR = UPLOAD_DIR / "firmas"
FIRMAS_DIR.mkdir(parents=True, exist_ok=True)


def obtener_usuario_o_404(db: Session, usuario_id: int):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado",
        )

    return usuario


@router.post(
    "/usuario/{usuario_id}/upload",
    response_model=FirmaDigitalResponse,
)
def subir_firma_usuario(
    usuario_id: int,
    nombre_firmante: str = Form(...),
    cargo: str = Form(default=""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(ROLES_PERMITIDOS)),
):
    usuario = obtener_usuario_o_404(db, usuario_id)

    extension = Path(file.filename or "").suffix.lower()

    if extension not in [".png", ".jpg", ".jpeg", ".webp"]:
        raise HTTPException(
            status_code=400,
            detail="Formato no permitido. Use PNG, JPG, JPEG o WEBP.",
        )

    nombre_archivo = f"firma_usuario_{usuario.id}_{uuid4().hex}{extension}"
    ruta_fisica = FIRMAS_DIR / nombre_archivo

    with ruta_fisica.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    tamano_bytes = ruta_fisica.stat().st_size
    url = f"/uploads/firmas/{nombre_archivo}"

    # Desactivar firmas anteriores del usuario
    firmas_anteriores = (
        db.query(FirmaDigitalSST)
        .filter(
            FirmaDigitalSST.usuario_id == usuario.id,
            FirmaDigitalSST.activo == True,
        )
        .all()
    )

    for firma in firmas_anteriores:
        firma.activo = False

    nueva_firma = FirmaDigitalSST(
        usuario_id=usuario.id,
        nombre_firmante=nombre_firmante,
        cargo=cargo,
        tipo_firma="FIRMA_PNG",
        archivo=str(ruta_fisica),
        url=url,
        mime_type=file.content_type,
        tamano_bytes=tamano_bytes,
        activo=True,
    )

    db.add(nueva_firma)
    db.commit()
    db.refresh(nueva_firma)

    return nueva_firma


@router.get(
    "/usuario/{usuario_id}",
    response_model=list[FirmaDigitalResponse],
)
def listar_firmas_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(ROLES_PERMITIDOS)),
):
    obtener_usuario_o_404(db, usuario_id)

    return (
        db.query(FirmaDigitalSST)
        .filter(FirmaDigitalSST.usuario_id == usuario_id)
        .order_by(FirmaDigitalSST.id.desc())
        .all()
    )


@router.get(
    "/usuario/{usuario_id}/activa",
    response_model=FirmaDigitalResponse,
)
def obtener_firma_activa_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(ROLES_PERMITIDOS)),
):
    obtener_usuario_o_404(db, usuario_id)

    firma = (
        db.query(FirmaDigitalSST)
        .filter(
            FirmaDigitalSST.usuario_id == usuario_id,
            FirmaDigitalSST.activo == True,
        )
        .order_by(FirmaDigitalSST.id.desc())
        .first()
    )

    if not firma:
        raise HTTPException(
            status_code=404,
            detail="El usuario no tiene firma activa",
        )

    return firma


@router.patch(
    "/{firma_id}/activar",
    response_model=FirmaDigitalResponse,
)
def activar_firma(
    firma_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(ROLES_PERMITIDOS)),
):
    firma = db.query(FirmaDigitalSST).filter(FirmaDigitalSST.id == firma_id).first()

    if not firma:
        raise HTTPException(
            status_code=404,
            detail="Firma no encontrada",
        )

    firmas_usuario = (
        db.query(FirmaDigitalSST)
        .filter(FirmaDigitalSST.usuario_id == firma.usuario_id)
        .all()
    )

    for item in firmas_usuario:
        item.activo = False

    firma.activo = True

    db.commit()
    db.refresh(firma)

    return firma


@router.delete("/{firma_id}")
def eliminar_firma(
    firma_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(require_roles(ROLES_PERMITIDOS)),
):
    firma = (
        db.query(FirmaDigitalSST)
        .filter(
            FirmaDigitalSST.id == firma_id,
            FirmaDigitalSST.activo == True,
        )
        .first()
    )

    if not firma:
        raise HTTPException(
            status_code=404,
            detail="Firma no encontrada",
        )

    firma.activo = False

    db.commit()

    return {
        "mensaje": "Firma electrónica desactivada correctamente",
    }
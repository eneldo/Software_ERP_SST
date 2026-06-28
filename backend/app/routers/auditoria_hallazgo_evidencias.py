# ============================================================
# ROUTER
# EVIDENCIAS FOTOGRÁFICAS HALLAZGOS AUDITORÍA SST
# FASE 1.7.4.2.2
# ============================================================

from pathlib import Path
from uuid import uuid4
import os
import shutil

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_roles
from app.models.auditoria_sst import AuditoriaHallazgoSST
from app.models.auditoria_hallazgo_evidencia import AuditoriaHallazgoEvidenciaSST
from app.schemas.auditoria_hallazgo_evidencia_schema import (
    AuditoriaHallazgoEvidenciaResponse,
)


router = APIRouter(
    prefix="/verificar/auditorias-hallazgos-evidencias",
    tags=["Auditorías SST Evidencias"],
)


ROLES_PERMITIDOS = [
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "RESPONSABLE_SST",
    "AUDITOR",
]


BASE_DIR = Path(__file__).resolve().parents[1]  # backend/app
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads"))
EVIDENCIAS_DIR = UPLOAD_DIR / "auditorias" / "hallazgos"
EVIDENCIAS_DIR.mkdir(parents=True, exist_ok=True)


def obtener_hallazgo_o_404(db: Session, hallazgo_id: int):
    hallazgo = (
        db.query(AuditoriaHallazgoSST)
        .filter(
            AuditoriaHallazgoSST.id == hallazgo_id,
            AuditoriaHallazgoSST.activo == True,
        )
        .first()
    )

    if not hallazgo:
        raise HTTPException(
            status_code=404,
            detail="Hallazgo de auditoría no encontrado",
        )

    return hallazgo


@router.post(
    "/{hallazgo_id}/upload",
    response_model=AuditoriaHallazgoEvidenciaResponse,
)
def subir_evidencia_hallazgo(
    hallazgo_id: int,
    descripcion: str = Form(default=""),
    tipo: str = Form(default="FOTO"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PERMITIDOS)),
):
    hallazgo = obtener_hallazgo_o_404(db, hallazgo_id)

    extension = Path(file.filename or "").suffix.lower()

    extensiones_permitidas = [
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".pdf",
    ]

    if extension not in extensiones_permitidas:
        raise HTTPException(
            status_code=400,
            detail="Formato no permitido. Use PNG, JPG, JPEG, WEBP o PDF.",
        )

    nombre_archivo = f"hallazgo_{hallazgo_id}_{uuid4().hex}{extension}"
    ruta_fisica = EVIDENCIAS_DIR / nombre_archivo

    with ruta_fisica.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    tamano_bytes = ruta_fisica.stat().st_size

    url = f"/uploads/auditorias/hallazgos/{nombre_archivo}"

    evidencia = AuditoriaHallazgoEvidenciaSST(
        hallazgo_id=hallazgo.id,
        auditoria_id=hallazgo.auditoria_id,
        empresa_id=hallazgo.empresa_id,
        usuario_id=getattr(usuario, "id", None),
        tipo=tipo,
        descripcion=descripcion,
        nombre_original=file.filename,
        archivo=str(ruta_fisica),
        url=url,
        extension=extension.replace(".", ""),
        mime_type=file.content_type,
        tamano_bytes=tamano_bytes,
        activo=True,
    )

    db.add(evidencia)
    db.commit()
    db.refresh(evidencia)

    return evidencia


@router.get(
    "/hallazgo/{hallazgo_id}",
    response_model=list[AuditoriaHallazgoEvidenciaResponse],
)
def listar_evidencias_hallazgo(
    hallazgo_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PERMITIDOS)),
):
    obtener_hallazgo_o_404(db, hallazgo_id)

    return (
        db.query(AuditoriaHallazgoEvidenciaSST)
        .filter(
            AuditoriaHallazgoEvidenciaSST.hallazgo_id == hallazgo_id,
            AuditoriaHallazgoEvidenciaSST.activo == True,
        )
        .order_by(AuditoriaHallazgoEvidenciaSST.id.desc())
        .all()
    )


@router.get(
    "/auditoria/{auditoria_id}",
    response_model=list[AuditoriaHallazgoEvidenciaResponse],
)
def listar_evidencias_auditoria(
    auditoria_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PERMITIDOS)),
):
    return (
        db.query(AuditoriaHallazgoEvidenciaSST)
        .filter(
            AuditoriaHallazgoEvidenciaSST.auditoria_id == auditoria_id,
            AuditoriaHallazgoEvidenciaSST.activo == True,
        )
        .order_by(AuditoriaHallazgoEvidenciaSST.id.desc())
        .all()
    )


@router.delete("/{evidencia_id}")
def eliminar_evidencia_hallazgo(
    evidencia_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PERMITIDOS)),
):
    evidencia = (
        db.query(AuditoriaHallazgoEvidenciaSST)
        .filter(
            AuditoriaHallazgoEvidenciaSST.id == evidencia_id,
            AuditoriaHallazgoEvidenciaSST.activo == True,
        )
        .first()
    )

    if not evidencia:
        raise HTTPException(
            status_code=404,
            detail="Evidencia no encontrada",
        )

    evidencia.activo = False

    db.commit()

    return {
        "mensaje": "Evidencia desactivada correctamente",
    }
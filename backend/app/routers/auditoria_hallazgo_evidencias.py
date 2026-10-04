# ============================================================
# ROUTER
# EVIDENCIAS FOTOGRÁFICAS HALLAZGOS AUDITORÍA SST
# FASE 1.7.4.2.2
# ============================================================

from pathlib import Path
from uuid import uuid4
import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_roles
from app.core.file_security import validate_upload
from app.models.auditoria_sst import AuditoriaSST, AuditoriaHallazgoSST
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


def _tenant_id(usuario) -> int | None:
    if str(getattr(usuario, "rol", "") or "").upper() == "SUPER_ADMIN":
        return None
    empresa_id = getattr(usuario, "empresa_id", None)
    if empresa_id is None:
        raise HTTPException(status_code=403, detail="Usuario sin empresa asignada")
    return int(empresa_id)


def obtener_hallazgo_o_404(db: Session, hallazgo_id: int, usuario):
    filtros = [AuditoriaHallazgoSST.id == hallazgo_id, AuditoriaHallazgoSST.activo]
    tenant_id = _tenant_id(usuario)
    if tenant_id is not None:
        filtros.append(AuditoriaHallazgoSST.empresa_id == tenant_id)
    hallazgo = db.query(AuditoriaHallazgoSST).filter(*filtros).first()

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
    hallazgo = obtener_hallazgo_o_404(db, hallazgo_id, usuario)

    validation = validate_upload(
        file,
        allowed_extensions={".png", ".jpg", ".jpeg", ".webp", ".pdf"},
    )
    extension = validation.extension
    nombre_archivo = f"hallazgo_{hallazgo_id}_{uuid4().hex}{extension}"
    ruta_fisica = EVIDENCIAS_DIR / nombre_archivo

    try:
        ruta_fisica.write_bytes(validation.content)
        evidencia = AuditoriaHallazgoEvidenciaSST(
            hallazgo_id=hallazgo.id,
            auditoria_id=hallazgo.auditoria_id,
            empresa_id=hallazgo.empresa_id,
            usuario_id=getattr(usuario, "id", None),
            tipo=tipo,
            descripcion=descripcion,
            nombre_original=validation.safe_filename,
            archivo=str(ruta_fisica),
            url=f"/uploads/auditorias/hallazgos/{nombre_archivo}",
            extension=extension.replace(".", ""),
            mime_type=validation.mime_type,
            tamano_bytes=validation.size_bytes,
            activo=True,
        )
        db.add(evidencia)
        db.commit()
        db.refresh(evidencia)
        return evidencia
    except Exception:
        db.rollback()
        ruta_fisica.unlink(missing_ok=True)
        raise


@router.get(
    "/hallazgo/{hallazgo_id}",
    response_model=list[AuditoriaHallazgoEvidenciaResponse],
)
def listar_evidencias_hallazgo(
    hallazgo_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_PERMITIDOS)),
):
    obtener_hallazgo_o_404(db, hallazgo_id, usuario)

    return (
        db.query(AuditoriaHallazgoEvidenciaSST)
        .filter(
            AuditoriaHallazgoEvidenciaSST.hallazgo_id == hallazgo_id,
            AuditoriaHallazgoEvidenciaSST.activo,
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
    filtros_auditoria = [AuditoriaSST.id == auditoria_id, AuditoriaSST.activo]
    tenant_id = _tenant_id(usuario)
    if tenant_id is not None:
        filtros_auditoria.append(AuditoriaSST.empresa_id == tenant_id)
    if not db.query(AuditoriaSST).filter(*filtros_auditoria).first():
        raise HTTPException(status_code=404, detail="Auditoría no encontrada")
    return (
        db.query(AuditoriaHallazgoEvidenciaSST)
        .filter(
            AuditoriaHallazgoEvidenciaSST.auditoria_id == auditoria_id,
            AuditoriaHallazgoEvidenciaSST.activo,
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
    filtros = [
        AuditoriaHallazgoEvidenciaSST.id == evidencia_id,
        AuditoriaHallazgoEvidenciaSST.activo,
    ]
    tenant_id = _tenant_id(usuario)
    if tenant_id is not None:
        filtros.append(AuditoriaHallazgoEvidenciaSST.empresa_id == tenant_id)
    evidencia = db.query(AuditoriaHallazgoEvidenciaSST).filter(*filtros).first()

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

# ============================================================
# ROUTER ARCHIVOS SST
# FASE 2.2.1A - Gestión Documental y Evidencias PRO
# ============================================================

import os
from uuid import uuid4
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.archivo_sst import ArchivoSST
from app.models.empresa import Empresa
from app.auth.dependencies import get_current_user, require_roles
from app.core.file_security import validate_upload
from app.schemas.archivo_sst_schema import ArchivoSSTResponse


router = APIRouter(
    prefix="/archivos-sst",
    tags=["Gestión Documental y Evidencias PRO"],
)


BASE_UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"


def _empresa_id_autorizada(usuario, empresa_id: int | None) -> int | None:
    if str(getattr(usuario, "rol", "") or "").upper() == "SUPER_ADMIN":
        return empresa_id
    usuario_empresa_id = getattr(usuario, "empresa_id", None)
    if usuario_empresa_id is None:
        raise HTTPException(status_code=403, detail="Usuario sin empresa asignada")
    if empresa_id is not None and int(usuario_empresa_id) != int(empresa_id):
        raise HTTPException(status_code=403, detail="No tiene permisos sobre esta empresa")
    return int(usuario_empresa_id)

TIPOS_PERMITIDOS = {
    "LOGO": "logos",
    "FIRMA_REPRESENTANTE": "firmas",
    "FIRMA_SST": "firmas",
    "SELLO": "firmas",
    "DOCUMENTO": "documentos",
    "EVIDENCIA": "evidencias",
    "ACTA": "actas",
    "CAPACITACION": "capacitaciones",
    "AUDITORIA": "auditorias",
}

EXTENSIONES_PERMITIDAS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}


def validar_archivo(file: UploadFile):
    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in EXTENSIONES_PERMITIDAS:
        raise HTTPException(
            status_code=400,
            detail=f"Extensión no permitida: {extension}",
        )

    return extension


@router.post("/subir", response_model=ArchivoSSTResponse)
def subir_archivo_sst(
    empresa_id: int = Form(...),
    tipo: str = Form(...),
    modulo: str | None = Form(None),
    referencia_id: int | None = Form(None),
    descripcion: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario=Depends(
        require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"])
    ),
):
    empresa_id = _empresa_id_autorizada(usuario, empresa_id)
    tipo = tipo.upper()

    if tipo not in TIPOS_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail="Tipo de archivo no permitido",
        )

    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    validation = validate_upload(file)
    extension = validation.extension

    carpeta_tipo = TIPOS_PERMITIDOS[tipo]
    carpeta_destino = BASE_UPLOAD_DIR / carpeta_tipo
    carpeta_destino.mkdir(parents=True, exist_ok=True)

    nombre_archivo = f"{uuid4().hex}{extension}"
    ruta_fisica = carpeta_destino / nombre_archivo

    ruta_fisica.write_bytes(validation.content)

    tamano_bytes = ruta_fisica.stat().st_size
    url = f"/uploads/{carpeta_tipo}/{nombre_archivo}"

    registro = ArchivoSST(
        empresa_id=empresa_id,
        usuario_id=usuario.id,
        tipo=tipo,
        nombre_original=validation.safe_filename,
        nombre_archivo=nombre_archivo,
        ruta=str(ruta_fisica),
        url=url,
        extension=extension,
        mime_type=validation.mime_type,
        tamano_bytes=tamano_bytes,
        modulo=modulo.upper() if modulo else None,
        referencia_id=referencia_id,
        descripcion=descripcion,
        activo=True,
    )

    db.add(registro)
    db.commit()
    db.refresh(registro)

    return registro


@router.get("/", response_model=list[ArchivoSSTResponse])
def listar_archivos_sst(
    empresa_id: int | None = None,
    tipo: str | None = None,
    modulo: str | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(
        require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"])
    ),
):
    empresa_id = _empresa_id_autorizada(usuario, empresa_id)
    query = db.query(ArchivoSST).filter(ArchivoSST.activo == True)

    if empresa_id is not None:
        query = query.filter(ArchivoSST.empresa_id == empresa_id)

    if tipo:
        query = query.filter(ArchivoSST.tipo == tipo.upper())

    if modulo:
        query = query.filter(ArchivoSST.modulo == modulo.upper())

    return query.order_by(ArchivoSST.id.desc()).all()


@router.get("/{archivo_id}", response_model=ArchivoSSTResponse)
def obtener_archivo_sst(
    archivo_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(
        require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"])
    ),
):
    tenant_id = _empresa_id_autorizada(usuario, None)
    filtros = [ArchivoSST.id == archivo_id]
    if tenant_id is not None:
        filtros.append(ArchivoSST.empresa_id == tenant_id)
    archivo = db.query(ArchivoSST).filter(*filtros).first()

    if not archivo:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    return archivo


@router.delete("/{archivo_id}")
def eliminar_archivo_sst(
    archivo_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    tenant_id = _empresa_id_autorizada(usuario, None)
    filtros = [ArchivoSST.id == archivo_id]
    if tenant_id is not None:
        filtros.append(ArchivoSST.empresa_id == tenant_id)
    archivo = db.query(ArchivoSST).filter(*filtros).first()

    if not archivo:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    archivo.activo = False
    db.commit()

    return {"mensaje": "Archivo desactivado correctamente"}

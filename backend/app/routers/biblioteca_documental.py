from uuid import uuid4
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles, require_permission
from app.core.default_permissions import PERM_REGISTROS_ELIMINAR
from app.core.file_security import validate_upload

from app.models.empresa import Empresa
from app.models.archivo_sst import ArchivoSST
from app.models.biblioteca_documental import BibliotecaDocumental

from app.schemas.biblioteca_documental_schema import (
    BibliotecaDocumentalCreate,
    BibliotecaDocumentalUpdate,
    BibliotecaDocumentalResponse,
)


router = APIRouter(
    prefix="/biblioteca-documental",
    tags=["Biblioteca Documental SST"],
)


BASE_UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads" / "documentos"
ELIMINAR_REGISTROS = require_permission(PERM_REGISTROS_ELIMINAR)

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


def serializar_documento(documento: BibliotecaDocumental):
    archivo = documento.archivo

    return {
        "id": documento.id,
        "empresa_id": documento.empresa_id,
        "archivo_id": documento.archivo_id,
        "usuario_id": documento.usuario_id,
        "codigo_documental": documento.codigo_documental,
        "titulo": documento.titulo,
        "categoria": documento.categoria,
        "tipo_documento": documento.tipo_documento,
        "modulo_origen": documento.modulo_origen,
        "version": documento.version,
        "estado": documento.estado,
        "responsable": documento.responsable,
        "descripcion": documento.descripcion,
        "palabras_clave": documento.palabras_clave,
        "fecha_aprobacion": documento.fecha_aprobacion,
        "fecha_vencimiento": documento.fecha_vencimiento,
        "activo": documento.activo,
        "archivo_url": archivo.url if archivo else None,
        "archivo_nombre": archivo.nombre_original if archivo else None,
        "archivo_extension": archivo.extension if archivo else None,
        "archivo_mime_type": archivo.mime_type if archivo else None,
        "fecha_creacion": documento.fecha_creacion,
        "fecha_actualizacion": documento.fecha_actualizacion,
    }


@router.post("/", response_model=BibliotecaDocumentalResponse)
def crear_documento_biblioteca(
    data: BibliotecaDocumentalCreate,
    db: Session = Depends(get_db),
    usuario=Depends(ELIMINAR_REGISTROS),
):
    empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    if data.archivo_id:
        archivo = db.query(ArchivoSST).filter(ArchivoSST.id == data.archivo_id).first()

        if not archivo:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

    existe = (
        db.query(BibliotecaDocumental)
        .filter(
            BibliotecaDocumental.empresa_id == data.empresa_id,
            BibliotecaDocumental.codigo_documental == data.codigo_documental,
            BibliotecaDocumental.version == data.version,
        )
        .first()
    )

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un documento con ese código y versión para la empresa",
        )

    documento = BibliotecaDocumental(
        **data.model_dump(),
        usuario_id=usuario.id,
    )

    db.add(documento)
    db.commit()
    db.refresh(documento)

    return serializar_documento(documento)


@router.post("/subir", response_model=BibliotecaDocumentalResponse)
def subir_documento_biblioteca(
    empresa_id: int = Form(...),
    codigo_documental: str = Form(...),
    titulo: str = Form(...),
    categoria: str = Form(...),
    tipo_documento: str = Form(...),
    modulo_origen: str | None = Form(None),
    version: str = Form("1.0"),
    estado: str = Form("BORRADOR"),
    responsable: str | None = Form(None),
    descripcion: str | None = Form(None),
    palabras_clave: str | None = Form(None),
    fecha_aprobacion: str | None = Form(None),
    fecha_vencimiento: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    validation = validate_upload(file)
    extension = validation.extension

    BASE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    nombre_archivo = f"{uuid4().hex}{extension}"
    ruta_fisica = BASE_UPLOAD_DIR / nombre_archivo

    ruta_fisica.write_bytes(validation.content)

    url = f"/uploads/documentos/{nombre_archivo}"

    archivo = ArchivoSST(
        empresa_id=empresa_id,
        usuario_id=usuario.id,
        tipo="DOCUMENTO",
        nombre_original=validation.safe_filename,
        nombre_archivo=nombre_archivo,
        ruta=str(ruta_fisica),
        url=url,
        extension=extension,
        mime_type=validation.mime_type,
        tamano_bytes=ruta_fisica.stat().st_size,
        modulo="BIBLIOTECA_DOCUMENTAL",
        referencia_id=None,
        descripcion=descripcion,
        activo=True,
    )

    db.add(archivo)
    db.commit()
    db.refresh(archivo)

    documento = BibliotecaDocumental(
        empresa_id=empresa_id,
        archivo_id=archivo.id,
        usuario_id=usuario.id,
        codigo_documental=codigo_documental,
        titulo=titulo,
        categoria=categoria,
        tipo_documento=tipo_documento,
        modulo_origen=modulo_origen,
        version=version,
        estado=estado,
        responsable=responsable,
        descripcion=descripcion,
        palabras_clave=palabras_clave,
        fecha_aprobacion=fecha_aprobacion or None,
        fecha_vencimiento=fecha_vencimiento or None,
        activo=True,
    )

    db.add(documento)
    db.commit()
    db.refresh(documento)

    archivo.referencia_id = documento.id
    db.commit()
    db.refresh(documento)

    return serializar_documento(documento)


@router.get("/", response_model=list[BibliotecaDocumentalResponse])
def listar_biblioteca_documental(
    empresa_id: int | None = None,
    categoria: str | None = None,
    estado: str | None = None,
    tipo_documento: str | None = None,
    buscar: str | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"])),
):
    query = db.query(BibliotecaDocumental).filter(BibliotecaDocumental.activo == True)

    if empresa_id:
        query = query.filter(BibliotecaDocumental.empresa_id == empresa_id)

    if categoria:
        query = query.filter(BibliotecaDocumental.categoria == categoria.upper())

    if estado:
        query = query.filter(BibliotecaDocumental.estado == estado.upper())

    if tipo_documento:
        query = query.filter(BibliotecaDocumental.tipo_documento == tipo_documento.upper())

    if buscar:
        patron = f"%{buscar}%"
        query = query.filter(
            BibliotecaDocumental.titulo.ilike(patron)
            | BibliotecaDocumental.codigo_documental.ilike(patron)
            | BibliotecaDocumental.descripcion.ilike(patron)
            | BibliotecaDocumental.palabras_clave.ilike(patron)
        )

    documentos = query.order_by(BibliotecaDocumental.id.desc()).all()

    return [serializar_documento(doc) for doc in documentos]


@router.get("/{documento_id}", response_model=BibliotecaDocumentalResponse)
def obtener_documento_biblioteca(
    documento_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"])),
):
    documento = db.query(BibliotecaDocumental).filter(BibliotecaDocumental.id == documento_id).first()

    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    return serializar_documento(documento)


@router.put("/{documento_id}", response_model=BibliotecaDocumentalResponse)
def actualizar_documento_biblioteca(
    documento_id: int,
    data: BibliotecaDocumentalUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    documento = db.query(BibliotecaDocumental).filter(BibliotecaDocumental.id == documento_id).first()

    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(documento, key, value)

    db.commit()
    db.refresh(documento)

    return serializar_documento(documento)


@router.patch("/{documento_id}/vigente", response_model=BibliotecaDocumentalResponse)
def marcar_documento_vigente(
    documento_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    documento = db.query(BibliotecaDocumental).filter(BibliotecaDocumental.id == documento_id).first()

    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    documento.estado = "VIGENTE"

    db.commit()
    db.refresh(documento)

    return serializar_documento(documento)


@router.patch("/{documento_id}/obsoleto", response_model=BibliotecaDocumentalResponse)
def marcar_documento_obsoleto(
    documento_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    documento = db.query(BibliotecaDocumental).filter(BibliotecaDocumental.id == documento_id).first()

    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    documento.estado = "OBSOLETO"

    db.commit()
    db.refresh(documento)

    return serializar_documento(documento)


@router.delete("/{documento_id}")
def eliminar_documento_biblioteca(
    documento_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"])),
):
    documento = db.query(BibliotecaDocumental).filter(BibliotecaDocumental.id == documento_id).first()

    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    documento.activo = False

    db.commit()

    return {"mensaje": "Documento desactivado correctamente"}

# ============================================================
# SERVICIO EVIDENCIAS INTELIGENTES REPORTES SST - ERP SST PRO
# FASE 1.1.25.6
# Archivo: backend/app/services/reporte_evidencia_service.py
# ============================================================

from __future__ import annotations

from io import BytesIO
from pathlib import Path
import os
import shutil
import uuid

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.reporte_evidencia_sst import ReporteEvidenciaSST
from app.models.reporte_inseguridad import ReporteInseguridadSST

try:
    from PIL import Image, ImageOps
except Exception:  # pragma: no cover
    Image = None
    ImageOps = None

UPLOAD_ROOT = Path(os.getenv("UPLOAD_DIR", "app/uploads")).resolve()
UPLOAD_DIR = UPLOAD_ROOT / "reportes-anonimos"
UPLOAD_EVID_DIR = UPLOAD_DIR / "evidencias"
UPLOAD_THUMB_DIR = UPLOAD_DIR / "thumbs"
UPLOAD_ORIGINAL_DIR = UPLOAD_DIR / "originales"

for d in (UPLOAD_DIR, UPLOAD_EVID_DIR, UPLOAD_THUMB_DIR, UPLOAD_ORIGINAL_DIR):
    d.mkdir(parents=True, exist_ok=True)

ALLOWED_EXT = {"pdf", "jpg", "jpeg", "png", "webp", "mp4", "mov", "m4v", "avi", "mp3", "wav", "ogg"}
IMAGE_EXT = {"jpg", "jpeg", "png", "webp"}
VIDEO_EXT = {"mp4", "mov", "m4v", "avi"}
AUDIO_EXT = {"mp3", "wav", "ogg"}
MAX_MB = int(os.getenv("REPORTE_EVIDENCIA_MAX_MB", "25"))
MAX_FILES = int(os.getenv("REPORTE_EVIDENCIA_MAX_FILES", "10"))
IMAGE_MAX_WIDTH = int(os.getenv("REPORTE_EVIDENCIA_IMAGE_MAX_WIDTH", "1600"))
IMAGE_MAX_HEIGHT = int(os.getenv("REPORTE_EVIDENCIA_IMAGE_MAX_HEIGHT", "1600"))
THUMB_SIZE = int(os.getenv("REPORTE_EVIDENCIA_THUMB_SIZE", "360"))
JPEG_QUALITY = int(os.getenv("REPORTE_EVIDENCIA_JPEG_QUALITY", "78"))
WEBP_QUALITY = int(os.getenv("REPORTE_EVIDENCIA_WEBP_QUALITY", "78"))


def public_url(path: Path) -> str:
    try:
        rel = path.resolve().relative_to(UPLOAD_ROOT)
        return "/uploads/" + rel.as_posix()
    except Exception:
        return "/uploads/reportes-anonimos/evidencias/" + path.name


def extension_from_name(filename: str | None) -> str:
    original = filename or "evidencia"
    return original.rsplit(".", 1)[-1].lower() if "." in original else "bin"


def tipo_archivo(extension: str, mime_type: str | None = None) -> str:
    mime = (mime_type or "").lower()
    if extension in IMAGE_EXT or mime.startswith("image/"):
        return "IMAGEN"
    if extension in VIDEO_EXT or mime.startswith("video/"):
        return "VIDEO"
    if extension == "pdf" or mime == "application/pdf":
        return "PDF"
    if extension in AUDIO_EXT or mime.startswith("audio/"):
        return "AUDIO"
    return "OTRO"


def clasificar_ia(texto: str | None, filename: str | None = None) -> tuple[str, str]:
    base = f"{texto or ''} {filename or ''}".lower()
    reglas = [
        ("RIESGO_ELECTRICO", ["eléctr", "electric", "cable", "tablero", "tomacorriente", "energizado", "chispa"]),
        ("INCENDIO", ["incendio", "fuego", "extintor", "humo", "combustible", "caliente"]),
        ("EPP", ["casco", "guante", "gafas", "arnés", "arnes", "botas", "protección", "proteccion", "epp"]),
        ("ORDEN_ASEO", ["orden", "aseo", "basura", "derrame", "obstru", "sucio", "desorden"]),
        ("RIESGO_LOCATIVO", ["piso", "escalera", "baranda", "techo", "pared", "hueco", "caída", "caida"]),
        ("QUIMICO", ["quím", "quim", "ácido", "acido", "solvente", "sustancia", "derrame químico"]),
        ("BIOLOGICO", ["biológ", "biolog", "sangre", "residuo", "infecc", "bacteria", "virus"]),
        ("MECANICO", ["máquina", "maquina", "atrapamiento", "polea", "motor", "herramienta", "corte"]),
        ("ACTO_INSEGURO", ["sin permiso", "no usa", "corriendo", "imprud", "acto inseguro"]),
        ("CONDICION_INSEGURA", ["condición", "condicion", "riesgo", "peligro", "insegura"]),
    ]
    for categoria, palabras in reglas:
        if any(p in base for p in palabras):
            return categoria, "Clasificación automática por palabras clave SST del reporte/evidencia."
    return "CONDICION_INSEGURA", "Clasificación automática por defecto. Validar por responsable SST."


def _read_upload(upload: UploadFile) -> bytes:
    content = upload.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="El archivo de evidencia está vacío")
    if len(content) > MAX_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"La evidencia supera {MAX_MB} MB")
    return content


def _save_raw(content: bytes, extension: str, folder: Path) -> Path:
    path = folder / f"{uuid.uuid4().hex}.{extension}"
    path.write_bytes(content)
    return path


def _optimize_image(content: bytes, extension: str) -> tuple[Path, Path, int]:
    if Image is None or ImageOps is None:
        opt = _save_raw(content, extension, UPLOAD_EVID_DIR)
        thumb = _save_raw(content, extension, UPLOAD_THUMB_DIR)
        return opt, thumb, len(content)

    try:
        with Image.open(BytesIO(content)) as img:
            img = ImageOps.exif_transpose(img)
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            img.thumbnail((IMAGE_MAX_WIDTH, IMAGE_MAX_HEIGHT))

            save_ext = "webp"
            optimized_path = UPLOAD_EVID_DIR / f"{uuid.uuid4().hex}.webp"
            img.save(optimized_path, format="WEBP", quality=WEBP_QUALITY, method=6)

            thumb_img = img.copy()
            thumb_img.thumbnail((THUMB_SIZE, THUMB_SIZE))
            thumb_path = UPLOAD_THUMB_DIR / f"{uuid.uuid4().hex}.webp"
            thumb_img.save(thumb_path, format="WEBP", quality=72, method=6)

            return optimized_path, thumb_path, optimized_path.stat().st_size
    except Exception:
        opt = _save_raw(content, extension, UPLOAD_EVID_DIR)
        thumb = _save_raw(content, extension, UPLOAD_THUMB_DIR)
        return opt, thumb, len(content)


def guardar_evidencia_reporte(
    db: Session,
    reporte: ReporteInseguridadSST,
    upload: UploadFile,
    descripcion_base: str | None = None,
    commit: bool = False,
) -> ReporteEvidenciaSST:
    extension = extension_from_name(upload.filename)
    if extension not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail="Archivo no permitido. Use imagen, video, PDF o audio permitido.")

    content = _read_upload(upload)
    original_path = _save_raw(content, extension, UPLOAD_ORIGINAL_DIR)
    tipo = tipo_archivo(extension, upload.content_type)

    if tipo == "IMAGEN":
        archivo_path, thumb_path, optimized_size = _optimize_image(content, extension)
    else:
        archivo_path = _save_raw(content, extension, UPLOAD_EVID_DIR)
        thumb_path = None
        optimized_size = len(content)

    categoria, descripcion_ia = clasificar_ia(descripcion_base or reporte.descripcion, upload.filename)
    evidencia = ReporteEvidenciaSST(
        reporte_id=reporte.id,
        tipo_archivo=tipo,
        archivo_nombre=upload.filename or f"evidencia.{extension}",
        archivo_url=public_url(archivo_path),
        archivo_original_url=public_url(original_path),
        archivo_thumbnail_url=public_url(thumb_path) if thumb_path else None,
        mime_type=upload.content_type,
        peso_original_bytes=len(content),
        peso_optimizado_bytes=optimized_size,
        extension=extension,
        categoria_ia=categoria,
        descripcion_ia=descripcion_ia,
        origen="REPORTE_ANONIMO_SST",
        activo=True,
    )
    db.add(evidencia)
    db.flush()

    # Mantiene compatibilidad con frontend antiguo: primera evidencia como principal
    if not reporte.archivo_url:
        reporte.archivo_url = evidencia.archivo_url
        reporte.archivo_nombre = evidencia.archivo_nombre
        reporte.archivo_mime_type = evidencia.mime_type
        reporte.archivo_tamano_bytes = evidencia.peso_optimizado_bytes or evidencia.peso_original_bytes

    if commit:
        db.commit()
        db.refresh(evidencia)
    return evidencia


def guardar_evidencias_reporte(
    db: Session,
    reporte: ReporteInseguridadSST,
    uploads: list[UploadFile] | None,
    descripcion_base: str | None = None,
) -> list[ReporteEvidenciaSST]:
    validos = [u for u in (uploads or []) if u and getattr(u, "filename", None)]
    if len(validos) > MAX_FILES:
        raise HTTPException(status_code=400, detail=f"Máximo {MAX_FILES} evidencias por reporte")
    return [guardar_evidencia_reporte(db, reporte, upload, descripcion_base, commit=False) for upload in validos]


def crear_registro_evidencia_desde_url(
    db: Session,
    reporte_id: int,
    archivo_url: str,
    archivo_nombre: str | None = None,
    mime_type: str | None = None,
    peso_bytes: int | None = None,
    descripcion_base: str | None = None,
) -> ReporteEvidenciaSST:
    ext = extension_from_name(archivo_nombre or archivo_url)
    categoria, descripcion_ia = clasificar_ia(descripcion_base, archivo_nombre)
    evidencia = ReporteEvidenciaSST(
        reporte_id=reporte_id,
        tipo_archivo=tipo_archivo(ext, mime_type),
        archivo_nombre=archivo_nombre or Path(archivo_url).name,
        archivo_url=archivo_url,
        archivo_original_url=archivo_url,
        archivo_thumbnail_url=None,
        mime_type=mime_type,
        peso_original_bytes=peso_bytes,
        peso_optimizado_bytes=peso_bytes,
        extension=ext,
        categoria_ia=categoria,
        descripcion_ia=descripcion_ia,
        origen="MIGRACION_EVIDENCIA_LEGADO",
        activo=True,
    )
    db.add(evidencia)
    db.flush()
    return evidencia


def sincronizar_evidencia_legado(db: Session, reporte: ReporteInseguridadSST):
    if not reporte.archivo_url:
        return None
    existe = db.query(ReporteEvidenciaSST).filter(
        ReporteEvidenciaSST.reporte_id == reporte.id,
        ReporteEvidenciaSST.archivo_url == reporte.archivo_url,
    ).first()
    if existe:
        return existe
    return crear_registro_evidencia_desde_url(
        db=db,
        reporte_id=reporte.id,
        archivo_url=reporte.archivo_url,
        archivo_nombre=reporte.archivo_nombre,
        mime_type=reporte.archivo_mime_type,
        peso_bytes=reporte.archivo_tamano_bytes,
        descripcion_base=reporte.descripcion,
    )


def clonar_archivo_si_existe(origen_url: str | None, subcarpeta: str = "relacionadas") -> str | None:
    if not origen_url or not origen_url.startswith("/uploads/"):
        return origen_url
    rel = origen_url.replace("/uploads/", "", 1)
    origen_path = UPLOAD_ROOT / rel
    if not origen_path.exists() or not origen_path.is_file():
        return origen_url
    destino_dir = UPLOAD_ROOT / subcarpeta
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino_path = destino_dir / f"{uuid.uuid4().hex}{origen_path.suffix}"
    shutil.copy2(origen_path, destino_path)
    return public_url(destino_path)

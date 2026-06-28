# ============================================================
# ERP SST COLOMBIA
# SERVICIO GLOBAL DE UPLOADS OPTIMIZADOS
# ============================================================
# Uso:
#   from app.services.upload_service import guardar_evidencia_sst
#
#   resultado = guardar_evidencia_sst(
#       file=archivo,
#       modulo="capacitaciones",
#       formato_imagen="webp",
#   )
#
# Retorna:
# {
#   "url": "/uploads/capacitaciones/archivo.webp",
#   "nombre_archivo": "archivo.webp",
#   "extension": ".webp",
#   "mime_type": "image/webp",
#   "tamano_bytes": 104833,
#   "optimizado": True
# }
# ============================================================

from pathlib import Path
from uuid import uuid4
import os
import shutil
from typing import Optional

from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError


# ============================================================
# CONFIGURACIÓN GLOBAL
# ============================================================

MAX_UPLOAD_MB = 10
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

TARGET_MAX_BYTES = 500 * 1024       # 500 KB
DEFAULT_MAX_WIDTH = 1600
DEFAULT_MAX_HEIGHT = 1600

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx"}
ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS | DOCUMENT_EXTENSIONS

BASE_UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"


# ============================================================
# VALIDACIONES
# ============================================================

def normalizar_modulo(modulo: str) -> str:
    """
    Limpia el nombre del módulo para evitar rutas inseguras.
    """
    if not modulo:
        raise HTTPException(status_code=400, detail="El módulo de carga es obligatorio.")

    modulo = modulo.strip().lower().replace("\\", "").replace("/", "")
    modulo = modulo.replace("..", "")

    if not modulo:
        raise HTTPException(status_code=400, detail="Nombre de módulo inválido.")

    return modulo


def validar_extension(nombre_archivo: str) -> str:
    extension = Path(nombre_archivo or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Extensión no permitida: {extension}. Permitidas: {sorted(ALLOWED_EXTENSIONS)}",
        )

    return extension


def validar_tamano_upload(upload_file: UploadFile) -> None:
    """
    Valida tamaño sin cargar todo el archivo en memoria.
    """
    upload_file.file.seek(0, os.SEEK_END)
    size = upload_file.file.tell()
    upload_file.file.seek(0)

    if size > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Archivo demasiado grande. Máximo permitido: {MAX_UPLOAD_MB} MB.",
        )


# ============================================================
# UTILIDADES DE GUARDADO
# ============================================================

def obtener_directorio_modulo(modulo: str) -> Path:
    modulo_limpio = normalizar_modulo(modulo)
    destino = BASE_UPLOAD_DIR / modulo_limpio
    destino.mkdir(parents=True, exist_ok=True)
    return destino


def construir_url(destino_dir: Path, nombre_archivo: str) -> str:
    """
    Construye URL pública compatible con:
    app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
    """
    return f"/uploads/{destino_dir.name}/{nombre_archivo}"


def guardar_documento_sin_comprimir(
    file: UploadFile,
    destino_dir: Path,
    extension: str,
) -> dict:
    nombre_archivo = f"{uuid4().hex}{extension}"
    ruta = destino_dir / nombre_archivo

    with ruta.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "nombre_archivo": nombre_archivo,
        "ruta_fisica": str(ruta),
        "url": construir_url(destino_dir, nombre_archivo),
        "extension": extension,
        "mime_type": file.content_type,
        "tamano_bytes": ruta.stat().st_size,
        "optimizado": False,
    }


def optimizar_imagen(
    file: UploadFile,
    destino_dir: Path,
    formato_salida: str = "webp",
    max_width: int = DEFAULT_MAX_WIDTH,
    max_height: int = DEFAULT_MAX_HEIGHT,
) -> dict:
    formato_salida = (formato_salida or "webp").lower().strip()
    extension_salida = ".webp" if formato_salida == "webp" else ".jpg"
    pil_format = "WEBP" if extension_salida == ".webp" else "JPEG"

    nombre_archivo = f"{uuid4().hex}{extension_salida}"
    ruta = destino_dir / nombre_archivo

    try:
        file.file.seek(0)

        with Image.open(file.file) as img:
            # Corrige orientación EXIF de fotos de celular.
            img = ImageOps.exif_transpose(img)

            # Convierte transparencias a fondo blanco.
            if img.mode in ("RGBA", "LA", "P"):
                rgba = img.convert("RGBA")
                fondo = Image.new("RGB", rgba.size, (255, 255, 255))
                fondo.paste(rgba, mask=rgba.split()[-1])
                img = fondo
            else:
                img = img.convert("RGB")

            # Redimensiona sin deformar.
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # Calidad inicial 80 y reducción progresiva.
            for calidad in [80, 75, 70, 65, 60, 55, 50]:
                parametros = {
                    "format": pil_format,
                    "quality": calidad,
                    "optimize": True,
                }

                if pil_format == "WEBP":
                    parametros["method"] = 6

                img.save(ruta, **parametros)

                if ruta.stat().st_size <= TARGET_MAX_BYTES:
                    break

            # Si sigue pesada, reduce resolución.
            if ruta.exists() and ruta.stat().st_size > TARGET_MAX_BYTES:
                for escala in [0.85, 0.75, 0.65, 0.55]:
                    nuevo_ancho = max(800, int(img.width * escala))
                    nuevo_alto = max(800, int(img.height * escala))
                    reducida = img.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)

                    parametros = {
                        "format": pil_format,
                        "quality": 70,
                        "optimize": True,
                    }

                    if pil_format == "WEBP":
                        parametros["method"] = 6

                    reducida.save(ruta, **parametros)

                    if ruta.stat().st_size <= TARGET_MAX_BYTES:
                        break

    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="El archivo no es una imagen válida.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error optimizando imagen: {exc}")

    return {
        "nombre_archivo": nombre_archivo,
        "ruta_fisica": str(ruta),
        "url": construir_url(destino_dir, nombre_archivo),
        "extension": extension_salida,
        "mime_type": "image/webp" if extension_salida == ".webp" else "image/jpeg",
        "tamano_bytes": ruta.stat().st_size,
        "optimizado": True,
    }


# ============================================================
# FUNCIÓN GLOBAL PARA TODOS LOS MÓDULOS SST
# ============================================================

def guardar_evidencia_sst(
    file: UploadFile,
    modulo: str,
    formato_imagen: str = "webp",
    max_width: int = DEFAULT_MAX_WIDTH,
    max_height: int = DEFAULT_MAX_HEIGHT,
) -> dict:
    """
    Función global para cualquier módulo del ERP SST.

    Módulos sugeridos:
    - evaluacion-inicial
    - matriz-legal
    - matriz-peligros
    - plan-anual
    - capacitaciones
    - inspecciones
    - epp
    - incidentes
    - auditorias
    - acciones-correctivas
    """
    extension = validar_extension(file.filename)
    validar_tamano_upload(file)

    destino_dir = obtener_directorio_modulo(modulo)

    if extension in IMAGE_EXTENSIONS:
        return optimizar_imagen(
            file=file,
            destino_dir=destino_dir,
            formato_salida=formato_imagen,
            max_width=max_width,
            max_height=max_height,
        )

    return guardar_documento_sin_comprimir(
        file=file,
        destino_dir=destino_dir,
        extension=extension,
    )


# Compatibilidad con nombre anterior
def guardar_upload_optimizado(
    file: UploadFile,
    destino_dir: Optional[Path] = None,
    formato_imagen: str = "webp",
    modulo: Optional[str] = None,
) -> dict:
    """
    Compatibilidad temporal:
    - Si envías destino_dir, guarda en ese directorio.
    - Si envías modulo, usa estructura global.
    """
    extension = validar_extension(file.filename)
    validar_tamano_upload(file)

    if modulo:
        destino = obtener_directorio_modulo(modulo)
    elif destino_dir:
        destino = Path(destino_dir)
        destino.mkdir(parents=True, exist_ok=True)
    else:
        raise HTTPException(status_code=400, detail="Debe indicar destino_dir o modulo.")

    if extension in IMAGE_EXTENSIONS:
        return optimizar_imagen(file=file, destino_dir=destino, formato_salida=formato_imagen)

    return guardar_documento_sin_comprimir(file=file, destino_dir=destino, extension=extension)

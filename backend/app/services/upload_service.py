from __future__ import annotations

import io
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

from app.config import settings
from app.core.file_security import IMAGE_EXTENSIONS, UploadValidation, validate_upload


TARGET_MAX_BYTES = 500 * 1024
DEFAULT_MAX_WIDTH = 1600
DEFAULT_MAX_HEIGHT = 1600
BASE_UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"


def normalizar_modulo(modulo: str) -> str:
    if not modulo:
        raise HTTPException(status_code=400, detail="El modulo de carga es obligatorio.")

    modulo_limpio = modulo.strip().lower().replace("\\", "").replace("/", "").replace("..", "")
    if not modulo_limpio:
        raise HTTPException(status_code=400, detail="Nombre de modulo invalido.")
    return modulo_limpio


def validar_extension(nombre_archivo: str) -> str:
    extension = Path(nombre_archivo or "").suffix.lower()
    allowed = {f".{item.lstrip('.').lower()}" for item in settings.ALLOWED_UPLOAD_EXTENSIONS}
    if extension not in allowed:
        raise HTTPException(status_code=400, detail=f"Extension no permitida: {extension or 'sin extension'}")
    return extension


def validar_tamano_upload(upload_file: UploadFile) -> None:
    validate_upload(upload_file)


def obtener_directorio_modulo(modulo: str) -> Path:
    destino = BASE_UPLOAD_DIR / normalizar_modulo(modulo)
    destino.mkdir(parents=True, exist_ok=True)
    return destino


def construir_url(destino_dir: Path, nombre_archivo: str) -> str:
    return f"/uploads/{destino_dir.name}/{nombre_archivo}"


def _optimizar_pdf_bytes(content: bytes) -> bytes:
    try:
        import pikepdf
        src = io.BytesIO(content)
        out = io.BytesIO()
        with pikepdf.Pdf.open(src) as pdf:
            pdf.save(out, compress_streams=True, object_stream_mode=pikepdf.ObjectStreamMode.generate, linearize=True)
        optimized = out.getvalue()
        return optimized if len(optimized) < len(content) else content
    except Exception:
        return content


def guardar_documento_sin_comprimir(
    file: UploadFile,
    destino_dir: Path,
    extension: str,
    validation: UploadValidation | None = None,
) -> dict:
    destino_dir.mkdir(parents=True, exist_ok=True)
    validado = validation or validate_upload(file)
    nombre_archivo = f"{uuid4().hex}{extension}"
    ruta = destino_dir / nombre_archivo

    content = validado.content
    if extension == ".pdf":
        content = _optimizar_pdf_bytes(content)

    ruta.write_bytes(content)

    return {
        "nombre_archivo": nombre_archivo,
        "ruta_fisica": str(ruta),
        "url": construir_url(destino_dir, nombre_archivo),
        "extension": extension,
        "mime_type": validado.mime_type,
        "tamano_bytes": ruta.stat().st_size,
        "optimizado": extension == ".pdf",
    }


def optimizar_imagen(
    file: UploadFile,
    destino_dir: Path,
    formato_salida: str = "webp",
    max_width: int = DEFAULT_MAX_WIDTH,
    max_height: int = DEFAULT_MAX_HEIGHT,
    validation: UploadValidation | None = None,
) -> dict:
    destino_dir.mkdir(parents=True, exist_ok=True)
    validado = validation or validate_upload(file)
    formato_salida = (formato_salida or "webp").lower().strip()
    extension_salida = ".webp" if formato_salida == "webp" else ".jpg"
    pil_format = "WEBP" if extension_salida == ".webp" else "JPEG"

    nombre_archivo = f"{uuid4().hex}{extension_salida}"
    ruta = destino_dir / nombre_archivo

    try:
        from io import BytesIO

        with Image.open(BytesIO(validado.content)) as img:
            img = ImageOps.exif_transpose(img)

            if img.mode in ("RGBA", "LA", "P"):
                rgba = img.convert("RGBA")
                fondo = Image.new("RGB", rgba.size, (255, 255, 255))
                fondo.paste(rgba, mask=rgba.split()[-1])
                img = fondo
            else:
                img = img.convert("RGB")

            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            for calidad in [80, 75, 70, 65, 60, 55, 50]:
                parametros = {"format": pil_format, "quality": calidad, "optimize": True}
                if pil_format == "WEBP":
                    parametros["method"] = 6
                img.save(ruta, **parametros)
                if ruta.stat().st_size <= TARGET_MAX_BYTES:
                    break

            if ruta.exists() and ruta.stat().st_size > TARGET_MAX_BYTES:
                for escala in [0.85, 0.75, 0.65, 0.55]:
                    nuevo_ancho = max(800, int(img.width * escala))
                    nuevo_alto = max(800, int(img.height * escala))
                    reducida = img.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
                    parametros = {"format": pil_format, "quality": 70, "optimize": True}
                    if pil_format == "WEBP":
                        parametros["method"] = 6
                    reducida.save(ruta, **parametros)
                    if ruta.stat().st_size <= TARGET_MAX_BYTES:
                        break

    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="El archivo no es una imagen valida.") from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error optimizando imagen.") from exc

    return {
        "nombre_archivo": nombre_archivo,
        "ruta_fisica": str(ruta),
        "url": construir_url(destino_dir, nombre_archivo),
        "extension": extension_salida,
        "mime_type": "image/webp" if extension_salida == ".webp" else "image/jpeg",
        "tamano_bytes": ruta.stat().st_size,
        "optimizado": True,
    }


def guardar_evidencia_sst(
    file: UploadFile,
    modulo: str,
    formato_imagen: str = "webp",
    max_width: int = DEFAULT_MAX_WIDTH,
    max_height: int = DEFAULT_MAX_HEIGHT,
) -> dict:
    validation = validate_upload(file)
    destino_dir = obtener_directorio_modulo(modulo)

    if validation.extension in IMAGE_EXTENSIONS:
        return optimizar_imagen(
            file=file,
            destino_dir=destino_dir,
            formato_salida=formato_imagen,
            max_width=max_width,
            max_height=max_height,
            validation=validation,
        )

    return guardar_documento_sin_comprimir(
        file=file,
        destino_dir=destino_dir,
        extension=validation.extension,
        validation=validation,
    )


def guardar_upload_optimizado(
    file: UploadFile,
    destino_dir: Optional[Path] = None,
    formato_imagen: str = "webp",
    modulo: Optional[str] = None,
) -> dict:
    validation = validate_upload(file)

    if modulo:
        destino = obtener_directorio_modulo(modulo)
    elif destino_dir:
        destino = Path(destino_dir)
        destino.mkdir(parents=True, exist_ok=True)
    else:
        raise HTTPException(status_code=400, detail="Debe indicar destino_dir o modulo.")

    if validation.extension in IMAGE_EXTENSIONS:
        return optimizar_imagen(
            file=file,
            destino_dir=destino,
            formato_salida=formato_imagen,
            validation=validation,
        )

    return guardar_documento_sin_comprimir(
        file=file,
        destino_dir=destino,
        extension=validation.extension,
        validation=validation,
    )

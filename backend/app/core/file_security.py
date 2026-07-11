from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Iterable

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from app.config import settings


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
OFFICE_ZIP_EXTENSIONS = {".docx", ".xlsx"}
OFFICE_LEGACY_EXTENSIONS = {".doc", ".xls"}
TEXT_EXTENSIONS = {".csv"}
PDF_EXTENSIONS = {".pdf"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".avi"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg"}


@dataclass(frozen=True)
class UploadValidation:
    safe_filename: str
    extension: str
    mime_type: str
    size_bytes: int
    content: bytes


def sanitize_filename(filename: str | None) -> str:
    name = Path(filename or "archivo").name.strip().replace("\x00", "")
    if not name:
        return "archivo"
    cleaned = "".join(ch for ch in name if ch.isalnum() or ch in {".", "-", "_", " "}).strip()
    return cleaned or "archivo"


def _normalize_extensions(extensions: Iterable[str] | None) -> set[str]:
    values = extensions if extensions is not None else settings.ALLOWED_UPLOAD_EXTENSIONS
    return {f".{str(item).strip().lower().lstrip('.')}" for item in values if str(item).strip()}


def _detect_mime(content: bytes, extension: str) -> str:
    head = content[:512]

    if head.startswith(b"%PDF"):
        return "application/pdf"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image/webp"
    if head.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if head.startswith(b"PK\x03\x04"):
        if extension in OFFICE_ZIP_EXTENSIONS:
            return "application/vnd.openxmlformats-officedocument"
        return "application/zip"
    if head.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        return "application/vnd.ms-office"
    if len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"WAVE":
        return "audio/wav"
    if len(head) >= 12 and head[4:8] == b"ftyp":
        return "video/quicktime" if extension == ".mov" else "video/mp4"
    if head.startswith(b"OggS"):
        return "audio/ogg"
    if head.startswith(b"ID3") or head[:2] in {b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"}:
        return "audio/mpeg"

    if extension in TEXT_EXTENSIONS:
        try:
            head.decode("utf-8")
            if b"\x00" not in head:
                return "text/csv"
        except UnicodeDecodeError:
            pass

    return "application/octet-stream"


def _validate_image_content(content: bytes) -> None:
    try:
        with Image.open(BytesIO(content)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo no es una imagen valida.") from exc


def _content_matches_extension(extension: str, mime_type: str, content: bytes) -> bool:
    if extension in IMAGE_EXTENSIONS:
        _validate_image_content(content)
        return mime_type in {"image/jpeg", "image/png", "image/webp"}
    if extension in PDF_EXTENSIONS:
        return mime_type == "application/pdf"
    if extension in OFFICE_ZIP_EXTENSIONS:
        return mime_type == "application/vnd.openxmlformats-officedocument"
    if extension in OFFICE_LEGACY_EXTENSIONS:
        return mime_type == "application/vnd.ms-office"
    if extension in TEXT_EXTENSIONS:
        return mime_type == "text/csv"
    if extension in {".mp4", ".m4v"}:
        return mime_type == "video/mp4"
    if extension == ".mov":
        return mime_type == "video/quicktime"
    if extension == ".avi":
        return True
    if extension == ".mp3":
        return mime_type == "audio/mpeg"
    if extension == ".wav":
        return mime_type == "audio/wav"
    if extension == ".ogg":
        return mime_type == "audio/ogg"
    return False


def validate_file_size(size_bytes: int | None, *, max_bytes: int | None = None) -> None:
    limit = max_bytes or int(settings.MAX_UPLOAD_SIZE_MB) * 1024 * 1024
    if size_bytes is not None and size_bytes > limit:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el tamano maximo permitido ({limit // (1024 * 1024)} MB).",
        )


def validate_upload(
    file: UploadFile,
    *,
    allowed_extensions: Iterable[str] | None = None,
    max_size_mb: int | None = None,
) -> UploadValidation:
    filename = sanitize_filename(file.filename)
    extension = Path(filename).suffix.lower()
    allowed = _normalize_extensions(allowed_extensions)

    if extension not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido: {extension or 'sin extension'}",
        )

    file.file.seek(0)
    content = file.file.read()
    file.file.seek(0)

    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo esta vacio.")

    max_bytes = int(max_size_mb or settings.MAX_UPLOAD_SIZE_MB) * 1024 * 1024
    validate_file_size(len(content), max_bytes=max_bytes)

    mime_type = _detect_mime(content, extension)
    if not _content_matches_extension(extension, mime_type, content):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El contenido del archivo no coincide con su extension.",
        )

    return UploadValidation(
        safe_filename=filename,
        extension=extension,
        mime_type=mime_type,
        size_bytes=len(content),
        content=content,
    )


def validate_upload_file(file: UploadFile) -> None:
    validate_upload(file)

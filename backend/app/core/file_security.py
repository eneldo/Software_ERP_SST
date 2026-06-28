# ============================================================
# FILE SECURITY UTILS - ERP SST PRO ENTERPRISE
# FASE 36.6 — Seguridad Enterprise Backend/Frontend
# Archivo: backend/app/core/file_security.py
# ============================================================

from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config import settings


def sanitize_filename(filename: str | None) -> str:
    """Limpia nombres de archivos para evitar path traversal."""
    name = Path(filename or "archivo").name.strip().replace("\x00", "")
    if not name:
        return "archivo"
    return "".join(ch for ch in name if ch.isalnum() or ch in {".", "-", "_", " "}).strip()


def validate_upload_file(file: UploadFile) -> None:
    """Validación base para cargas de archivos."""
    filename = sanitize_filename(file.filename)
    suffix = Path(filename).suffix.lower()
    if suffix not in settings.ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido: {suffix or 'sin extensión'}",
        )


def validate_file_size(size_bytes: int | None) -> None:
    max_bytes = int(settings.MAX_UPLOAD_SIZE_MB) * 1024 * 1024
    if size_bytes is not None and size_bytes > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el tamaño máximo permitido ({settings.MAX_UPLOAD_SIZE_MB} MB).",
        )

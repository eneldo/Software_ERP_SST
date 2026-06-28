# ============================================================
# UTILIDADES DE UPLOADS - ERP SST PRO
# FASE 36.4 — Normalización Enterprise
# ============================================================

from pathlib import Path


def ensure_upload_directories(base_dir: str, subdirs: list[str]) -> Path:
    upload_dir = Path(base_dir).resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)
    for carpeta in subdirs:
        safe_name = str(carpeta).strip().strip("/\\")
        if safe_name:
            (upload_dir / safe_name).mkdir(parents=True, exist_ok=True)
    return upload_dir

# ============================================================
# SCHEMAS AUDITORÍA INTEGRAL DE EVIDENCIAS
# ERP SST PRO ENTERPRISE
# FASE 35.4 — Auditoría Integral de Evidencias
# Archivo: backend/app/schemas/auditoria_evidencias_schema.py
# ============================================================

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class EvidenciaAuditoriaItem(BaseModel):
    id: int
    empresa_id: int | None = None
    usuario_id: int | None = None
    tipo: str | None = None
    modulo: str | None = None
    referencia_id: int | None = None
    nombre_original: str | None = None
    nombre_archivo: str | None = None
    url: str | None = None
    preview_url: str | None = None
    thumbnail_url: str | None = None
    extension: str | None = None
    mime_type: str | None = None
    tamano_bytes: int | None = None
    activo: bool | None = True
    fecha_creacion: datetime | None = None

    existe_archivo: bool = False
    existe_preview: bool = False
    existe_thumbnail: bool = False
    optimizada_webp: bool = False
    hallazgos: list[str] = []

    model_config = ConfigDict(from_attributes=True)


class EvidenciaAuditoriaResumen(BaseModel):
    total: int = 0
    activas: int = 0
    inactivas: int = 0
    imagenes: int = 0
    pdfs: int = 0
    otros: int = 0
    webp: int = 0
    sin_archivo_fisico: int = 0
    sin_preview: int = 0
    sin_thumbnail: int = 0
    con_hallazgos: int = 0
    peso_total_mb: float = 0
    modulos: dict[str, int] = {}


class EvidenciaAuditoriaResponse(BaseModel):
    resumen: EvidenciaAuditoriaResumen
    evidencias: list[EvidenciaAuditoriaItem]
    recomendaciones: list[str]


class EvidenciaHealthResponse(BaseModel):
    ok: bool
    mensaje: str
    upload_root: str
    carpetas: dict[str, bool]

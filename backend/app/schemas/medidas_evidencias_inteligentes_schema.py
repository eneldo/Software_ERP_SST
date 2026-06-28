# ============================================================
# SCHEMAS EVIDENCIAS INTELIGENTES + TRAZABILIDAD VISUAL
# ERP SST PRO
# FASE 1.1.8.7.5
# Archivo: backend/app/schemas/medidas_evidencias_inteligentes_schema.py
# ============================================================

from __future__ import annotations

from datetime import datetime, date
from pydantic import BaseModel, ConfigDict


class EvidenciaInteligenteItem(BaseModel):
    id: int
    tipo: str | None = None
    nombre_original: str | None = None
    nombre_archivo: str | None = None
    url: str | None = None
    preview_url: str | None = None
    thumbnail_url: str | None = None
    extension: str | None = None
    mime_type: str | None = None
    tamano_bytes: int | None = None
    modulo: str | None = None
    referencia_id: int | None = None
    descripcion: str | None = None
    origen_visual: str | None = None
    activo: bool | None = True
    fecha_creacion: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TrazabilidadVisualItem(BaseModel):
    orden: int
    fecha: datetime | date | None = None
    tipo: str
    titulo: str
    descripcion: str | None = None
    usuario: str | None = None
    estado: str | None = None
    icono: str | None = None
    color: str | None = None


class SemaforoEjecutivoResponse(BaseModel):
    nivel: str
    color: str
    score: int
    mensaje: str
    factores: list[str]


class EvidenciasInteligentesResponse(BaseModel):
    medida_id: int
    codigo: str
    titulo: str
    origen: str | None = None
    estado: str | None = None
    semaforo: SemaforoEjecutivoResponse
    evidencias_medida: list[EvidenciaInteligenteItem]
    evidencias_origen: list[EvidenciaInteligenteItem]
    trazabilidad_visual: list[TrazabilidadVisualItem]
    resumen: dict

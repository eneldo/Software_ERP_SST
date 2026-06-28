# ============================================================
# SCHEMAS EVIDENCIAS INTELIGENTES REPORTES SST - ERP SST PRO
# FASE 1.1.25.6
# Archivo: backend/app/schemas/reporte_evidencia_schema.py
# ============================================================

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ReporteEvidenciaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: int
    reporte_id: int
    tipo_archivo: str
    archivo_nombre: Optional[str] = None
    archivo_url: str
    archivo_original_url: Optional[str] = None
    archivo_thumbnail_url: Optional[str] = None
    mime_type: Optional[str] = None
    peso_original_bytes: Optional[int] = None
    peso_optimizado_bytes: Optional[int] = None
    extension: Optional[str] = None
    categoria_ia: Optional[str] = None
    descripcion_ia: Optional[str] = None
    origen: Optional[str] = None
    activo: bool = True
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None


class ReporteEvidenciaCreate(BaseModel):
    reporte_id: int = Field(..., gt=0)
    categoria_ia: Optional[str] = Field(default=None, max_length=80)
    descripcion_ia: Optional[str] = None


class ReporteEvidenciaDashboardResponse(BaseModel):
    total: int = 0
    imagenes: int = 0
    videos: int = 0
    pdf: int = 0
    audios: int = 0
    otros: int = 0
    peso_original_bytes: int = 0
    peso_optimizado_bytes: int = 0
    ahorro_bytes: int = 0
    ahorro_porcentaje: float = 0
    por_categoria_ia: dict[str, int] = {}
    por_tipo_archivo: dict[str, int] = {}


class ReporteTimelineItem(BaseModel):
    fecha: Optional[datetime] = None
    tipo: str
    titulo: str
    descripcion: Optional[str] = None
    icono: Optional[str] = None

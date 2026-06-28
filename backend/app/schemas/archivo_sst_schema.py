# ============================================================
# SCHEMAS ARCHIVOS SST
# FASE 2.2.1A - Gestión Documental y Evidencias PRO
# ============================================================

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ArchivoSSTResponse(BaseModel):
    id: int
    empresa_id: int
    usuario_id: Optional[int] = None
    tipo: str
    nombre_original: str
    nombre_archivo: str
    ruta: str
    url: str
    extension: Optional[str] = None
    mime_type: Optional[str] = None
    tamano_bytes: Optional[int] = None
    modulo: Optional[str] = None
    referencia_id: Optional[int] = None
    descripcion: Optional[str] = None
    activo: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True
# ============================================================
# SCHEMA HISTORIAL MODIFICACIONES NORMATIVAS
# ============================================================

from datetime import date, datetime
from typing import Optional
from pydantic import ConfigDict,  BaseModel


class MatrizLegalHistorialCreate(BaseModel):
    matriz_legal_id: int
    tipo_cambio: str
    descripcion_cambio: str
    valor_anterior: Optional[str] = None
    valor_nuevo: Optional[str] = None
    norma_anterior: Optional[str] = None
    estado_norma_anterior: Optional[str] = None
    estado_norma_nuevo: Optional[str] = None
    motivo: Optional[str] = None
    fecha_efectiva: Optional[date] = None


class MatrizLegalHistorialResponse(BaseModel):
    id: int
    matriz_legal_id: int
    empresa_id: int
    usuario_id: Optional[int] = None
    tipo_cambio: str
    descripcion_cambio: str
    valor_anterior: Optional[str] = None
    valor_nuevo: Optional[str] = None
    norma_anterior: Optional[str] = None
    estado_norma_anterior: Optional[str] = None
    estado_norma_nuevo: Optional[str] = None
    motivo: Optional[str] = None
    fecha_efectiva: Optional[date] = None
    activo: bool
    fecha_creacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

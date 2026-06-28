# ============================================================
# SCHEMAS: Biblioteca Documental SST
# Archivo: backend/app/schemas/biblioteca_documental_schema.py
# FASE 1.8.4.3.9.2 - Centro Documental Enterprise Visual PRO
# ============================================================

from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class BibliotecaDocumentalCreate(BaseModel):
    empresa_id: int
    archivo_id: Optional[int] = None
    codigo_documental: str
    titulo: str
    categoria: str
    tipo_documento: str
    modulo_origen: Optional[str] = None
    version: str = "1.0"
    estado: str = "BORRADOR"
    estado_revision: str = "PENDIENTE"
    aprobador: Optional[str] = None
    motivo_cambio_estado: Optional[str] = None
    ultima_revision: Optional[date] = None
    proxima_revision: Optional[date] = None
    responsable: Optional[str] = None
    descripcion: Optional[str] = None
    palabras_clave: Optional[str] = None
    fecha_aprobacion: Optional[date] = None
    fecha_vencimiento: Optional[date] = None


class BibliotecaDocumentalUpdate(BaseModel):
    archivo_id: Optional[int] = None
    codigo_documental: Optional[str] = None
    titulo: Optional[str] = None
    categoria: Optional[str] = None
    tipo_documento: Optional[str] = None
    modulo_origen: Optional[str] = None
    version: Optional[str] = None
    estado: Optional[str] = None
    estado_revision: Optional[str] = None
    aprobador: Optional[str] = None
    motivo_cambio_estado: Optional[str] = None
    ultima_revision: Optional[date] = None
    proxima_revision: Optional[date] = None
    responsable: Optional[str] = None
    descripcion: Optional[str] = None
    palabras_clave: Optional[str] = None
    fecha_aprobacion: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    activo: Optional[bool] = None


class BibliotecaDocumentalResponse(BaseModel):
    id: int
    empresa_id: int
    archivo_id: Optional[int] = None
    usuario_id: Optional[int] = None

    codigo_documental: str
    titulo: str
    categoria: str
    tipo_documento: str
    modulo_origen: Optional[str] = None
    version: str
    estado: str
    estado_revision: Optional[str] = None
    aprobador: Optional[str] = None
    motivo_cambio_estado: Optional[str] = None
    ultima_revision: Optional[date] = None
    proxima_revision: Optional[date] = None
    responsable: Optional[str] = None
    descripcion: Optional[str] = None
    palabras_clave: Optional[str] = None
    fecha_aprobacion: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    activo: bool

    archivo_url: Optional[str] = None
    archivo_nombre: Optional[str] = None
    archivo_extension: Optional[str] = None
    archivo_mime_type: Optional[str] = None

    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True

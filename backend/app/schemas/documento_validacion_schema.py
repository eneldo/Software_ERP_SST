# ============================================================
# SCHEMAS
# DOCUMENTOS VALIDACIÓN SST
# FASE 1.7.4.2.5.3
# Portal de Verificación Documental Enterprise PRO
# ============================================================

from datetime import datetime
from typing import Optional

from pydantic import ConfigDict,  BaseModel


class DocumentoValidacionResponse(BaseModel):
    id: int
    codigo_validacion: str
    tipo_documento: str
    referencia_id: int

    empresa_id: Optional[int] = None
    usuario_id: Optional[int] = None

    nombre_archivo: Optional[str] = None
    hash_sha256: str
    url_archivo: Optional[str] = None

    estado: str
    observacion: Optional[str] = None

    fecha_generacion: datetime
    fecha_anulacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentoValidacionPublicResponse(BaseModel):
    codigo_validacion: str
    tipo_documento: str
    referencia_id: int

    empresa_id: Optional[int] = None
    empresa_nombre: Optional[str] = None
    empresa_nit: Optional[str] = None
    empresa_logo: Optional[str] = None

    usuario_id: Optional[int] = None
    nombre_archivo: Optional[str] = None
    hash_sha256: str
    url_archivo: Optional[str] = None

    estado: str
    observacion: Optional[str] = None

    fecha_generacion: datetime
    fecha_anulacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

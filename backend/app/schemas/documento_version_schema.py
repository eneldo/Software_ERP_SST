# ============================================================
# SCHEMAS: DocumentoVersion
# Archivo: backend/app/schemas/documento_version_schema.py
# FASE 1.8.4.3.9 - Centro de Control Documental SST Enterprise
# ============================================================

from datetime import datetime
from typing import Optional

from pydantic import ConfigDict,  BaseModel, Field


class DocumentoVersionBase(BaseModel):
    documento_id: int = Field(..., description="ID del documento en biblioteca_documental")
    version: str = Field(..., max_length=20)
    descripcion_cambio: Optional[str] = None
    usuario: Optional[str] = None
    archivo_url: Optional[str] = None


class DocumentoVersionCreate(DocumentoVersionBase):
    pass


class DocumentoVersionResponse(DocumentoVersionBase):
    id: int
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)

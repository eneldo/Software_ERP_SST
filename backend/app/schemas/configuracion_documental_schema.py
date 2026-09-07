# ============================================================
# SCHEMAS CONFIGURACIÓN DOCUMENTAL
# FASE 2.2.1B - Configuración Documental y Firmas PRO
# ============================================================

from typing import Optional
from datetime import datetime
from pydantic import ConfigDict,  BaseModel


class ConfiguracionDocumentalCreate(BaseModel):
    empresa_id: int
    logo_url: Optional[str] = None
    firma_representante_url: Optional[str] = None
    firma_sst_url: Optional[str] = None
    sello_url: Optional[str] = None
    prefijo_documental: str = "SGSST"
    version_documental: str = "1.0"
    pie_documental: Optional[str] = "Documento controlado generado desde ERP SST PRO."


class ConfiguracionDocumentalUpdate(BaseModel):
    logo_url: Optional[str] = None
    firma_representante_url: Optional[str] = None
    firma_sst_url: Optional[str] = None
    sello_url: Optional[str] = None
    prefijo_documental: Optional[str] = None
    version_documental: Optional[str] = None
    pie_documental: Optional[str] = None


class ConfiguracionDocumentalResponse(BaseModel):
    id: int
    empresa_id: int
    logo_url: Optional[str] = None
    firma_representante_url: Optional[str] = None
    firma_sst_url: Optional[str] = None
    sello_url: Optional[str] = None
    prefijo_documental: str
    version_documental: str
    pie_documental: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

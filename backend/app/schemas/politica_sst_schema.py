# ============================================================
# SCHEMAS POLÍTICA SST
# FASE 2.1 - PLANEAR SG-SST PRO
# ============================================================

from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class PoliticaSSTCreate(BaseModel):
    empresa_id: int
    titulo: str
    contenido: str
    version: str = "1.0"
    estado: str = "BORRADOR"
    responsable_sst: Optional[str] = None
    representante_legal: Optional[str] = None
    fecha_aprobacion: Optional[date] = None
    fecha_vigencia: Optional[date] = None
    observaciones: Optional[str] = None
    divulgada_copasst: bool = False
    tiene_acta_divulgacion: bool = False


class PoliticaSSTUpdate(BaseModel):
    titulo: Optional[str] = None
    contenido: Optional[str] = None
    version: Optional[str] = None
    estado: Optional[str] = None
    responsable_sst: Optional[str] = None
    representante_legal: Optional[str] = None
    fecha_aprobacion: Optional[date] = None
    fecha_vigencia: Optional[date] = None
    observaciones: Optional[str] = None
    activo: Optional[bool] = None
    divulgada_copasst: Optional[bool] = None
    tiene_acta_divulgacion: Optional[bool] = None


class PoliticaSSTResponse(BaseModel):
    id: int
    empresa_id: int
    titulo: str
    contenido: str
    version: str
    estado: str
    responsable_sst: Optional[str] = None
    representante_legal: Optional[str] = None
    fecha_aprobacion: Optional[date] = None
    fecha_vigencia: Optional[date] = None
    observaciones: Optional[str] = None
    activo: bool
    divulgada_copasst: bool
    tiene_acta_divulgacion: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True
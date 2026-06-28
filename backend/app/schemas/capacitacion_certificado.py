# ============================================================
# SCHEMAS: CERTIFICADOS DE CAPACITACIÓN SST
# FASE 2.7.4 - HARDENING ENTERPRISE CAPACITACIONES SST
# ============================================================

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class CapacitacionCertificadoCreate(BaseModel):
    capacitacion_id: int
    asistente_id: int
    archivo_pdf: Optional[str] = None


class CapacitacionCertificadoResponse(BaseModel):
    id: int
    capacitacion_id: int
    asistente_id: int
    archivo_pdf: Optional[str] = None
    fecha_generacion: Optional[datetime] = None
    activo: bool

    class Config:
        from_attributes = True

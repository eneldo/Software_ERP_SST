# ============================================================
# SCHEMAS
# FIRMA ELECTRÓNICA SST ENTERPRISE
# FASE 1.7.4.2.4
# ============================================================

from datetime import datetime
from typing import Optional

from pydantic import ConfigDict,  BaseModel


class FirmaDigitalResponse(BaseModel):
    id: int
    usuario_id: int

    nombre_firmante: str
    cargo: Optional[str] = None
    tipo_firma: str

    archivo: str
    url: str
    mime_type: Optional[str] = None
    tamano_bytes: int

    activo: bool

    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

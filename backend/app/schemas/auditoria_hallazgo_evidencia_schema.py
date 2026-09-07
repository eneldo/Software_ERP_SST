# ============================================================
# SCHEMAS
# EVIDENCIAS FOTOGRÁFICAS HALLAZGOS AUDITORÍA SST
# FASE 1.7.4.2.2
# ============================================================

from datetime import datetime
from typing import Optional

from pydantic import ConfigDict,  BaseModel


class AuditoriaHallazgoEvidenciaResponse(BaseModel):
    id: int

    hallazgo_id: int
    auditoria_id: int
    empresa_id: int
    usuario_id: Optional[int] = None

    tipo: str
    descripcion: Optional[str] = None

    nombre_original: Optional[str] = None
    archivo: str
    url: str
    extension: Optional[str] = None
    mime_type: Optional[str] = None
    tamano_bytes: int

    activo: bool

    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

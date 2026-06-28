# ============================================================
# SCHEMAS
# PLAN MEJORAMIENTO SST - EVIDENCIAS
# FASE 1.5.7
# ============================================================

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ============================================================
# CREAR
# ============================================================

class PlanMejoramientoEvidenciaCreate(BaseModel):
    plan_id: int

    empresa_id: int

    tipo_evidencia: str = "CIERRE"

    descripcion: Optional[str] = None


# ============================================================
# RESPUESTA
# ============================================================

class PlanMejoramientoEvidenciaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    plan_id: int

    empresa_id: int

    usuario_id: Optional[int]

    archivo_id: Optional[int]

    tipo_evidencia: Optional[str]

    descripcion: Optional[str]

    url: Optional[str]

    nombre_original: Optional[str]

    extension: Optional[str]

    mime_type: Optional[str]

    tamano_bytes: Optional[int]

    activo: bool

    fecha_creacion: Optional[datetime]

    fecha_actualizacion: Optional[datetime]
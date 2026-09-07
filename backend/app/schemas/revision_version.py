# ============================================================
# ERP SST PRO ENTERPRISE
# MÓDULO: VERSIONADO DOCUMENTAL
# ARCHIVO: revision_version.py
#
# Schemas para:
# - Historial documental
# - Comparación de versiones
# - Restauración
# - Auditoría documental
#
# FASE 1.8.4.3
# ============================================================

from datetime import datetime
from typing import Optional

from pydantic import ConfigDict,  BaseModel


# ============================================================
# RESPONSE VERSION
# ============================================================

class RevisionVersionResponse(BaseModel):

    id: int

    revision_id: int

    version_numero: int

    codigo_version: str

    usuario_id: Optional[int] = None

    accion: str

    hash_sha256: Optional[str] = None

    observacion: Optional[str] = None

    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# RESPONSE DETALLE
# ============================================================

class RevisionVersionDetalleResponse(
    RevisionVersionResponse
):

    datos_json: dict


# ============================================================
# RESTAURAR
# ============================================================

class RestaurarVersionRequest(BaseModel):

    observacion: Optional[str] = (
        "Restauración documental"
    )


# ============================================================
# COMPARACIÓN
# ============================================================

class ComparacionVersionResponse(BaseModel):

    version_origen: int

    version_destino: int

    diferencias: dict
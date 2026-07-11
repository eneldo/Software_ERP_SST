from __future__ import annotations

from fastapi import APIRouter, Depends

from app.auth.dependencies import require_roles
from app.core.metrics import metrics_payload


router = APIRouter(prefix="/observabilidad", tags=["Observabilidad"])

OBSERVABILIDAD_ROLES = require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])


@router.get("/metricas")
def obtener_metricas(usuario=Depends(OBSERVABILIDAD_ROLES)):
    return metrics_payload()

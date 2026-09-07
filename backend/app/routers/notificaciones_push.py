# ============================================================
# ROUTER NOTIFICACIONES PUSH
# H-035: Endpoints para suscripción y envío de push
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.usuario import Usuario
from app.models.push_subscription import PushSubscriptionModel

router = APIRouter(
    prefix="/notificaciones-push",
    tags=["H-035: Notificaciones Push"],
)

ROLES_SST = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "COORDINADOR_SST"]


class PushSubscriptionRequest(BaseModel):
    endpoint: str
    keys: dict = {}


@router.post("/suscribir")
def suscribir_push(
    data: PushSubscriptionRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    from app.services.notificaciones_push_service import guardar_suscripcion
    resultado = guardar_suscripcion(db, usuario.empresa_id, usuario.id, data.model_dump())
    return resultado


@router.post("/desuscribir")
def desuscribir_push(
    data: dict,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    from app.services.notificaciones_push_service import eliminar_suscripcion
    endpoint = data.get("endpoint", "")
    if not endpoint:
        raise HTTPException(status_code=400, detail="Endpoint requerido")
    return eliminar_suscripcion(db, endpoint)


@router.get("/mis-suscripciones")
def mis_suscripciones(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    subs = (
        db.query(PushSubscriptionModel)
        .filter(
            PushSubscriptionModel.usuario_id == usuario.id,
            PushSubscriptionModel.activo == True,
        )
        .all()
    )
    return {"total": len(subs), "suscripciones": [{"id": s.id, "endpoint": s.endpoint[:80] + "..."} for s in subs]}


@router.post("/enviar/{usuario_id}")
def enviar_push_usuario(
    usuario_id: int,
    data: dict,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles(ROLES_SST)),
):
    from app.services.notificaciones_push_service import notificar_push
    titulo = data.get("titulo", "ERP SST PRO")
    cuerpo = data.get("cuerpo", "")
    url = data.get("url", "/")
    return notificar_push(db, usuario_id, titulo, cuerpo, url)

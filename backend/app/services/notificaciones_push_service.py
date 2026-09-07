# ============================================================
# SERVICIO NOTIFICACIONES PUSH (Web Push)
# H-035: Notificaciones push para el navegador
# ============================================================

import json
import logging
from sqlalchemy.orm import Session

from app.models.notificacion_sst import NotificacionSST

logger = logging.getLogger("app.notificaciones_push")


class PushSubscription:
    def __init__(self, endpoint: str, keys: dict):
        self.endpoint = endpoint
        self.keys = keys


def guardar_suscripcion(db: Session, empresa_id: int, usuario_id: int, subscription: dict) -> dict:
    """Guarda suscripción push del navegador."""
    endpoint = subscription.get("endpoint", "")
    keys = subscription.get("keys", {})

    existe = (
        db.query(PushSubscriptionModel)
        .filter(
            PushSubscriptionModel.endpoint == endpoint,
            PushSubscriptionModel.usuario_id == usuario_id,
        )
        .first()
    )

    if existe:
        existe.p256dh = keys.get("p256dh", "")
        existe.auth = keys.get("auth", "")
        db.commit()
        return {"ok": True, "mensaje": "Suscripción actualizada"}

    sub = PushSubscriptionModel(
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        endpoint=endpoint,
        p256dh=keys.get("p256dh", ""),
        auth=keys.get("auth", ""),
        activo=True,
    )
    db.add(sub)
    db.commit()
    return {"ok": True, "mensaje": "Suscripción registrada"}


def eliminar_suscripcion(db: Session, endpoint: str) -> dict:
    """Elimina suscripción push."""
    sub = db.query(PushSubscriptionModel).filter(PushSubscriptionModel.endpoint == endpoint).first()
    if sub:
        sub.activo = False
        db.commit()
    return {"ok": True}


def notificar_push(db: Session, usuario_id: int, titulo: str, cuerpo: str, url: str = "/") -> dict:
    """Envía notificación push a todas las suscripciones activas del usuario."""
    suscripciones = (
        db.query(PushSubscriptionModel)
        .filter(
            PushSubscriptionModel.usuario_id == usuario_id,
            PushSubscriptionModel.activo == True,
        )
        .all()
    )

    if not suscripciones:
        return {"ok": False, "mensaje": "No hay suscripciones activas"}

    payload = json.dumps({
        "title": titulo,
        "body": cuerpo,
        "url": url,
        "icon": "/logo192.png",
        "badge": "/logo192.png",
    })

    enviados = 0
    for sub in suscripciones:
        try:
            from pywebpush import webpush
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                },
                data=payload,
                ttl=60 * 60,
            )
            enviados += 1
        except Exception as ex:
            logger.warning("Push failed for subscription %s: %s", sub.id, str(ex)[:100])
            sub.activo = False

    db.commit()
    return {"ok": True, "enviados": enviados, "total": len(suscripciones)}

# ============================================================
# SERVICIO ALERTAS MATRIZ LEGAL
# H-018: Genera NotificacionSST para normas proximas a vencer
# ============================================================

from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.matriz_legal import MatrizLegalSST
from app.models.notificacion_sst import NotificacionSST


DIAS_AVISO_VENCIMIENTO = [30, 15, 7, 1]


def generar_alertas_vencimiento_legal(
    db: Session,
    empresa_id: int,
) -> list[dict]:
    hoy = date.today()
    alertas_generadas = []

    normas_proximas = (
        db.query(MatrizLegalSST)
        .filter(
            MatrizLegalSST.empresa_id == empresa_id,
            MatrizLegalSST.fecha_vencimiento != None,
            MatrizLegalSST.fecha_vencimiento >= hoy,
            MatrizLegalSST.activo == True,
        )
        .all()
    )

    for norma in normas_proximas:
        if not norma.fecha_vencimiento:
            continue

        dias_restantes = (norma.fecha_vencimiento - hoy).days

        for dias_aviso in DIAS_AVISO_VENCIMIENTO:
            if dias_restantes == dias_aviso:
                existe = (
                    db.query(NotificacionSST)
                    .filter(
                        NotificacionSST.empresa_id == empresa_id,
                        NotificacionSST.modulo == "MATRIZ_LEGAL",
                        NotificacionSST.referencia_id == norma.id,
                        NotificacionSST.titulo.contains(f"{dias_aviso} días"),
                    )
                    .first()
                )

                if not existe:
                    severidad = "ALTA" if dias_aviso <= 7 else "MEDIA" if dias_aviso <= 15 else "BAJA"

                    notif = NotificacionSST(
                        empresa_id=empresa_id,
                        modulo="MATRIZ_LEGAL",
                        referencia_id=norma.id,
                        tipo="VENCIMIENTO_NORMA",
                        titulo=f"Norma {norma.codigo} vence en {dias_aviso} días",
                        descripcion=(
                            f"La norma {norma.norma} ({norma.codigo}) "
                            f"vence el {norma.fecha_vencimiento.isoformat()}. "
                            f"Responsable: {norma.responsable or 'No asignado'}. "
                            f"Estado cumplimiento: {norma.estado_cumplimiento}."
                        ),
                        prioridad=severidad,
                        estado="PENDIENTE",
                    )
                    db.add(notif)
                    alertas_generadas.append({
                        "norma_id": norma.id,
                        "codigo": norma.codigo,
                        "norma": norma.norma,
                        "fecha_vencimiento": norma.fecha_vencimiento.isoformat(),
                        "dias_restantes": dias_restantes,
                        "severidad": severidad,
                    })

    normas_vencidas = (
        db.query(MatrizLegalSST)
        .filter(
            MatrizLegalSST.empresa_id == empresa_id,
            MatrizLegalSST.fecha_vencimiento != None,
            MatrizLegalSST.fecha_vencimiento < hoy,
            MatrizLegalSST.activo == True,
        )
        .all()
    )

    for norma in normas_vencidas:
        existe = (
            db.query(NotificacionSST)
            .filter(
                NotificacionSST.empresa_id == empresa_id,
                NotificacionSST.modulo == "MATRIZ_LEGAL",
                NotificacionSST.referencia_id == norma.id,
                NotificacionSST.tipo == "NORMA_VENCIDA",
            )
            .first()
        )

        if not existe:
            notif = NotificacionSST(
                empresa_id=empresa_id,
                modulo="MATRIZ_LEGAL",
                referencia_id=norma.id,
                tipo="NORMA_VENCIDA",
                titulo=f"Norma {norma.codigo} VENCIDA",
                descripcion=(
                    f"La norma {norma.norma} ({norma.codigo}) "
                    f"venció el {norma.fecha_vencimiento.isoformat()}. "
                    f"Requiere atención inmediata."
                ),
                prioridad="ALTA",
                estado="PENDIENTE",
            )
            db.add(notif)
            alertas_generadas.append({
                "norma_id": norma.id,
                "codigo": norma.codigo,
                "norma": norma.norma,
                "fecha_vencimiento": norma.fecha_vencimiento.isoformat(),
                "dias_restantes": -1,
                "severidad": "ALTA",
            })

    if alertas_generadas:
        db.commit()

    return alertas_generadas


def contar_alertas_activas(db: Session, empresa_id: int) -> dict:
    total_pendientes = (
        db.query(func.count(NotificacionSST.id))
        .filter(
            NotificacionSST.empresa_id == empresa_id,
            NotificacionSST.modulo == "MATRIZ_LEGAL",
            NotificacionSST.estado == "PENDIENTE",
        )
        .scalar()
    )

    criticas = (
        db.query(func.count(NotificacionSST.id))
        .filter(
            NotificacionSST.empresa_id == empresa_id,
            NotificacionSST.modulo == "MATRIZ_LEGAL",
            NotificacionSST.estado == "PENDIENTE",
            NotificacionSST.prioridad == "ALTA",
        )
        .scalar()
    )

    return {
        "total_pendientes": total_pendientes,
        "criticas": criticas,
    }

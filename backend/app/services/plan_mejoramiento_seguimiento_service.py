from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.plan_mejoramiento import PlanMejoramientoSST
from app.models.plan_mejoramiento_seguimiento import PlanMejoramientoSeguimientoSST


def normalizar_avance(valor):
    try:
        avance = int(valor or 0)
    except Exception:
        avance = 0

    if avance < 0:
        return 0

    if avance > 100:
        return 100

    return avance


def obtener_plan_o_404(db: Session, plan_id: int):
    plan = (
        db.query(PlanMejoramientoSST)
        .filter(
            PlanMejoramientoSST.id == plan_id,
            PlanMejoramientoSST.activo == True,
        )
        .first()
    )

    if not plan:
        raise HTTPException(status_code=404, detail="Plan de mejoramiento no encontrado")

    return plan


def obtener_seguimiento_o_404(db: Session, seguimiento_id: int):
    seguimiento = (
        db.query(PlanMejoramientoSeguimientoSST)
        .filter(
            PlanMejoramientoSeguimientoSST.id == seguimiento_id,
            PlanMejoramientoSeguimientoSST.activo == True,
        )
        .first()
    )

    if not seguimiento:
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado")

    return seguimiento


def crear_seguimiento_plan(db: Session, plan_id: int, usuario_id: int, data):
    plan = obtener_plan_o_404(db, plan_id)

    estado_anterior = plan.estado
    avance_anterior = int(plan.porcentaje_avance or 0)

    estado_nuevo = data.estado_nuevo or plan.estado
    avance_nuevo = (
        normalizar_avance(data.porcentaje_avance_nuevo)
        if data.porcentaje_avance_nuevo is not None
        else avance_anterior
    )

    seguimiento = PlanMejoramientoSeguimientoSST(
        plan_id=plan.id,
        empresa_id=plan.empresa_id,
        usuario_id=usuario_id,
        fecha_seguimiento=data.fecha_seguimiento or date.today(),
        tipo_seguimiento=data.tipo_seguimiento or "SEGUIMIENTO",
        estado_anterior=estado_anterior,
        estado_nuevo=estado_nuevo,
        porcentaje_avance_anterior=avance_anterior,
        porcentaje_avance_nuevo=avance_nuevo,
        observacion=data.observacion,
        recomendacion=data.recomendacion,
        proxima_fecha=data.proxima_fecha,
        activo=True,
    )

    plan.estado = estado_nuevo
    plan.porcentaje_avance = avance_nuevo

    if avance_nuevo >= 100:
        plan.estado = "FINALIZADO"
        plan.porcentaje_avance = 100
        if not plan.fecha_cierre:
            plan.fecha_cierre = date.today()

    if plan.estado == "FINALIZADO":
        plan.porcentaje_avance = 100
        if not plan.fecha_cierre:
            plan.fecha_cierre = date.today()

    db.add(seguimiento)
    db.commit()
    db.refresh(seguimiento)

    return seguimiento


def listar_seguimientos_plan(db: Session, plan_id: int):
    obtener_plan_o_404(db, plan_id)

    return (
        db.query(PlanMejoramientoSeguimientoSST)
        .filter(
            PlanMejoramientoSeguimientoSST.plan_id == plan_id,
            PlanMejoramientoSeguimientoSST.activo == True,
        )
        .order_by(PlanMejoramientoSeguimientoSST.id.desc())
        .all()
    )


def eliminar_seguimiento(db: Session, seguimiento_id: int):
    seguimiento = obtener_seguimiento_o_404(db, seguimiento_id)

    seguimiento.activo = False
    db.commit()

    return {"mensaje": "Seguimiento eliminado correctamente"}
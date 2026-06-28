# ============================================================
# SERVICE
# PLAN DE MEJORAMIENTO SST INTELIGENTE
# FASE 1.5.2
# ERP SST PRO
# ============================================================

from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.plan_mejoramiento import PlanMejoramientoSST
from app.models.plan_mejoramiento_seguimiento import PlanMejoramientoSeguimientoSST

from app.models.evaluacion_inicial import (
    EvaluacionInicialSST,
    EvaluacionInicialItemSST,
)


# ============================================================
# CONSTANTES OFICIALES DEL MÓDULO
# ============================================================

ESTADO_PENDIENTE = "PENDIENTE"
ESTADO_EN_PROCESO = "EN_PROCESO"
ESTADO_VENCIDO = "VENCIDO"
ESTADO_FINALIZADO = "FINALIZADO"

PRIORIDAD_ALTA = "ALTA"
PRIORIDAD_MEDIA = "MEDIA"
PRIORIDAD_BAJA = "BAJA"


# ============================================================
# UTILIDADES
# ============================================================

def normalizar_texto(valor: str | None, defecto: str = "") -> str:
    if valor is None:
        return defecto

    texto = str(valor).strip()

    if not texto:
        return defecto

    return texto


def normalizar_prioridad(prioridad: str | None) -> str:
    valor = normalizar_texto(prioridad, PRIORIDAD_MEDIA).upper()

    if valor not in [PRIORIDAD_ALTA, PRIORIDAD_MEDIA, PRIORIDAD_BAJA]:
        return PRIORIDAD_MEDIA

    return valor


def normalizar_estado(estado: str | None) -> str:
    valor = normalizar_texto(estado, ESTADO_PENDIENTE).upper()

    if valor not in [
        ESTADO_PENDIENTE,
        ESTADO_EN_PROCESO,
        ESTADO_VENCIDO,
        ESTADO_FINALIZADO,
    ]:
        return ESTADO_PENDIENTE

    return valor


def normalizar_avance(valor: int | None) -> int:
    try:
        avance = int(valor or 0)
    except Exception:
        avance = 0

    if avance < 0:
        return 0

    if avance > 100:
        return 100

    return avance


def calcular_codigo_plan(db: Session) -> str:
    ultimo = (
        db.query(PlanMejoramientoSST)
        .order_by(PlanMejoramientoSST.id.desc())
        .first()
    )

    siguiente = 1

    if ultimo:
        siguiente = int(ultimo.id or 0) + 1

    return f"PM-SST-{siguiente:04d}"


def calcular_prioridad_item(item: EvaluacionInicialItemSST) -> str:
    texto = f"{item.estandar or ''} {item.criterio or ''}".lower()

    palabras_alta = [
        "peligro",
        "riesgo",
        "emergencia",
        "accidente",
        "incidente",
        "médica",
        "medica",
        "salud",
        "seguridad social",
        "legal",
        "normatividad",
        "matriz",
        "plan de emergencia",
    ]

    if any(palabra in texto for palabra in palabras_alta):
        return PRIORIDAD_ALTA

    return PRIORIDAD_MEDIA


def calcular_fecha_compromiso(prioridad: str) -> date:
    hoy = date.today()

    if prioridad == PRIORIDAD_ALTA:
        return hoy + timedelta(days=15)

    if prioridad == PRIORIDAD_MEDIA:
        return hoy + timedelta(days=30)

    return hoy + timedelta(days=60)


def actualizar_estado_por_fecha(plan: PlanMejoramientoSST) -> PlanMejoramientoSST:
    if plan.estado == ESTADO_FINALIZADO:
        plan.porcentaje_avance = 100
        return plan

    if plan.fecha_compromiso and plan.fecha_compromiso < date.today():
        plan.estado = ESTADO_VENCIDO

    return plan


def aplicar_estado_y_avance(plan: PlanMejoramientoSST) -> PlanMejoramientoSST:
    plan.prioridad = normalizar_prioridad(plan.prioridad)
    plan.estado = normalizar_estado(plan.estado)
    plan.porcentaje_avance = normalizar_avance(plan.porcentaje_avance)

    if plan.porcentaje_avance >= 100:
        plan.estado = ESTADO_FINALIZADO
        if not plan.fecha_cierre:
            plan.fecha_cierre = date.today()

    if plan.estado == ESTADO_FINALIZADO:
        plan.porcentaje_avance = 100
        if not plan.fecha_cierre:
            plan.fecha_cierre = date.today()

    if plan.estado == ESTADO_EN_PROCESO and plan.porcentaje_avance == 0:
        plan.porcentaje_avance = 10

    actualizar_estado_por_fecha(plan)

    return plan


# ============================================================
# SERIALIZACIÓN
# ============================================================

def serializar_plan(plan: PlanMejoramientoSST) -> dict:
    return {
        "id": plan.id,
        "empresa_id": plan.empresa_id,
        "usuario_id": plan.usuario_id,
        "evaluacion_id": plan.evaluacion_id,
        "item_evaluacion_id": plan.item_evaluacion_id,
        "codigo": plan.codigo,
        "titulo": plan.titulo,
        "descripcion": plan.descripcion,
        "causa": plan.causa,
        "accion_correctiva": plan.accion_correctiva,
        "responsable": plan.responsable,
        "prioridad": plan.prioridad,
        "estado": plan.estado,
        "fecha_apertura": plan.fecha_apertura,
        "fecha_compromiso": plan.fecha_compromiso,
        "fecha_cierre": plan.fecha_cierre,
        "porcentaje_avance": plan.porcentaje_avance,
        "evidencia": plan.evidencia,
        "observaciones": plan.observaciones,
        "activo": plan.activo,
        "fecha_creacion": plan.fecha_creacion,
        "fecha_actualizacion": plan.fecha_actualizacion,
    }


# ============================================================
# CONSULTAS
# ============================================================

def obtener_plan_o_404(
    db: Session,
    plan_id: int,
) -> PlanMejoramientoSST:
    plan = (
        db.query(PlanMejoramientoSST)
        .filter(
            PlanMejoramientoSST.id == plan_id,
            PlanMejoramientoSST.activo == True,
        )
        .first()
    )

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Acción de mejoramiento no encontrada",
        )

    return plan


def listar_planes(
    db: Session,
    empresa_id: int | None = None,
    estado: str | None = None,
    prioridad: str | None = None,
    responsable: str | None = None,
    buscar: str | None = None,
):
    query = db.query(PlanMejoramientoSST).filter(
        PlanMejoramientoSST.activo == True
    )

    if empresa_id:
        query = query.filter(PlanMejoramientoSST.empresa_id == empresa_id)

    if estado:
        query = query.filter(PlanMejoramientoSST.estado == estado.upper())

    if prioridad:
        query = query.filter(PlanMejoramientoSST.prioridad == prioridad.upper())

    if responsable:
        query = query.filter(
            PlanMejoramientoSST.responsable.ilike(f"%{responsable}%")
        )

    if buscar:
        patron = f"%{buscar}%"
        query = query.filter(
            PlanMejoramientoSST.codigo.ilike(patron)
            | PlanMejoramientoSST.titulo.ilike(patron)
            | PlanMejoramientoSST.accion_correctiva.ilike(patron)
        )

    planes = query.order_by(PlanMejoramientoSST.id.desc()).all()

    for plan in planes:
        aplicar_estado_y_avance(plan)

    db.commit()

    return planes


# ============================================================
# CREACIÓN / ACTUALIZACIÓN
# ============================================================

def crear_plan_manual(
    db: Session,
    data,
    usuario_id: int | None,
) -> PlanMejoramientoSST:
    plan = PlanMejoramientoSST(
        empresa_id=data.empresa_id,
        usuario_id=usuario_id,
        evaluacion_id=data.evaluacion_id,
        item_evaluacion_id=data.item_evaluacion_id,
        codigo=calcular_codigo_plan(db),
        titulo=data.titulo,
        descripcion=data.descripcion,
        causa=data.causa,
        accion_correctiva=data.accion_correctiva,
        responsable=data.responsable,
        prioridad=normalizar_prioridad(data.prioridad),
        estado=normalizar_estado(data.estado),
        fecha_apertura=data.fecha_apertura or date.today(),
        fecha_compromiso=data.fecha_compromiso,
        fecha_cierre=data.fecha_cierre,
        porcentaje_avance=normalizar_avance(data.porcentaje_avance),
        evidencia=data.evidencia,
        observaciones=data.observaciones,
        activo=True,
    )

    if not plan.fecha_compromiso:
        plan.fecha_compromiso = calcular_fecha_compromiso(plan.prioridad)

    aplicar_estado_y_avance(plan)

    db.add(plan)
    db.commit()
    db.refresh(plan)

    return plan


def actualizar_plan(
    db: Session,
    plan_id: int,
    data,
) -> PlanMejoramientoSST:
    plan = obtener_plan_o_404(db, plan_id)

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(plan, key, value)

    aplicar_estado_y_avance(plan)

    db.commit()
    db.refresh(plan)

    return plan


def cerrar_plan(
    db: Session,
    plan_id: int,
    observaciones: str | None = None,
) -> PlanMejoramientoSST:
    plan = obtener_plan_o_404(db, plan_id)

    plan.estado = ESTADO_FINALIZADO
    plan.porcentaje_avance = 100
    plan.fecha_cierre = date.today()

    if observaciones:
        plan.observaciones = observaciones

    db.commit()
    db.refresh(plan)

    return plan


def cambiar_estado_plan(
    db: Session,
    plan_id: int,
    estado: str,
) -> PlanMejoramientoSST:
    plan = obtener_plan_o_404(db, plan_id)

    plan.estado = normalizar_estado(estado)
    aplicar_estado_y_avance(plan)

    db.commit()
    db.refresh(plan)

    return plan


def cambiar_avance_plan(
    db: Session,
    plan_id: int,
    porcentaje_avance: int,
) -> PlanMejoramientoSST:
    plan = obtener_plan_o_404(db, plan_id)

    plan.porcentaje_avance = normalizar_avance(porcentaje_avance)

    if plan.porcentaje_avance > 0 and plan.estado == ESTADO_PENDIENTE:
        plan.estado = ESTADO_EN_PROCESO

    aplicar_estado_y_avance(plan)

    db.commit()
    db.refresh(plan)

    return plan


def eliminar_plan_logico(
    db: Session,
    plan_id: int,
):
    plan = obtener_plan_o_404(db, plan_id)

    plan.activo = False
    db.commit()

    return {
        "mensaje": "Acción de mejoramiento desactivada correctamente",
    }


# ============================================================
# GENERACIÓN AUTOMÁTICA DESDE EVALUACIÓN INICIAL
# ============================================================

def accion_sugerida_para_item(item: EvaluacionInicialItemSST) -> str:
    criterio = normalizar_texto(item.criterio, "criterio evaluado")

    return (
        f"Implementar acciones correctivas para dar cumplimiento al criterio: "
        f"{criterio}"
    )


def titulo_para_item(item: EvaluacionInicialItemSST) -> str:
    numeral = normalizar_texto(item.numeral, "SIN_NUMERAL")
    estandar = normalizar_texto(item.estandar, "Estándar SST")

    return f"{numeral} - {estandar}"


def existe_plan_para_item(
    db: Session,
    item_id: int,
) -> bool:
    existe = (
        db.query(PlanMejoramientoSST)
        .filter(
            PlanMejoramientoSST.item_evaluacion_id == item_id,
            PlanMejoramientoSST.activo == True,
        )
        .first()
    )

    return existe is not None


def generar_desde_evaluacion(
    db: Session,
    evaluacion_id: int,
    usuario_id: int | None,
) -> dict:
    evaluacion = (
        db.query(EvaluacionInicialSST)
        .options(joinedload(EvaluacionInicialSST.items))
        .filter(
            EvaluacionInicialSST.id == evaluacion_id,
            EvaluacionInicialSST.activo == True,
        )
        .first()
    )

    if not evaluacion:
        raise HTTPException(
            status_code=404,
            detail="Evaluación inicial no encontrada",
        )

    items_no_cumplen = [
        item for item in evaluacion.items
        if item.activo and item.respuesta == "NO_CUMPLE"
    ]

    creados = 0
    omitidos = 0
    planes_creados = []

    for item in items_no_cumplen:
        if existe_plan_para_item(db, item.id):
            omitidos += 1
            continue

        prioridad = calcular_prioridad_item(item)
        fecha_compromiso = calcular_fecha_compromiso(prioridad)

        plan = PlanMejoramientoSST(
            empresa_id=evaluacion.empresa_id,
            usuario_id=usuario_id,
            evaluacion_id=evaluacion.id,
            item_evaluacion_id=item.id,
            codigo=calcular_codigo_plan(db),
            titulo=titulo_para_item(item),
            descripcion=item.criterio,
            causa=(
                item.observaciones
                or "Criterio marcado como NO CUMPLE en la evaluación inicial."
            ),
            accion_correctiva=accion_sugerida_para_item(item),
            responsable=item.responsable or evaluacion.responsable,
            prioridad=prioridad,
            estado=ESTADO_PENDIENTE,
            fecha_apertura=date.today(),
            fecha_compromiso=fecha_compromiso,
            porcentaje_avance=0,
            evidencia=item.evidencia,
            observaciones=None,
            activo=True,
        )

        aplicar_estado_y_avance(plan)

        db.add(plan)
        db.commit()
        db.refresh(plan)

        planes_creados.append(plan)
        creados += 1

    return {
        "mensaje": "Plan de mejoramiento generado correctamente",
        "evaluacion_id": evaluacion_id,
        "total_no_cumplen": len(items_no_cumplen),
        "creados": creados,
        "omitidos": omitidos,
        "planes": [serializar_plan(plan) for plan in planes_creados],
    }


# ============================================================
# DASHBOARD PLAN DE MEJORAMIENTO
# ============================================================

def dashboard_plan_mejoramiento(
    db: Session,
    empresa_id: int | None = None,
) -> dict:
    query = db.query(PlanMejoramientoSST).filter(
        PlanMejoramientoSST.activo == True
    )

    if empresa_id:
        query = query.filter(PlanMejoramientoSST.empresa_id == empresa_id)

    planes = query.all()

    for plan in planes:
        aplicar_estado_y_avance(plan)

    db.commit()

    total = len(planes)
    pendientes = len([p for p in planes if p.estado == ESTADO_PENDIENTE])
    en_proceso = len([p for p in planes if p.estado == ESTADO_EN_PROCESO])
    vencidas = len([p for p in planes if p.estado == ESTADO_VENCIDO])
    finalizadas = len([p for p in planes if p.estado == ESTADO_FINALIZADO])

    cumplimiento = round((finalizadas / total) * 100, 2) if total > 0 else 0

    plan_ids = [p.id for p in planes]

    seguimientos_query = db.query(PlanMejoramientoSeguimientoSST).filter(
        PlanMejoramientoSeguimientoSST.activo == True
    )

    if plan_ids:
        seguimientos_query = seguimientos_query.filter(
            PlanMejoramientoSeguimientoSST.plan_id.in_(plan_ids)
        )
    else:
        seguimientos_query = seguimientos_query.filter(False)

    seguimientos = seguimientos_query.all()

    planes_con_seguimiento = set([s.plan_id for s in seguimientos])
    acciones_con_seguimiento = len(planes_con_seguimiento)
    acciones_sin_seguimiento = max(0, total - acciones_con_seguimiento)

    hoy = date.today()

    seguimientos_proximos = len(
        [
            s
            for s in seguimientos
            if s.proxima_fecha and s.proxima_fecha >= hoy
        ]
    )

    seguimientos_vencidos = len(
        [
            s
            for s in seguimientos
            if s.proxima_fecha and s.proxima_fecha < hoy
        ]
    )

    return {
        "total_acciones": total,
        "pendientes": pendientes,
        "en_proceso": en_proceso,
        "vencidas": vencidas,
        "finalizadas": finalizadas,
        "cumplimiento": cumplimiento,
        "total_seguimientos": len(seguimientos),
        "acciones_con_seguimiento": acciones_con_seguimiento,
        "acciones_sin_seguimiento": acciones_sin_seguimiento,
        "seguimientos_proximos": seguimientos_proximos,
        "seguimientos_vencidos": seguimientos_vencidos,
    }

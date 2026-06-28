# ============================================================
# SERVICE
# AUDITORÍA SST INTELIGENTE
# FASE 1.7.3
# ERP SST PRO
# ============================================================

from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.empresa import Empresa
from app.models.auditoria_sst import AuditoriaSST, AuditoriaHallazgoSST
from app.models.plan_mejoramiento import PlanMejoramientoSST


# ============================================================
# CÓDIGOS AUTOMÁTICOS
# ============================================================

def calcular_codigo_auditoria(db: Session) -> str:
    ultimo = db.query(AuditoriaSST).order_by(AuditoriaSST.id.desc()).first()
    siguiente = int(ultimo.id or 0) + 1 if ultimo else 1
    return f"AUD-SST-{siguiente:04d}"


def calcular_codigo_hallazgo(db: Session, auditoria_id: int) -> str:
    total = (
        db.query(AuditoriaHallazgoSST)
        .filter(AuditoriaHallazgoSST.auditoria_id == auditoria_id)
        .count()
    )
    return f"HALL-{auditoria_id}-{total + 1:03d}"


# ============================================================
# VALIDACIONES
# ============================================================

def obtener_auditoria_o_404(db: Session, auditoria_id: int) -> AuditoriaSST:
    auditoria = (
        db.query(AuditoriaSST)
        .options(joinedload(AuditoriaSST.hallazgos))
        .filter(
            AuditoriaSST.id == auditoria_id,
            AuditoriaSST.activo == True,
        )
        .first()
    )

    if not auditoria:
        raise HTTPException(
            status_code=404,
            detail="Auditoría SST no encontrada",
        )

    return auditoria


def obtener_hallazgo_o_404(db: Session, hallazgo_id: int) -> AuditoriaHallazgoSST:
    hallazgo = (
        db.query(AuditoriaHallazgoSST)
        .filter(
            AuditoriaHallazgoSST.id == hallazgo_id,
            AuditoriaHallazgoSST.activo == True,
        )
        .first()
    )

    if not hallazgo:
        raise HTTPException(
            status_code=404,
            detail="Hallazgo no encontrado",
        )

    return hallazgo


# ============================================================
# RECALCULAR RESUMEN AUDITORÍA
# ============================================================

def recalcular_resumen_auditoria(db: Session, auditoria_id: int):
    auditoria = obtener_auditoria_o_404(db, auditoria_id)

    hallazgos = [h for h in auditoria.hallazgos if h.activo]

    auditoria.total_hallazgos = len(hallazgos)

    auditoria.no_conformidades = len(
        [h for h in hallazgos if h.tipo_hallazgo == "NO_CONFORMIDAD"]
    )

    auditoria.observaciones = len(
        [h for h in hallazgos if h.tipo_hallazgo == "OBSERVACION"]
    )

    auditoria.oportunidades_mejora = len(
        [h for h in hallazgos if h.tipo_hallazgo == "OPORTUNIDAD_MEJORA"]
    )

    cerrados = len([h for h in hallazgos if h.estado == "CERRADO"])

    auditoria.porcentaje_cierre = (
        round((cerrados / len(hallazgos)) * 100)
        if hallazgos
        else 0
    )

    db.commit()
    db.refresh(auditoria)

    return auditoria


# ============================================================
# CRUD AUDITORÍA
# ============================================================

def crear_auditoria(db: Session, data, usuario_id: int):
    empresa = (
        db.query(Empresa)
        .filter(Empresa.id == data.empresa_id)
        .first()
    )

    if not empresa:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada",
        )

    auditoria = AuditoriaSST(
        empresa_id=data.empresa_id,
        usuario_id=usuario_id,
        codigo=calcular_codigo_auditoria(db),
        nombre=data.nombre,
        tipo_auditoria=data.tipo_auditoria,
        estado=data.estado,
        objetivo=data.objetivo,
        alcance=data.alcance,
        criterio=data.criterio,
        auditor_lider=data.auditor_lider,
        equipo_auditor=data.equipo_auditor,
        fecha_programada=data.fecha_programada,
        fecha_inicio=data.fecha_inicio,
        fecha_cierre=data.fecha_cierre,
        conclusiones=data.conclusiones,
        recomendaciones=data.recomendaciones,
        activo=True,
    )

    db.add(auditoria)
    db.commit()
    db.refresh(auditoria)

    return auditoria


def listar_auditorias(
    db: Session,
    empresa_id: int | None = None,
    estado: str | None = None,
    buscar: str | None = None,
):
    query = (
        db.query(AuditoriaSST)
        .options(joinedload(AuditoriaSST.hallazgos))
        .filter(AuditoriaSST.activo == True)
    )

    if empresa_id:
        query = query.filter(AuditoriaSST.empresa_id == empresa_id)

    if estado:
        query = query.filter(AuditoriaSST.estado == estado)

    if buscar:
        patron = f"%{buscar}%"
        query = query.filter(
            AuditoriaSST.codigo.ilike(patron)
            | AuditoriaSST.nombre.ilike(patron)
            | AuditoriaSST.auditor_lider.ilike(patron)
        )

    return query.order_by(AuditoriaSST.id.desc()).all()


def actualizar_auditoria(db: Session, auditoria_id: int, data):
    auditoria = obtener_auditoria_o_404(db, auditoria_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(auditoria, key, value)

    db.commit()
    db.refresh(auditoria)

    return auditoria


def eliminar_auditoria(db: Session, auditoria_id: int):
    auditoria = obtener_auditoria_o_404(db, auditoria_id)

    auditoria.activo = False
    db.commit()

    return {
        "mensaje": "Auditoría desactivada correctamente"
    }


# ============================================================
# CRUD HALLAZGOS
# ============================================================

def crear_hallazgo(db: Session, auditoria_id: int, data, usuario_id: int):
    auditoria = obtener_auditoria_o_404(db, auditoria_id)

    hallazgo = AuditoriaHallazgoSST(
        auditoria_id=auditoria.id,
        empresa_id=auditoria.empresa_id,
        usuario_id=usuario_id,
        codigo=calcular_codigo_hallazgo(db, auditoria.id),
        tipo_hallazgo=data.tipo_hallazgo,
        requisito=data.requisito,
        descripcion=data.descripcion,
        evidencia=data.evidencia,
        causa=data.causa,
        accion_recomendada=data.accion_recomendada,
        responsable=data.responsable,
        fecha_compromiso=data.fecha_compromiso,
        estado=data.estado,
        activo=True,
    )

    db.add(hallazgo)
    db.commit()
    db.refresh(hallazgo)

    recalcular_resumen_auditoria(db, auditoria.id)

    return hallazgo


def actualizar_hallazgo(db: Session, hallazgo_id: int, data):
    hallazgo = obtener_hallazgo_o_404(db, hallazgo_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(hallazgo, key, value)

    db.commit()
    db.refresh(hallazgo)

    recalcular_resumen_auditoria(db, hallazgo.auditoria_id)

    return hallazgo


def eliminar_hallazgo(db: Session, hallazgo_id: int):
    hallazgo = obtener_hallazgo_o_404(db, hallazgo_id)

    auditoria_id = hallazgo.auditoria_id
    hallazgo.activo = False

    db.commit()

    recalcular_resumen_auditoria(db, auditoria_id)

    return {
        "mensaje": "Hallazgo desactivado correctamente"
    }


# ============================================================
# GENERAR PLAN DE MEJORAMIENTO DESDE HALLAZGO
# ============================================================

def generar_plan_desde_hallazgo(
    db: Session,
    hallazgo_id: int,
    usuario_id: int,
):
    hallazgo = obtener_hallazgo_o_404(db, hallazgo_id)

    if hallazgo.plan_mejoramiento_id:
        raise HTTPException(
            status_code=400,
            detail="Este hallazgo ya tiene plan de mejoramiento asociado",
        )

    prioridad = (
        "ALTA"
        if hallazgo.tipo_hallazgo == "NO_CONFORMIDAD"
        else "MEDIA"
    )

    ultimo = (
        db.query(PlanMejoramientoSST)
        .order_by(PlanMejoramientoSST.id.desc())
        .first()
    )

    siguiente = int(ultimo.id or 0) + 1 if ultimo else 1

    plan = PlanMejoramientoSST(
        empresa_id=hallazgo.empresa_id,
        usuario_id=usuario_id,
        codigo=f"PM-SST-{siguiente:04d}",
        titulo=f"Auditoría - {hallazgo.codigo}",
        descripcion=hallazgo.descripcion,
        causa=hallazgo.causa or "Hallazgo generado en auditoría SST.",
        accion_correctiva=(
            hallazgo.accion_recomendada
            or "Implementar acción correctiva para cerrar el hallazgo de auditoría."
        ),
        responsable=hallazgo.responsable,
        prioridad=prioridad,
        estado="PENDIENTE",
        fecha_apertura=date.today(),
        fecha_compromiso=(
            hallazgo.fecha_compromiso
            or date.today() + timedelta(days=30)
        ),
        porcentaje_avance=0,
        observaciones="Plan generado automáticamente desde hallazgo de auditoría SST.",
        activo=True,
    )

    db.add(plan)
    db.commit()
    db.refresh(plan)

    hallazgo.plan_mejoramiento_id = plan.id

    db.commit()
    db.refresh(hallazgo)

    recalcular_resumen_auditoria(db, hallazgo.auditoria_id)

    return {
        "mensaje": "Plan de mejoramiento generado desde hallazgo",
        "hallazgo_id": hallazgo.id,
        "plan_mejoramiento_id": plan.id,
        "codigo_plan": plan.codigo,
    }


# ============================================================
# DASHBOARD EJECUTIVO AUDITORÍAS + HALLAZGOS
# FASE 1.7.3
# ============================================================

def dashboard_auditorias(
    db: Session,
    empresa_id: int | None = None,
):
    query = (
        db.query(AuditoriaSST)
        .options(joinedload(AuditoriaSST.hallazgos))
        .filter(AuditoriaSST.activo == True)
    )

    if empresa_id:
        query = query.filter(AuditoriaSST.empresa_id == empresa_id)

    auditorias = query.all()

    total = len(auditorias)

    programadas = len(
        [a for a in auditorias if a.estado == "PROGRAMADA"]
    )

    en_proceso = len(
        [a for a in auditorias if a.estado == "EN_PROCESO"]
    )

    cerradas = len(
        [a for a in auditorias if a.estado == "CERRADA"]
    )

    hallazgos = []

    for auditoria in auditorias:
        hallazgos.extend(
            [h for h in auditoria.hallazgos if h.activo]
        )

    total_hallazgos = len(hallazgos)

    no_conformidades = len(
        [h for h in hallazgos if h.tipo_hallazgo == "NO_CONFORMIDAD"]
    )

    observaciones = len(
        [h for h in hallazgos if h.tipo_hallazgo == "OBSERVACION"]
    )

    oportunidades = len(
        [h for h in hallazgos if h.tipo_hallazgo == "OPORTUNIDAD_MEJORA"]
    )

    hallazgos_abiertos = len(
        [h for h in hallazgos if h.estado == "ABIERTO"]
    )

    hallazgos_en_proceso = len(
        [h for h in hallazgos if h.estado == "EN_PROCESO"]
    )

    hallazgos_cerrados = len(
        [h for h in hallazgos if h.estado == "CERRADO"]
    )

    no_conformidades_abiertas = len(
        [
            h
            for h in hallazgos
            if h.tipo_hallazgo == "NO_CONFORMIDAD"
            and h.estado != "CERRADO"
        ]
    )

    planes_generados = len(
        [h for h in hallazgos if h.plan_mejoramiento_id]
    )

    planes_pendientes = max(
        0,
        total_hallazgos - planes_generados,
    )

    riesgo_alto = 0
    riesgo_medio = 0
    riesgo_bajo = 0

    for auditoria in auditorias:
        hallazgos_auditoria = [
            h for h in auditoria.hallazgos if h.activo
        ]

        nc_abiertas = len(
            [
                h
                for h in hallazgos_auditoria
                if h.tipo_hallazgo == "NO_CONFORMIDAD"
                and h.estado != "CERRADO"
            ]
        )

        abiertos = len(
            [h for h in hallazgos_auditoria if h.estado == "ABIERTO"]
        )

        en_proc = len(
            [h for h in hallazgos_auditoria if h.estado == "EN_PROCESO"]
        )

        if nc_abiertas > 0 or abiertos >= 3:
            riesgo_alto += 1
        elif abiertos > 0 or en_proc > 0:
            riesgo_medio += 1
        else:
            riesgo_bajo += 1

    porcentaje_cierre = (
        round((hallazgos_cerrados / total_hallazgos) * 100, 2)
        if total_hallazgos > 0
        else 0
    )

    cumplimiento_hallazgos = porcentaje_cierre

    return {
        "total_auditorias": total,
        "programadas": programadas,
        "en_proceso": en_proceso,
        "cerradas": cerradas,
        "total_hallazgos": total_hallazgos,
        "no_conformidades": no_conformidades,
        "observaciones": observaciones,
        "oportunidades_mejora": oportunidades,
        "hallazgos_abiertos": hallazgos_abiertos,
        "hallazgos_en_proceso": hallazgos_en_proceso,
        "hallazgos_cerrados": hallazgos_cerrados,
        "no_conformidades_abiertas": no_conformidades_abiertas,
        "planes_generados": planes_generados,
        "planes_pendientes": planes_pendientes,
        "riesgo_alto": riesgo_alto,
        "riesgo_medio": riesgo_medio,
        "riesgo_bajo": riesgo_bajo,
        "porcentaje_cierre_general": porcentaje_cierre,
        "cumplimiento_hallazgos": cumplimiento_hallazgos,
    }
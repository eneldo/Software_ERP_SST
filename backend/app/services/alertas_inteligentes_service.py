# ============================================================
# SERVICIO GENERADOR INTELIGENTE DE ALERTAS SST
# H-020: 11 dominios + plantillas + canales
# ============================================================

from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.notificacion_sst import NotificacionSST, ConfiguracionNotificacionSST
from app.models.plantilla_notificacion_sst import PlantillaNotificacionSST


DOMAINS = [
    "CAPA", "INSPECCIONES", "HALLAZGOS", "INCIDENTES",
    "EXAMENES", "EPP", "CAPACITACIONES", "AUDITORIAS",
    "PLAN_MEJORAMIENTO", "MATRIZ_LEGAL", "PORTAL_EMPLEADO",
]


def _obtener_config(db: Session, empresa_id: int) -> ConfiguracionNotificacionSST:
    config = (
        db.query(ConfiguracionNotificacionSST)
        .filter(ConfiguracionNotificacionSST.empresa_id == empresa_id)
        .first()
    )
    if not config:
        config = ConfiguracionNotificacionSST(empresa_id=empresa_id)
        db.add(config)
        db.flush()
    return config


def _crear_notificacion(
    db: Session,
    empresa_id: int,
    modulo: str,
    tipo: str,
    titulo: str,
    descripcion: str,
    prioridad: str = "MEDIA",
    referencia_id: int | None = None,
    fecha_vencimiento: date | None = None,
    accion_recomendada: str | None = None,
    url_destino: str | None = None,
) -> NotificacionSST | None:
    clave = f"{empresa_id}:{modulo}:{tipo}:{referencia_id or 'global'}"
    existe = (
        db.query(NotificacionSST)
        .filter(NotificacionSST.clave_unica == clave)
        .first()
    )
    if existe:
        return None

    notif = NotificacionSST(
        empresa_id=empresa_id,
        modulo=modulo,
        referencia_id=referencia_id,
        clave_unica=clave,
        tipo=tipo,
        prioridad=prioridad,
        estado="PENDIENTE",
        titulo=titulo,
        descripcion=descripcion,
        accion_recomendada=accion_recomendada,
        url_destino=url_destino,
        fecha_vencimiento=fecha_vencimiento,
    )
    db.add(notif)
    return notif


def _alertas_capa(db: Session, empresa_id: int) -> list[dict]:
    from app.models.capa import CapaSST

    hoy = date.today()
    alertas = []

    capas = (
        db.query(CapaSST)
        .filter(CapaSST.empresa_id == empresa_id, CapaSST.activo == True)
        .all()
    )

    for capa in capas:
        if capa.fecha_limite and capa.fecha_limite < hoy and capa.estado != "CERRADA":
            notif = _crear_notificacion(
                db, empresa_id, "CAPA", "VENCIMIENTO",
                f"CAPA {capa.codigo} vencida",
                f"La CAPA {capa.codigo} venció el {capa.fecha_limite}. Estado: {capa.estado}.",
                "ALTA", capa.id, capa.fecha_limite,
                "Verificar avance y cerrar CAPA",
            )
            if notif:
                alertas.append({"modulo": "CAPA", "tipo": "VENCIMIENTO", "id": capa.id})

    return alertas


def _alertas_inspecciones(db: Session, empresa_id: int) -> list[dict]:
    from app.models.inspeccion import InspeccionSST

    hoy = date.today()
    alertas = []

    inspecciones = (
        db.query(InspeccionSST)
        .filter(InspeccionSST.empresa_id == empresa_id, InspeccionSST.activo == True)
        .all()
    )

    for insp in inspecciones:
        if insp.fecha_limite and insp.fecha_limite < hoy and insp.estado != "CERRADA":
            notif = _crear_notificacion(
                db, empresa_id, "INSPECCIONES", "VENCIMIENTO",
                f"Inspección {insp.codigo} vencida",
                f"La inspección {insp.codigo} venció el {insp.fecha_limite}.",
                "ALTA", insp.id, insp.fecha_limite,
            )
            if notif:
                alertas.append({"modulo": "INSPECCIONES", "tipo": "VENCIMIENTO", "id": insp.id})

    return alertas


def _alertas_incidentes(db: Session, empresa_id: int) -> list[dict]:
    from app.models.incidente import IncidenteAccidenteSST

    alertas = []

    incidentes = (
        db.query(IncidenteAccidenteSST)
        .filter(
            IncidenteAccidenteSST.empresa_id == empresa_id,
            IncidenteAccidenteSST.estado_investigacion != "CERRADO",
            IncidenteAccidenteSST.activo == True,
        )
        .all()
    )

    for inc in incidentes:
        if inc.clasificacion in ("GRAVE", "MORTAL"):
            notif = _crear_notificacion(
                db, empresa_id, "INCIDENTES", "SEGUIMIENTO",
                f"Incidente grave: {inc.codigo}",
                f"El incidente {inc.codigo} requiere investigación urgente. Clasificación: {inc.clasificacion}.",
                "CRITICA", inc.id,
            )
            if notif:
                alertas.append({"modulo": "INCIDENTES", "tipo": "SEGUIMIENTO", "id": inc.id})

    return alertas


def _alertas_examenes(db: Session, empresa_id: int) -> list[dict]:
    from app.models.examen_medico import ExamenMedico

    hoy = date.today()
    alertas = []

    examenes = (
        db.query(ExamenMedico)
        .filter(ExamenMedico.empresa_id == empresa_id, ExamenMedico.activo == True)
        .all()
    )

    for exam in examenes:
        if exam.fecha_proximo_examen and exam.fecha_proximo_examen <= hoy + timedelta(days=30):
            dias = (exam.fecha_proximo_examen - hoy).days
            prioridad = "ALTA" if dias <= 7 else "MEDIA"
            notif = _crear_notificacion(
                db, empresa_id, "EXAMENES", "VENCIMIENTO",
                f"Examen médico vence en {dias} días",
                f"El examen del empleado {exam.empleado_nombre} vence el {exam.fecha_proximo_examen}.",
                prioridad, exam.id, exam.fecha_proximo_examen,
            )
            if notif:
                alertas.append({"modulo": "EXAMENES", "tipo": "VENCIMIENTO", "id": exam.id})

    return alertas


def _alertas_epp(db: Session, empresa_id: int) -> list[dict]:
    from app.models.epp import EPPEntrega

    hoy = date.today()
    alertas = []

    entregas = (
        db.query(EPPEntrega)
        .filter(EPPEntrega.empresa_id == empresa_id, EPPEntrega.activo == True)
        .all()
    )

    for ent in entregas:
        if ent.fecha_proxima_reposicion and ent.fecha_proxima_reposicion <= hoy + timedelta(days=15):
            notif = _crear_notificacion(
                db, empresa_id, "EPP", "VENCIMIENTO",
                f"EPP {ent.catalogo_nombre} proximo a reponer",
                f"La entrega {ent.codigo} vence el {ent.fecha_proxima_reposicion}.",
                "MEDIA", ent.id, ent.fecha_proxima_reposicion,
            )
            if notif:
                alertas.append({"modulo": "EPP", "tipo": "VENCIMIENTO", "id": ent.id})

    return alertas


def _alertas_capacitaciones(db: Session, empresa_id: int) -> list[dict]:
    from app.models.capacitacion import CapacitacionSST

    hoy = date.today()
    alertas = []

    caps = (
        db.query(CapacitacionSST)
        .filter(
            CapacitacionSST.empresa_id == empresa_id,
            CapacitacionSST.estado == "PROGRAMADA",
            CapacitacionSST.activo == True,
        )
        .all()
    )

    for cap in caps:
        if cap.fecha_programada and cap.fecha_programada < hoy:
            notif = _crear_notificacion(
                db, empresa_id, "CAPACITACIONES", "VENCIMIENTO",
                f"Capacitación {cap.codigo} vencida",
                f"La capacitación {cap.nombre} programada para {cap.fecha_programada} no se ejecutó.",
                "ALTA", cap.id, cap.fecha_programada,
            )
            if notif:
                alertas.append({"modulo": "CAPACITACIONES", "tipo": "VENCIMIENTO", "id": cap.id})

    return alertas


def _alertas_auditorias(db: Session, empresa_id: int) -> list[dict]:
    from app.models.auditoria_sst import AuditoriaSST

    hoy = date.today()
    alertas = []

    auditorias = (
        db.query(AuditoriaSST)
        .filter(
            AuditoriaSST.empresa_id == empresa_id,
            AuditoriaSST.estado != "CERRADA",
            AuditoriaSST.activo == True,
        )
        .all()
    )

    for aud in auditorias:
        if aud.fecha_cierre_estimada and aud.fecha_cierre_estimada < hoy:
            notif = _crear_notificacion(
                db, empresa_id, "AUDITORIAS", "VENCIMIENTO",
                f"Auditoría {aud.codigo} vencida",
                f"La auditoría {aud.codigo} venció el {aud.fecha_cierre_estimada}.",
                "ALTA", aud.id, aud.fecha_cierre_estimada,
            )
            if notif:
                alertas.append({"modulo": "AUDITORIAS", "tipo": "VENCIMIENTO", "id": aud.id})

    return alertas


def _alertas_plan_mejoramiento(db: Session, empresa_id: int) -> list[dict]:
    from app.models.plan_mejoramiento import PlanMejoramientoSST

    hoy = date.today()
    alertas = []

    planes = (
        db.query(PlanMejoramientoSST)
        .filter(
            PlanMejoramientoSST.empresa_id == empresa_id,
            PlanMejoramientoSST.estado.notin_(["FINALIZADO"]),
            PlanMejoramientoSST.activo == True,
        )
        .all()
    )

    for plan in planes:
        if plan.fecha_compromiso and plan.fecha_compromiso < hoy:
            notif = _crear_notificacion(
                db, empresa_id, "PLAN_MEJORAMIENTO", "VENCIMIENTO",
                f"Plan {plan.codigo} vencido",
                f"El plan de mejoramiento {plan.codigo} venció el {plan.fecha_compromiso}.",
                "ALTA", plan.id, plan.fecha_compromiso,
            )
            if notif:
                alertas.append({"modulo": "PLAN_MEJORAMIENTO", "tipo": "VENCIMIENTO", "id": plan.id})

    return alertas


def generar_alertas_inteligentes(db: Session, empresa_id: int) -> dict:
    total_generadas = 0
    dominios_procesados = []

    generadores = [
        ("CAPA", _alertas_capa),
        ("INSPECCIONES", _alertas_inspecciones),
        ("INCIDENTES", _alertas_incidentes),
        ("EXAMENES", _alertas_examenes),
        ("EPP", _alertas_epp),
        ("CAPACITACIONES", _alertas_capacitaciones),
        ("AUDITORIAS", _alertas_auditorias),
        ("PLAN_MEJORAMIENTO", _alertas_plan_mejoramiento),
    ]

    for nombre, generador in generadores:
        try:
            alertas = generador(db, empresa_id)
            total_generadas += len(alertas)
            dominios_procesados.append({"dominio": nombre, "alertas": len(alertas)})
        except Exception as e:
            dominios_procesados.append({"dominio": nombre, "error": str(e)})

    try:
        from app.services.alertas_matriz_legal_service import generar_alertas_vencimiento_legal
        alertas_legal = generar_alertas_vencimiento_legal(db, empresa_id)
        total_generadas += len(alertas_legal)
        dominios_procesados.append({"dominio": "MATRIZ_LEGAL", "alertas": len(alertas_legal)})
    except Exception as e:
        dominios_procesados.append({"dominio": "MATRIZ_LEGAL", "error": str(e)})

    db.commit()

    return {
        "total_generadas": total_generadas,
        "dominios": dominios_procesados,
    }

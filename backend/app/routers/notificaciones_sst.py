# ============================================================
# ROUTER NOTIFICACIONES SST - ERP SST PRO
# FASE 1.1.24.1 — CENTRO DE NOTIFICACIONES INTELIGENTES SST
# Archivo: backend/app/routers/notificaciones_sst.py
# ============================================================

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.auth.dependencies import require_roles, require_permission
from app.core.default_permissions import PERM_REGISTROS_ELIMINAR
from app.database import get_db
from app.models.auditoria_sst import AuditoriaSST, AuditoriaHallazgoSST
from app.models.capa import CapaSST
from app.models.capacitacion import CapacitacionSST
from app.models.empleado import Empleado
from app.models.empresa import Empresa
from app.models.epp import EPPEntrega
from app.models.examen_medico import ExamenMedico
from app.models.incidente import IncidenteAccidenteSST
from app.models.inspeccion import InspeccionHallazgoSST, InspeccionSST
from app.models.notificacion_sst import ConfiguracionNotificacionSST, NotificacionSST
from app.models.plan_mejoramiento import PlanMejoramientoSST
from app.schemas.notificacion_sst_schema import (
    ConfiguracionNotificacionSSTCreate,
    ConfiguracionNotificacionSSTResponse,
    ConfiguracionNotificacionSSTUpdate,
    GeneracionNotificacionesResponse,
    NotificacionSSTCreate,
    NotificacionSSTResponse,
    NotificacionSSTUpdate,
    NotificacionesDashboardResponse,
)

router = APIRouter(prefix="/notificaciones", tags=["Centro de Notificaciones SST"])

ROLES_SST = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]
ROLES_ADMIN = ["SUPER_ADMIN", "ADMIN_EMPRESA"]
ELIMINAR_REGISTROS = require_permission(PERM_REGISTROS_ELIMINAR)

ESTADOS_CIERRE = ["CERRADA", "CERRADO", "FINALIZADA", "FINALIZADO", "EJECUTADA", "RESUELTO", "RESUELTA", "ANULADA", "ANULADO"]


# ============================================================
# HELPERS
# ============================================================

def _upper(value: Any, default: str | None = None) -> str | None:
    if value is None:
        return default
    txt = str(value).strip().upper()
    return txt if txt else default


def _empresa_id_autorizada(usuario, empresa_id: int | None) -> int | None:
    if str(getattr(usuario, "rol", "") or "").upper() == "SUPER_ADMIN":
        return empresa_id
    usuario_empresa_id = getattr(usuario, "empresa_id", None)
    if usuario_empresa_id is None:
        raise HTTPException(status_code=403, detail="Usuario sin empresa asignada")
    if empresa_id is not None and int(usuario_empresa_id) != int(empresa_id):
        raise HTTPException(status_code=403, detail="No tiene permisos sobre esta empresa")
    return int(usuario_empresa_id)


def _notificacion_to_response(item: NotificacionSST) -> NotificacionSSTResponse:
    data = NotificacionSSTResponse.model_validate(item)
    data.empresa_nombre = item.empresa.nombre if item.empresa else None
    data.sede_nombre = item.sede.nombre if item.sede else None
    data.area_nombre = item.area.nombre if item.area else None
    return data


def _base_query(db: Session):
    return db.query(NotificacionSST).options(
        joinedload(NotificacionSST.empresa),
        joinedload(NotificacionSST.sede),
        joinedload(NotificacionSST.area),
    )


def _crear_o_ignorar(db: Session, payload: dict) -> tuple[bool, NotificacionSST | None]:
    clave = payload.get("clave_unica")
    if clave:
        existente = db.query(NotificacionSST).filter(NotificacionSST.clave_unica == clave).first()
        if existente:
            # Si ya existe y estaba archivada, no la duplicamos. Si fue resuelta, tampoco.
            return False, existente
    item = NotificacionSST(**payload)
    db.add(item)
    return True, item


def _prioridad_por_fecha(fecha_objetivo: date | None, hoy: date, dias_alerta: int) -> str:
    if not fecha_objetivo:
        return "MEDIA"
    if fecha_objetivo < hoy:
        return "CRITICA"
    if fecha_objetivo <= hoy + timedelta(days=3):
        return "ALTA"
    if fecha_objetivo <= hoy + timedelta(days=dias_alerta):
        return "MEDIA"
    return "BAJA"


def _url(modulo: str, referencia_id: int | None = None) -> str:
    rutas = {
        "CAPA": "/hacer/capa",
        "INSPECCIONES": "/hacer/inspecciones",
        "HALLAZGOS": "/hacer/inspecciones",
        "INCIDENTES": "/hacer/incidentes",
        "EXAMENES": "/hacer/examenes-medicos",
        "EPP": "/hacer/epp",
        "CAPACITACIONES": "/hacer/capacitaciones",
        "AUDITORIAS": "/verificar/auditorias",
        "PLAN_MEJORAMIENTO": "/actuar/plan-mejoramiento",
    }
    return rutas.get(modulo, "/verificar/notificaciones")


def _empresa_config(db: Session, empresa_id: int | None):
    if not empresa_id:
        return None
    return db.query(ConfiguracionNotificacionSST).filter(
        ConfiguracionNotificacionSST.empresa_id == empresa_id,
        ConfiguracionNotificacionSST.activo.is_(True),
    ).first()


def _dias_alerta(db: Session, empresa_id: int | None, default: int = 15) -> int:
    cfg = _empresa_config(db, empresa_id)
    if cfg and cfg.habilitar_notificaciones:
        return int(cfg.dias_alerta_vencimiento or default)
    return default


def _filtro_empresa(query, model, empresa_id):
    if empresa_id and hasattr(model, "empresa_id"):
        return query.filter(model.empresa_id == empresa_id)
    return query


def _filtro_sede_area(query, model, sede_id=None, area_id=None):
    if sede_id and hasattr(model, "sede_id"):
        query = query.filter(model.sede_id == sede_id)
    if area_id and hasattr(model, "area_id"):
        query = query.filter(model.area_id == area_id)
    return query


# ============================================================
# GENERADOR INTELIGENTE
# ============================================================

def generar_alertas_inteligentes(db: Session, empresa_id: int | None = None, sede_id: int | None = None, area_id: int | None = None, usuario_id: int | None = None) -> dict:
    hoy = date.today()
    creadas = 0
    existentes = 0
    detalle = {
        "CAPA": 0,
        "INSPECCIONES": 0,
        "HALLAZGOS": 0,
        "INCIDENTES": 0,
        "EXAMENES": 0,
        "EPP": 0,
        "CAPACITACIONES": 0,
        "AUDITORIAS": 0,
        "PLAN_MEJORAMIENTO": 0,
    }

    dias_alerta = _dias_alerta(db, empresa_id, 15)
    limite = hoy + timedelta(days=dias_alerta)

    def add(payload: dict):
        nonlocal creadas, existentes
        payload.setdefault("usuario_id", usuario_id)
        payload.setdefault("origen_generacion", "AUTOMATICA")
        payload.setdefault("estado", "PENDIENTE")
        payload.setdefault("leida", False)
        payload.setdefault("archivada", False)
        payload.setdefault("activa", True)
        ok, _ = _crear_o_ignorar(db, payload)
        if ok:
            creadas += 1
            detalle[payload["modulo"]] = detalle.get(payload["modulo"], 0) + 1
        else:
            existentes += 1

    # CAPA vencidas o próximas.
    capas_q = db.query(CapaSST).filter(CapaSST.activo.is_(True))
    capas_q = _filtro_empresa(capas_q, CapaSST, empresa_id)
    capas_q = _filtro_sede_area(capas_q, CapaSST, sede_id, area_id)
    capas_q = capas_q.filter(or_(CapaSST.fecha_compromiso <= limite, CapaSST.avance < 30))
    capas_q = capas_q.filter(func.upper(CapaSST.estado).notin_(ESTADOS_CIERRE))
    for c in capas_q.all():
        prioridad = _prioridad_por_fecha(c.fecha_compromiso, hoy, dias_alerta)
        if c.prioridad and _upper(c.prioridad) in ["ALTA", "CRITICA", "CRÍTICA"] and prioridad in ["MEDIA", "BAJA"]:
            prioridad = "ALTA"
        add({
            "empresa_id": c.empresa_id,
            "sede_id": c.sede_id,
            "area_id": c.area_id,
            "modulo": "CAPA",
            "referencia_id": c.id,
            "clave_unica": f"CAPA-{c.id}-{c.estado}-{c.fecha_compromiso}",
            "tipo": "VENCIMIENTO" if c.fecha_compromiso and c.fecha_compromiso <= limite else "SEGUIMIENTO",
            "prioridad": prioridad,
            "titulo": f"CAPA pendiente: {c.codigo}",
            "descripcion": f"{c.titulo}. Estado: {c.estado}. Avance: {float(c.avance or 0):.0f}%.",
            "accion_recomendada": "Revisar responsable, registrar seguimiento y cerrar la acción si ya fue efectiva.",
            "url_destino": _url("CAPA", c.id),
            "fecha_evento": c.fecha_apertura,
            "fecha_vencimiento": c.fecha_compromiso,
        })

    # Inspecciones vencidas o próximas.
    insp_q = db.query(InspeccionSST).filter(InspeccionSST.activo.is_(True))
    insp_q = _filtro_empresa(insp_q, InspeccionSST, empresa_id)
    insp_q = _filtro_sede_area(insp_q, InspeccionSST, sede_id, area_id)
    insp_q = insp_q.filter(InspeccionSST.fecha_programada <= limite)
    insp_q = insp_q.filter(func.upper(InspeccionSST.estado).notin_(ESTADOS_CIERRE))
    for i in insp_q.all():
        add({
            "empresa_id": i.empresa_id,
            "sede_id": i.sede_id,
            "area_id": i.area_id,
            "modulo": "INSPECCIONES",
            "referencia_id": i.id,
            "clave_unica": f"INSP-{i.id}-{i.estado}-{i.fecha_programada}",
            "tipo": "VENCIMIENTO",
            "prioridad": _prioridad_por_fecha(i.fecha_programada, hoy, dias_alerta),
            "titulo": f"Inspección pendiente: {i.codigo}",
            "descripcion": f"{i.titulo}. Programada para {i.fecha_programada}. Estado: {i.estado}.",
            "accion_recomendada": "Ejecutar la inspección, registrar hallazgos y anexar evidencias.",
            "url_destino": _url("INSPECCIONES", i.id),
            "fecha_evento": i.fecha_inspeccion,
            "fecha_vencimiento": i.fecha_programada,
        })

    # Hallazgos abiertos o críticos.
    hall_q = db.query(InspeccionHallazgoSST).filter(InspeccionHallazgoSST.activo.is_(True))
    hall_q = _filtro_empresa(hall_q, InspeccionHallazgoSST, empresa_id)
    hall_q = hall_q.filter(func.upper(InspeccionHallazgoSST.estado).notin_(ESTADOS_CIERRE))
    hall_q = hall_q.filter(or_(InspeccionHallazgoSST.fecha_compromiso <= limite, func.upper(InspeccionHallazgoSST.nivel_riesgo).in_(["ALTO", "CRITICO", "CRÍTICO"])))
    for h in hall_q.all():
        riesgo = _upper(h.nivel_riesgo, "MEDIO")
        prioridad = "ALTA" if riesgo in ["ALTO", "CRITICO", "CRÍTICO"] else _prioridad_por_fecha(h.fecha_compromiso, hoy, dias_alerta)
        add({
            "empresa_id": h.empresa_id,
            "modulo": "HALLAZGOS",
            "referencia_id": h.id,
            "clave_unica": f"HALL-INSP-{h.id}-{h.estado}-{h.fecha_compromiso}",
            "tipo": "SEGUIMIENTO",
            "prioridad": prioridad,
            "titulo": f"Hallazgo de inspección abierto #{h.id}",
            "descripcion": h.descripcion,
            "accion_recomendada": "Asignar seguimiento, evidencia y fecha de cierre del hallazgo.",
            "url_destino": _url("HALLAZGOS", h.id),
            "fecha_evento": h.fecha_creacion.date() if h.fecha_creacion else None,
            "fecha_vencimiento": h.fecha_compromiso,
        })

    # Incidentes/Accidentes abiertos, graves o con investigación pendiente.
    inc_q = db.query(IncidenteAccidenteSST).filter(IncidenteAccidenteSST.activo.is_(True))
    inc_q = _filtro_empresa(inc_q, IncidenteAccidenteSST, empresa_id)
    inc_q = _filtro_sede_area(inc_q, IncidenteAccidenteSST, sede_id, area_id)
    inc_q = inc_q.filter(or_(
        func.upper(IncidenteAccidenteSST.estado).notin_(ESTADOS_CIERRE),
        IncidenteAccidenteSST.investigacion_cerrada.is_(False),
        func.upper(IncidenteAccidenteSST.severidad).in_(["ALTA", "GRAVE", "CRITICA", "CRÍTICA"]),
    ))
    for ev in inc_q.all():
        severidad = _upper(ev.severidad, "BAJA")
        prioridad = "CRITICA" if severidad in ["GRAVE", "CRITICA", "CRÍTICA"] else "ALTA" if _upper(ev.tipo_evento) == "ACCIDENTE" else "MEDIA"
        add({
            "empresa_id": ev.empresa_id,
            "sede_id": ev.sede_id,
            "area_id": ev.area_id,
            "modulo": "INCIDENTES",
            "referencia_id": ev.id,
            "clave_unica": f"INC-{ev.id}-{ev.estado}-{ev.estado_investigacion}",
            "tipo": "SEGUIMIENTO",
            "prioridad": prioridad,
            "titulo": f"Evento SST abierto: {ev.codigo}",
            "descripcion": f"{ev.titulo}. Tipo: {ev.tipo_evento}. Severidad: {ev.severidad}. Investigación: {ev.estado_investigacion}.",
            "accion_recomendada": "Cerrar investigación, documentar causas, registrar testigos/lesionados y generar CAPA si aplica.",
            "url_destino": _url("INCIDENTES", ev.id),
            "fecha_evento": ev.fecha_evento,
            "fecha_vencimiento": ev.fecha_investigacion,
        })

    # Exámenes médicos vencidos o próximos. Se filtra por empresa vía empleado.
    ex_q = db.query(ExamenMedico).join(Empleado, Empleado.id == ExamenMedico.empleado_id).filter(ExamenMedico.activo.is_(True))
    if empresa_id:
        ex_q = ex_q.filter(Empleado.empresa_id == empresa_id)
    if sede_id:
        ex_q = ex_q.filter(Empleado.sede_id == sede_id)
    if area_id:
        ex_q = ex_q.filter(Empleado.area_id == area_id)
    ex_q = ex_q.filter(ExamenMedico.fecha_vencimiento <= limite)
    for ex in ex_q.all():
        emp = ex.empleado
        add({
            "empresa_id": getattr(emp, "empresa_id", None),
            "sede_id": getattr(emp, "sede_id", None),
            "area_id": getattr(emp, "area_id", None),
            "modulo": "EXAMENES",
            "referencia_id": ex.id,
            "clave_unica": f"EXAMEN-{ex.id}-{ex.fecha_vencimiento}",
            "tipo": "VENCIMIENTO",
            "prioridad": _prioridad_por_fecha(ex.fecha_vencimiento, hoy, dias_alerta),
            "titulo": f"Examen médico por vencer/vencido #{ex.id}",
            "descripcion": f"Tipo: {ex.tipo_examen}. Concepto: {ex.concepto}. Vence: {ex.fecha_vencimiento}.",
            "accion_recomendada": "Programar renovación del examen médico ocupacional y actualizar soporte documental.",
            "url_destino": _url("EXAMENES", ex.id),
            "fecha_evento": ex.fecha_examen,
            "fecha_vencimiento": ex.fecha_vencimiento,
        })

    # EPP con reposición vencida o próxima.
    epp_q = db.query(EPPEntrega).filter(EPPEntrega.activo.is_(True))
    epp_q = _filtro_empresa(epp_q, EPPEntrega, empresa_id)
    epp_q = epp_q.filter(EPPEntrega.fecha_reposicion <= limite)
    for e in epp_q.all():
        add({
            "empresa_id": e.empresa_id,
            "modulo": "EPP",
            "referencia_id": e.id,
            "clave_unica": f"EPP-{e.id}-{e.fecha_reposicion}",
            "tipo": "VENCIMIENTO",
            "prioridad": _prioridad_por_fecha(e.fecha_reposicion, hoy, dias_alerta),
            "titulo": f"Reposición EPP pendiente #{e.id}",
            "descripcion": f"EPP entregado el {e.fecha_entrega}. Reposición: {e.fecha_reposicion}. Estado: {e.estado}.",
            "accion_recomendada": "Verificar estado del EPP, registrar reposición y firma del trabajador.",
            "url_destino": _url("EPP", e.id),
            "fecha_evento": e.fecha_entrega,
            "fecha_vencimiento": e.fecha_reposicion,
        })

    # Capacitaciones programadas vencidas/próximas sin ejecutar.
    cap_q = db.query(CapacitacionSST).filter(CapacitacionSST.activo.is_(True))
    cap_q = _filtro_empresa(cap_q, CapacitacionSST, empresa_id)
    cap_q = cap_q.filter(CapacitacionSST.fecha_programada <= limite)
    cap_q = cap_q.filter(func.upper(CapacitacionSST.estado).notin_(ESTADOS_CIERRE))
    for cap in cap_q.all():
        add({
            "empresa_id": cap.empresa_id,
            "modulo": "CAPACITACIONES",
            "referencia_id": cap.id,
            "clave_unica": f"CAPACITACION-{cap.id}-{cap.estado}-{cap.fecha_programada}",
            "tipo": "VENCIMIENTO",
            "prioridad": _prioridad_por_fecha(cap.fecha_programada, hoy, dias_alerta),
            "titulo": f"Capacitación pendiente: {cap.codigo}",
            "descripcion": f"{cap.nombre}. Tema: {cap.tema}. Programada: {cap.fecha_programada}.",
            "accion_recomendada": "Ejecutar capacitación, registrar asistentes, evidencias y certificados.",
            "url_destino": _url("CAPACITACIONES", cap.id),
            "fecha_evento": cap.fecha_programada,
            "fecha_vencimiento": cap.fecha_programada,
        })

    # Auditorías programadas próximas/vencidas y hallazgos abiertos.
    aud_q = db.query(AuditoriaSST).filter(AuditoriaSST.activo.is_(True))
    aud_q = _filtro_empresa(aud_q, AuditoriaSST, empresa_id)
    aud_q = aud_q.filter(AuditoriaSST.fecha_programada <= limite)
    aud_q = aud_q.filter(func.upper(AuditoriaSST.estado).notin_(ESTADOS_CIERRE))
    for aud in aud_q.all():
        add({
            "empresa_id": aud.empresa_id,
            "modulo": "AUDITORIAS",
            "referencia_id": aud.id,
            "clave_unica": f"AUDITORIA-{aud.id}-{aud.estado}-{aud.fecha_programada}",
            "tipo": "VENCIMIENTO",
            "prioridad": _prioridad_por_fecha(aud.fecha_programada, hoy, dias_alerta),
            "titulo": f"Auditoría SST pendiente: {aud.codigo}",
            "descripcion": f"{aud.nombre}. Programada: {aud.fecha_programada}. Estado: {aud.estado}.",
            "accion_recomendada": "Ejecutar auditoría, registrar hallazgos y plan de mejoramiento.",
            "url_destino": _url("AUDITORIAS", aud.id),
            "fecha_evento": aud.fecha_programada,
            "fecha_vencimiento": aud.fecha_programada,
        })

    aud_h_q = db.query(AuditoriaHallazgoSST).filter(AuditoriaHallazgoSST.activo.is_(True))
    aud_h_q = _filtro_empresa(aud_h_q, AuditoriaHallazgoSST, empresa_id)
    aud_h_q = aud_h_q.filter(func.upper(AuditoriaHallazgoSST.estado).notin_(ESTADOS_CIERRE))
    aud_h_q = aud_h_q.filter(AuditoriaHallazgoSST.fecha_compromiso <= limite)
    for ah in aud_h_q.all():
        add({
            "empresa_id": ah.empresa_id,
            "modulo": "AUDITORIAS",
            "referencia_id": ah.id,
            "clave_unica": f"AUD-HALL-{ah.id}-{ah.estado}-{ah.fecha_compromiso}",
            "tipo": "SEGUIMIENTO",
            "prioridad": _prioridad_por_fecha(ah.fecha_compromiso, hoy, dias_alerta),
            "titulo": f"Hallazgo auditoría pendiente: {ah.codigo}",
            "descripcion": ah.descripcion,
            "accion_recomendada": "Gestionar plan de acción del hallazgo de auditoría y evidenciar cierre.",
            "url_destino": _url("AUDITORIAS", ah.id),
            "fecha_evento": ah.fecha_creacion.date() if ah.fecha_creacion else None,
            "fecha_vencimiento": ah.fecha_compromiso,
        })

    # Planes de mejoramiento vencidos o próximos.
    pm_q = db.query(PlanMejoramientoSST).filter(PlanMejoramientoSST.activo.is_(True))
    pm_q = _filtro_empresa(pm_q, PlanMejoramientoSST, empresa_id)
    pm_q = pm_q.filter(PlanMejoramientoSST.fecha_compromiso <= limite)
    pm_q = pm_q.filter(func.upper(PlanMejoramientoSST.estado).notin_(ESTADOS_CIERRE))
    for pm in pm_q.all():
        prioridad = _upper(pm.prioridad, "MEDIA")
        if prioridad not in ["CRITICA", "ALTA", "MEDIA", "BAJA"]:
            prioridad = _prioridad_por_fecha(pm.fecha_compromiso, hoy, dias_alerta)
        add({
            "empresa_id": pm.empresa_id,
            "modulo": "PLAN_MEJORAMIENTO",
            "referencia_id": pm.id,
            "clave_unica": f"PM-{pm.id}-{pm.estado}-{pm.fecha_compromiso}",
            "tipo": "VENCIMIENTO",
            "prioridad": prioridad,
            "titulo": f"Plan de mejoramiento pendiente: {pm.codigo}",
            "descripcion": f"{pm.titulo}. Avance: {pm.porcentaje_avance or 0}%. Estado: {pm.estado}.",
            "accion_recomendada": "Actualizar avance, evidencias y cerrar la acción correctiva cuando corresponda.",
            "url_destino": _url("PLAN_MEJORAMIENTO", pm.id),
            "fecha_evento": pm.fecha_apertura,
            "fecha_vencimiento": pm.fecha_compromiso,
        })

    db.commit()
    total_activas = db.query(func.count(NotificacionSST.id)).filter(NotificacionSST.activa.is_(True), NotificacionSST.archivada.is_(False)).scalar() or 0
    return {"generadas": creadas, "existentes": existentes, "total_activas": int(total_activas), "detalle": detalle}


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/", response_model=list[NotificacionSSTResponse])
def listar_notificaciones(
    empresa_id: int | None = Query(default=None),
    sede_id: int | None = Query(default=None),
    area_id: int | None = Query(default=None),
    modulo: str | None = Query(default=None),
    prioridad: str | None = Query(default=None),
    estado: str | None = Query(default=None),
    leida: bool | None = Query(default=None),
    archivada: bool | None = Query(default=False),
    buscar: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    empresa_id = _empresa_id_autorizada(usuario, empresa_id)
    query = _base_query(db).filter(NotificacionSST.activa.is_(True))
    if empresa_id is not None:
        query = query.filter(NotificacionSST.empresa_id == empresa_id)
    if sede_id:
        query = query.filter(NotificacionSST.sede_id == sede_id)
    if area_id:
        query = query.filter(NotificacionSST.area_id == area_id)
    if modulo:
        query = query.filter(func.upper(NotificacionSST.modulo) == modulo.upper())
    if prioridad:
        query = query.filter(func.upper(NotificacionSST.prioridad) == prioridad.upper())
    if estado:
        query = query.filter(func.upper(NotificacionSST.estado) == estado.upper())
    if leida is not None:
        query = query.filter(NotificacionSST.leida == leida)
    if archivada is not None:
        query = query.filter(NotificacionSST.archivada == archivada)
    if buscar:
        like = f"%{buscar.strip().lower()}%"
        query = query.filter(or_(
            func.lower(NotificacionSST.titulo).like(like),
            func.lower(NotificacionSST.descripcion).like(like),
            func.lower(NotificacionSST.modulo).like(like),
        ))
    items = query.order_by(NotificacionSST.leida.asc(), NotificacionSST.fecha_creacion.desc()).limit(limit).all()
    return [_notificacion_to_response(item) for item in items]


@router.get("/dashboard", response_model=NotificacionesDashboardResponse)
def dashboard_notificaciones(
    empresa_id: int | None = Query(default=None),
    sede_id: int | None = Query(default=None),
    area_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    empresa_id = _empresa_id_autorizada(usuario, empresa_id)
    query = db.query(NotificacionSST).filter(NotificacionSST.activa.is_(True))
    if empresa_id is not None:
        query = query.filter(NotificacionSST.empresa_id == empresa_id)
    if sede_id:
        query = query.filter(NotificacionSST.sede_id == sede_id)
    if area_id:
        query = query.filter(NotificacionSST.area_id == area_id)

    items = query.all()
    total = len(items)
    no_leidas = sum(1 for i in items if not i.leida and not i.archivada)
    leidas = sum(1 for i in items if i.leida and not i.archivada)
    archivadas = sum(1 for i in items if i.archivada)

    def count_by(attr):
        data = {}
        for item in items:
            key = _upper(getattr(item, attr, None), "SIN_DATO")
            data[key] = data.get(key, 0) + 1
        return data

    por_modulo = count_by("modulo")
    por_prioridad = count_by("prioridad")
    por_estado = count_by("estado")
    criticas = por_prioridad.get("CRITICA", 0)
    altas = por_prioridad.get("ALTA", 0)
    medias = por_prioridad.get("MEDIA", 0)
    bajas = por_prioridad.get("BAJA", 0)

    recomendaciones = []
    if criticas:
        recomendaciones.append("Atender de inmediato las alertas críticas vencidas o de alto impacto SST.")
    if altas:
        recomendaciones.append("Asignar responsables y fechas de cierre para alertas de prioridad alta.")
    if no_leidas:
        recomendaciones.append("Revisar notificaciones no leídas y documentar las acciones tomadas.")
    if not recomendaciones:
        recomendaciones.append("Centro de notificaciones estable. Mantener generación diaria de alertas SST.")

    return NotificacionesDashboardResponse(
        total=total,
        no_leidas=no_leidas,
        leidas=leidas,
        archivadas=archivadas,
        criticas=criticas,
        altas=altas,
        medias=medias,
        bajas=bajas,
        por_modulo=por_modulo,
        por_prioridad=por_prioridad,
        por_estado=por_estado,
        recomendaciones=recomendaciones,
    )


@router.post("/", response_model=NotificacionSSTResponse)
def crear_notificacion(data: NotificacionSSTCreate, db: Session = Depends(get_db), usuario=Depends(ELIMINAR_REGISTROS)):
    payload = data.model_dump()
    payload["usuario_id"] = payload.get("usuario_id") or getattr(usuario, "id", None)
    if payload.get("empresa_id"):
        empresa = db.query(Empresa).filter(Empresa.id == payload["empresa_id"]).first()
        if not empresa:
            raise HTTPException(status_code=404, detail="Empresa no encontrada")
    item = NotificacionSST(**payload)
    db.add(item)
    db.commit()
    db.refresh(item)
    return _notificacion_to_response(item)


@router.post("/generar", response_model=GeneracionNotificacionesResponse)
def generar_notificaciones(
    empresa_id: int | None = Query(default=None),
    sede_id: int | None = Query(default=None),
    area_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    resultado = generar_alertas_inteligentes(
        db=db,
        empresa_id=empresa_id,
        sede_id=sede_id,
        area_id=area_id,
        usuario_id=getattr(usuario, "id", None),
    )
    return GeneracionNotificacionesResponse(**resultado)


@router.post("/generar-v2")
def generar_alertas_v2(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    from app.services.alertas_inteligentes_service import generar_alertas_inteligentes as generar_v2
    return generar_v2(db, empresa_id)


@router.get("/{notificacion_id}", response_model=NotificacionSSTResponse)
def obtener_notificacion(notificacion_id: int, db: Session = Depends(get_db), usuario=Depends(require_roles(ROLES_SST))):
    item = _base_query(db).filter(NotificacionSST.id == notificacion_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    return _notificacion_to_response(item)


@router.put("/{notificacion_id}", response_model=NotificacionSSTResponse)
def actualizar_notificacion(notificacion_id: int, data: NotificacionSSTUpdate, db: Session = Depends(get_db), usuario=Depends(require_roles(ROLES_SST))):
    item = db.query(NotificacionSST).filter(NotificacionSST.id == notificacion_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    if item.leida and not item.fecha_lectura:
        item.fecha_lectura = datetime.utcnow()
        item.estado = "LEIDA"
    if item.archivada and not item.fecha_archivo:
        item.fecha_archivo = datetime.utcnow()
        item.estado = "ARCHIVADA"
    db.commit()
    db.refresh(item)
    return _notificacion_to_response(item)


@router.put("/{notificacion_id}/leer", response_model=NotificacionSSTResponse)
def marcar_leida(notificacion_id: int, db: Session = Depends(get_db), usuario=Depends(require_roles(ROLES_SST))):
    item = db.query(NotificacionSST).filter(NotificacionSST.id == notificacion_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    item.leida = True
    item.estado = "LEIDA"
    item.fecha_lectura = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return _notificacion_to_response(item)


@router.put("/acciones/leer-todas")
def marcar_todas_leidas(
    empresa_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    query = db.query(NotificacionSST).filter(NotificacionSST.activa.is_(True), NotificacionSST.archivada.is_(False))
    if empresa_id:
        query = query.filter(NotificacionSST.empresa_id == empresa_id)
    total = 0
    for item in query.all():
        item.leida = True
        item.estado = "LEIDA"
        item.fecha_lectura = item.fecha_lectura or datetime.utcnow()
        total += 1
    db.commit()
    return {"ok": True, "actualizadas": total}


@router.put("/{notificacion_id}/archivar", response_model=NotificacionSSTResponse)
def archivar_notificacion(notificacion_id: int, db: Session = Depends(get_db), usuario=Depends(require_roles(ROLES_SST))):
    item = db.query(NotificacionSST).filter(NotificacionSST.id == notificacion_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    item.archivada = True
    item.estado = "ARCHIVADA"
    item.fecha_archivo = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return _notificacion_to_response(item)


@router.delete("/{notificacion_id}")
def eliminar_notificacion(notificacion_id: int, db: Session = Depends(get_db), usuario=Depends(ELIMINAR_REGISTROS)):
    item = db.query(NotificacionSST).filter(NotificacionSST.id == notificacion_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    item.activa = False
    item.archivada = True
    item.estado = "ARCHIVADA"
    item.fecha_archivo = datetime.utcnow()
    db.commit()
    return {"ok": True, "mensaje": "Notificación desactivada"}


# ============================================================
# CONFIGURACIÓN
# ============================================================

@router.get("/configuracion/{empresa_id}", response_model=ConfiguracionNotificacionSSTResponse)
def obtener_configuracion(empresa_id: int, db: Session = Depends(get_db), usuario=Depends(require_roles(ROLES_SST))):
    cfg = db.query(ConfiguracionNotificacionSST).filter(ConfiguracionNotificacionSST.empresa_id == empresa_id).first()
    if not cfg:
        cfg = ConfiguracionNotificacionSST(empresa_id=empresa_id)
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    return cfg


@router.post("/configuracion", response_model=ConfiguracionNotificacionSSTResponse)
def crear_configuracion(data: ConfiguracionNotificacionSSTCreate, db: Session = Depends(get_db), usuario=Depends(ELIMINAR_REGISTROS)):
    empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    existente = db.query(ConfiguracionNotificacionSST).filter(ConfiguracionNotificacionSST.empresa_id == data.empresa_id).first()
    if existente:
        raise HTTPException(status_code=400, detail="La empresa ya tiene configuración de notificaciones")
    cfg = ConfiguracionNotificacionSST(**data.model_dump())
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg


@router.put("/configuracion/{empresa_id}", response_model=ConfiguracionNotificacionSSTResponse)
def actualizar_configuracion(empresa_id: int, data: ConfiguracionNotificacionSSTUpdate, db: Session = Depends(get_db), usuario=Depends(ELIMINAR_REGISTROS)):
    cfg = db.query(ConfiguracionNotificacionSST).filter(ConfiguracionNotificacionSST.empresa_id == empresa_id).first()
    if not cfg:
        cfg = ConfiguracionNotificacionSST(empresa_id=empresa_id)
        db.add(cfg)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(cfg, key, value)
    db.commit()
    db.refresh(cfg)
    return cfg

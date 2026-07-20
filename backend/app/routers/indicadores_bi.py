# ============================================================
# ROUTER INDICADORES BI EXECUTIVE SST ENTERPRISE - ERP SST PRO
# FASE 1.1.18.2 — BI EXECUTIVE SST ENTERPRISE
# Archivo: backend/app/routers/indicadores_bi.py
# ============================================================

from __future__ import annotations

from calendar import month_name
from datetime import date, datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.core.roles import ROLES_LECTURA_EJECUTIVA, SUPER_ADMIN, normalizar_rol
from app.database import get_db
from app.models.area import Area
from app.models.auditoria_sst import AuditoriaHallazgoSST, AuditoriaSST
from app.models.capacitacion import CapacitacionSST
from app.models.capa import CapaSST
from app.models.empleado import Empleado
from app.models.empresa import Empresa
from app.models.epp import EPPEntrega
from app.models.examen_medico import ExamenMedico
from app.models.incidente import IncidenteAccidenteSST
from app.models.inspeccion import InspeccionHallazgoSST, InspeccionSST
from app.models.matriz_peligros import MatrizPeligrosSST
from app.models.sede import Sede

router = APIRouter(prefix="/indicadores/bi", tags=["BI Executive SST Enterprise"])

ROLES_SST = list(ROLES_LECTURA_EJECUTIVA)


# ============================================================
# HELPERS
# ============================================================

MESES_ES = {
    1: "Ene",
    2: "Feb",
    3: "Mar",
    4: "Abr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dic",
}


def _as_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except Exception:
        return 0.0


def _empresa_autorizada(usuario, empresa_id: int | None) -> int | None:
    """Fuerza el alcance empresarial para cualquier consulta BI."""
    if normalizar_rol(getattr(usuario, "rol", None)) == SUPER_ADMIN:
        return empresa_id

    empresa_usuario = getattr(usuario, "empresa_id", None)
    if not empresa_usuario:
        raise HTTPException(status_code=403, detail="Usuario sin empresa asignada")
    if empresa_id is not None and int(empresa_id) != int(empresa_usuario):
        raise HTTPException(status_code=403, detail="No puede consultar indicadores de otra empresa")
    return int(empresa_usuario)


def _safe_count(query) -> int:
    try:
        return int(query.count() or 0)
    except Exception:
        return 0


def _pct(numerador: float, denominador: float) -> float:
    if not denominador or denominador <= 0:
        return 0.0
    return round((numerador / denominador) * 100, 2)


def _upper(value: Any) -> str:
    return str(value or "").strip().upper()


def _meses_ultimos_12() -> list[dict[str, Any]]:
    hoy = date.today()
    meses = []
    year = hoy.year
    month = hoy.month

    for i in range(11, -1, -1):
        m = month - i
        y = year
        while m <= 0:
            m += 12
            y -= 1
        meses.append({
            "anio": y,
            "mes": m,
            "label": f"{MESES_ES[m]} {str(y)[-2:]}",
            "key": f"{y:04d}-{m:02d}",
        })
    return meses


def _key_fecha(value: Any) -> str | None:
    if not value:
        return None
    try:
        return f"{value.year:04d}-{value.month:02d}"
    except Exception:
        return None


def _base_query(db: Session, model, activo: bool = True):
    query = db.query(model)
    if activo and hasattr(model, "activo"):
        query = query.filter(model.activo == True)
    return query


def _aplicar_filtros(query, model, empresa_id=None, sede_id=None, area_id=None):
    if empresa_id and hasattr(model, "empresa_id"):
        query = query.filter(model.empresa_id == empresa_id)
    if sede_id and hasattr(model, "sede_id"):
        query = query.filter(model.sede_id == sede_id)
    if area_id and hasattr(model, "area_id"):
        query = query.filter(model.area_id == area_id)
    return query


def _conteo_estado(query, model, estados_cierre: set[str]) -> tuple[int, int, int]:
    total = _safe_count(query)
    cerrados = 0
    abiertos = 0
    try:
        items = query.all()
        for item in items:
            estado = _upper(getattr(item, "estado", ""))
            if estado in estados_cierre:
                cerrados += 1
            else:
                abiertos += 1
    except Exception:
        cerrados = 0
        abiertos = total
    return total, cerrados, abiertos


def _score_sst(
    cumplimiento_inspecciones: float,
    cumplimiento_capa: float,
    control_eventos: float,
    cumplimiento_auditorias: float,
    cumplimiento_capacitaciones: float,
    cobertura_examenes: float,
) -> float:
    score = (
        cumplimiento_inspecciones * 0.20
        + cumplimiento_capa * 0.20
        + control_eventos * 0.20
        + cumplimiento_auditorias * 0.15
        + cumplimiento_capacitaciones * 0.15
        + cobertura_examenes * 0.10
    )
    return round(max(0.0, min(100.0, score)), 2)


def _semaforo(score: float) -> str:
    if score >= 85:
        return "VERDE"
    if score >= 60:
        return "AMARILLO"
    return "ROJO"


def _control_eventos(eventos_abiertos: int, eventos_total: int, graves: int = 0) -> float:
    if eventos_total <= 0:
        return 100.0
    cierre = _pct(eventos_total - eventos_abiertos, eventos_total)
    penalizacion_graves = min(graves * 10, 40)
    return round(max(0.0, cierre - penalizacion_graves), 2)


def _resumen_base(db: Session, empresa_id=None, sede_id=None, area_id=None) -> dict[str, Any]:
    empleados_q = _aplicar_filtros(_base_query(db, Empleado), Empleado, empresa_id, sede_id, area_id)
    inspecciones_q = _aplicar_filtros(_base_query(db, InspeccionSST), InspeccionSST, empresa_id, sede_id, area_id)
    hallazgos_q = _aplicar_filtros(_base_query(db, InspeccionHallazgoSST), InspeccionHallazgoSST, empresa_id, None, None)
    capa_q = _aplicar_filtros(_base_query(db, CapaSST), CapaSST, empresa_id, sede_id, area_id)
    eventos_q = _aplicar_filtros(_base_query(db, IncidenteAccidenteSST), IncidenteAccidenteSST, empresa_id, sede_id, area_id)
    capacitaciones_q = _aplicar_filtros(_base_query(db, CapacitacionSST), CapacitacionSST, empresa_id, None, None)
    epp_q = _aplicar_filtros(_base_query(db, EPPEntrega), EPPEntrega, empresa_id, None, None)
    examenes_q = _aplicar_filtros(_base_query(db, ExamenMedico), ExamenMedico, empresa_id, None, None)
    auditorias_q = _aplicar_filtros(_base_query(db, AuditoriaSST), AuditoriaSST, empresa_id, None, None)

    empleados = _safe_count(empleados_q)

    insp_total, insp_cerradas, insp_abiertas = _conteo_estado(
        inspecciones_q,
        InspeccionSST,
        {"CERRADA", "EJECUTADA", "FINALIZADA"},
    )

    hall_total, hall_cerrados, hall_abiertos = _conteo_estado(
        hallazgos_q,
        InspeccionHallazgoSST,
        {"CERRADO", "CERRADA", "FINALIZADO", "RESUELTO"},
    )

    capa_total, capa_cerradas, capa_abiertas = _conteo_estado(
        capa_q,
        CapaSST,
        {"CERRADA", "CERRADO", "FINALIZADA"},
    )

    eventos_total, eventos_cerrados, eventos_abiertos = _conteo_estado(
        eventos_q,
        IncidenteAccidenteSST,
        {"CERRADO", "CERRADA", "FINALIZADO", "INVESTIGADO"},
    )

    accidentes = _safe_count(eventos_q.filter(func.upper(IncidenteAccidenteSST.tipo_evento).like("%ACCIDENTE%")))
    incidentes = max(eventos_total - accidentes, 0)
    graves = _safe_count(eventos_q.filter(func.upper(IncidenteAccidenteSST.severidad).in_(["ALTA", "GRAVE", "CRITICA", "CRÍTICA"])))

    cap_total, cap_cerradas, cap_abiertas = _conteo_estado(
        capacitaciones_q,
        CapacitacionSST,
        {"EJECUTADA", "FINALIZADA", "CERRADA"},
    )

    aud_total, aud_cerradas, aud_abiertas = _conteo_estado(
        auditorias_q,
        AuditoriaSST,
        {"CERRADA", "FINALIZADA", "EJECUTADA"},
    )

    cumplimiento_inspecciones = _pct(insp_cerradas, insp_total)
    cumplimiento_capa = _pct(capa_cerradas, capa_total)
    control = _control_eventos(eventos_abiertos, eventos_total, graves)
    cumplimiento_auditorias = _pct(aud_cerradas, aud_total)
    cumplimiento_capacitaciones = _pct(cap_cerradas, cap_total)
    cobertura_epp = min(_pct(_safe_count(epp_q), empleados), 100.0) if empleados else 0.0
    cobertura_examenes = min(_pct(_safe_count(examenes_q), empleados), 100.0) if empleados else 0.0

    score = _score_sst(
        cumplimiento_inspecciones,
        cumplimiento_capa,
        control,
        cumplimiento_auditorias,
        cumplimiento_capacitaciones,
        cobertura_examenes,
    )

    return {
        "score_sst": score,
        "semaforo": _semaforo(score),
        "empleados": empleados,
        "inspecciones": insp_total,
        "inspecciones_abiertas": insp_abiertas,
        "inspecciones_cerradas": insp_cerradas,
        "hallazgos": hall_total,
        "hallazgos_abiertos": hall_abiertos,
        "hallazgos_cerrados": hall_cerrados,
        "capa": capa_total,
        "capa_abiertas": capa_abiertas,
        "capa_cerradas": capa_cerradas,
        "eventos": eventos_total,
        "eventos_abiertos": eventos_abiertos,
        "eventos_cerrados": eventos_cerrados,
        "incidentes": incidentes,
        "accidentes": accidentes,
        "eventos_graves": graves,
        "capacitaciones": cap_total,
        "capacitaciones_cerradas": cap_cerradas,
        "auditorias": aud_total,
        "auditorias_cerradas": aud_cerradas,
        "cobertura_epp": cobertura_epp,
        "cobertura_examenes": cobertura_examenes,
        "cumplimiento_inspecciones": cumplimiento_inspecciones,
        "cumplimiento_capa": cumplimiento_capa,
        "control_eventos": control,
        "cumplimiento_auditorias": cumplimiento_auditorias,
        "cumplimiento_capacitaciones": cumplimiento_capacitaciones,
    }


# ============================================================
# ENDPOINTS BI
# ============================================================

@router.get("/resumen")
def bi_resumen(
    empresa_id: int | None = Query(default=None),
    sede_id: int | None = Query(default=None),
    area_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    empresa_id = _empresa_autorizada(usuario, empresa_id)
    resumen = _resumen_base(db, empresa_id, sede_id, area_id)
    recomendaciones = []

    if resumen["semaforo"] == "ROJO":
        recomendaciones.append("Activar plan gerencial de intervención para indicadores críticos del SG-SST.")
    if resumen["hallazgos_abiertos"]:
        recomendaciones.append("Priorizar cierre de hallazgos abiertos y documentar evidencias de cierre.")
    if resumen["capa_abiertas"]:
        recomendaciones.append("Hacer comité semanal de CAPA abiertas y vencidas hasta estabilizar el cumplimiento.")
    if resumen["eventos_abiertos"]:
        recomendaciones.append("Cerrar investigaciones de incidentes/accidentes y verificar acciones correctivas.")
    if resumen["cumplimiento_capacitaciones"] < 80:
        recomendaciones.append("Reforzar ejecución de capacitaciones y registro de asistencia.")
    if not recomendaciones:
        recomendaciones.append("Gestión SST estable. Mantener seguimiento mensual y revisión por la dirección.")

    return {
        "kpis": resumen,
        "recomendaciones": recomendaciones,
        "fecha_generacion": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/tendencias")
def bi_tendencias(
    empresa_id: int | None = Query(default=None),
    sede_id: int | None = Query(default=None),
    area_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    empresa_id = _empresa_autorizada(usuario, empresa_id)
    meses = _meses_ultimos_12()
    base = {
        m["key"]: {
            "mes": m["label"],
            "inspecciones": 0,
            "capa": 0,
            "incidentes": 0,
            "accidentes": 0,
            "auditorias": 0,
            "capacitaciones": 0,
            "hallazgos": 0,
        }
        for m in meses
    }

    def sumar(model, fecha_attr, campo, filtro_extra=None):
        query = _aplicar_filtros(_base_query(db, model), model, empresa_id, sede_id, area_id)
        if filtro_extra is not None:
            query = filtro_extra(query)
        for item in query.all():
            key = _key_fecha(getattr(item, fecha_attr, None) or getattr(item, "fecha_creacion", None))
            if key in base:
                base[key][campo] += 1

    sumar(InspeccionSST, "fecha_inspeccion", "inspecciones")
    sumar(CapaSST, "fecha_apertura", "capa")
    sumar(IncidenteAccidenteSST, "fecha_evento", "incidentes", lambda q: q.filter(func.upper(IncidenteAccidenteSST.tipo_evento).notlike("%ACCIDENTE%")))
    sumar(IncidenteAccidenteSST, "fecha_evento", "accidentes", lambda q: q.filter(func.upper(IncidenteAccidenteSST.tipo_evento).like("%ACCIDENTE%")))
    sumar(AuditoriaSST, "fecha_inicio", "auditorias")
    sumar(CapacitacionSST, "fecha_ejecucion", "capacitaciones")
    sumar(InspeccionHallazgoSST, "fecha_creacion", "hallazgos")

    return list(base.values())


@router.get("/ranking-sedes")
def bi_ranking_sedes(
    empresa_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    empresa_id = _empresa_autorizada(usuario, empresa_id)
    query = db.query(Sede)
    if empresa_id:
        query = query.filter(Sede.empresa_id == empresa_id)
    sedes = query.order_by(Sede.id.asc()).all()

    data = []
    for sede in sedes:
        resumen = _resumen_base(db, sede.empresa_id, sede.id, None)
        data.append({
            "id": sede.id,
            "nombre": sede.nombre,
            "empresa_id": sede.empresa_id,
            "score_sst": resumen["score_sst"],
            "semaforo": resumen["semaforo"],
            "inspecciones": resumen["inspecciones"],
            "hallazgos_abiertos": resumen["hallazgos_abiertos"],
            "capa_abiertas": resumen["capa_abiertas"],
            "eventos": resumen["eventos"],
        })

    if not data:
        resumen = _resumen_base(db, empresa_id, None, None)
        data.append({
            "id": None,
            "nombre": "Sin sedes registradas",
            "empresa_id": empresa_id,
            "score_sst": resumen["score_sst"],
            "semaforo": resumen["semaforo"],
            "inspecciones": resumen["inspecciones"],
            "hallazgos_abiertos": resumen["hallazgos_abiertos"],
            "capa_abiertas": resumen["capa_abiertas"],
            "eventos": resumen["eventos"],
        })

    return sorted(data, key=lambda x: x["score_sst"])


@router.get("/ranking-areas")
def bi_ranking_areas(
    empresa_id: int | None = Query(default=None),
    sede_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    empresa_id = _empresa_autorizada(usuario, empresa_id)
    query = db.query(Area)
    if empresa_id:
        query = query.filter(Area.empresa_id == empresa_id)
    if sede_id and hasattr(Area, "sede_id"):
        query = query.filter(Area.sede_id == sede_id)

    areas = query.order_by(Area.id.asc()).all()
    data = []

    for area in areas:
        resumen = _resumen_base(db, area.empresa_id, sede_id, area.id)
        data.append({
            "id": area.id,
            "nombre": area.nombre,
            "empresa_id": area.empresa_id,
            "score_sst": resumen["score_sst"],
            "semaforo": resumen["semaforo"],
            "inspecciones": resumen["inspecciones"],
            "hallazgos_abiertos": resumen["hallazgos_abiertos"],
            "capa_abiertas": resumen["capa_abiertas"],
            "eventos": resumen["eventos"],
        })

    if not data:
        resumen = _resumen_base(db, empresa_id, sede_id, None)
        data.append({
            "id": None,
            "nombre": "Sin áreas registradas",
            "empresa_id": empresa_id,
            "score_sst": resumen["score_sst"],
            "semaforo": resumen["semaforo"],
            "inspecciones": resumen["inspecciones"],
            "hallazgos_abiertos": resumen["hallazgos_abiertos"],
            "capa_abiertas": resumen["capa_abiertas"],
            "eventos": resumen["eventos"],
        })

    return sorted(data, key=lambda x: x["score_sst"])


@router.get("/top-riesgos")
def bi_top_riesgos(
    empresa_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    empresa_id = _empresa_autorizada(usuario, empresa_id)
    query = _base_query(db, MatrizPeligrosSST)
    if empresa_id:
        query = query.filter(MatrizPeligrosSST.empresa_id == empresa_id)

    riesgos = query.order_by(MatrizPeligrosSST.nivel_riesgo.desc()).limit(10).all()
    return [
        {
            "id": r.id,
            "codigo": r.codigo,
            "proceso": r.proceso,
            "actividad": r.actividad,
            "peligro": r.peligro,
            "clasificacion": r.clasificacion_peligro,
            "nivel_riesgo": int(r.nivel_riesgo or 0),
            "interpretacion": r.interpretacion_riesgo,
            "aceptabilidad": r.aceptabilidad,
            "responsable": r.responsable,
        }
        for r in riesgos
    ]


@router.get("/top-hallazgos")
def bi_top_hallazgos(
    empresa_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    empresa_id = _empresa_autorizada(usuario, empresa_id)
    inspeccion_q = _base_query(db, InspeccionHallazgoSST)
    auditoria_q = _base_query(db, AuditoriaHallazgoSST)
    if empresa_id:
        inspeccion_q = inspeccion_q.filter(InspeccionHallazgoSST.empresa_id == empresa_id)
        auditoria_q = auditoria_q.filter(AuditoriaHallazgoSST.empresa_id == empresa_id)

    rows = []
    for h in inspeccion_q.order_by(InspeccionHallazgoSST.id.desc()).limit(8).all():
        rows.append({
            "id": h.id,
            "origen": "INSPECCION",
            "descripcion": h.descripcion,
            "tipo": h.tipo_hallazgo,
            "riesgo": h.nivel_riesgo,
            "estado": h.estado,
            "responsable": h.responsable,
            "fecha_compromiso": h.fecha_compromiso.isoformat() if h.fecha_compromiso else None,
        })

    for h in auditoria_q.order_by(AuditoriaHallazgoSST.id.desc()).limit(8).all():
        rows.append({
            "id": h.id,
            "origen": "AUDITORIA",
            "descripcion": h.descripcion,
            "tipo": h.tipo_hallazgo,
            "riesgo": "ALTO" if _upper(h.tipo_hallazgo) in {"NO_CONFORMIDAD", "NO CONFORMIDAD"} else "MEDIO",
            "estado": h.estado,
            "responsable": h.responsable,
            "fecha_compromiso": h.fecha_compromiso.isoformat() if h.fecha_compromiso else None,
        })

    prioridad = {"CRITICO": 0, "CRÍTICO": 0, "ALTO": 1, "MEDIO": 2, "BAJO": 3}
    return sorted(rows, key=lambda x: (prioridad.get(_upper(x.get("riesgo")), 4), x.get("estado") == "CERRADO"))[:12]


@router.get("/resumen-completo")
def bi_resumen_completo(
    empresa_id: int | None = Query(default=None),
    sede_id: int | None = Query(default=None),
    area_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    empresa_id = _empresa_autorizada(usuario, empresa_id)
    return {
        "resumen": bi_resumen(empresa_id, sede_id, area_id, db, usuario),
        "tendencias": bi_tendencias(empresa_id, sede_id, area_id, db, usuario),
        "ranking_sedes": bi_ranking_sedes(empresa_id, db, usuario),
        "ranking_areas": bi_ranking_areas(empresa_id, sede_id, db, usuario),
        "top_riesgos": bi_top_riesgos(empresa_id, db, usuario),
        "top_hallazgos": bi_top_hallazgos(empresa_id, db, usuario),
    }

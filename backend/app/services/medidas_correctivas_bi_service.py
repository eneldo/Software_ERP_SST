# ============================================================
# SERVICE DASHBOARD BI MEDIDAS CORRECTIVAS
# ERP SST PRO
# FASE 1.1.8.7.5.4 — Dashboard Ejecutivo BI
# Archivo: backend/app/services/medidas_correctivas_bi_service.py
# ============================================================

from __future__ import annotations

from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.archivo_sst import ArchivoSST
from app.models.capa import CapaSST, CapaSeguimientoSST
from app.models.alerta_medida_correctiva import AlertaMedidaCorrectivaSST


def _safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _safe_name(value, default="Sin dato"):
    value = str(value or "").strip()
    return value if value else default


def _estado_eficacia(item: CapaSST) -> str:
    porcentaje = getattr(item, "porcentaje_eficacia", None)

    if item.efectiva is True or _safe_float(porcentaje, -1) >= 80:
        return "EFICAZ"

    if porcentaje is not None:
        numeric = _safe_float(porcentaje, 0)
        if numeric >= 50:
            return "PARCIAL"
        return "NO_EFICAZ"

    if item.efectiva is False and item.verificacion_eficacia:
        return "NO_EFICAZ"

    return "PENDIENTE"


def _bar(items, getter, top=10):
    data = {}
    for item in items:
        key = getter(item)
        key = _safe_name(key)
        data[key] = data.get(key, 0) + 1
    return [{"name": k, "value": v} for k, v in sorted(data.items(), key=lambda x: x[1], reverse=True)[:top]]


def _costo_por(items, getter, top=10):
    data = {}
    for item in items:
        key = _safe_name(getter(item))
        data[key] = data.get(key, 0) + _safe_float(getattr(item, "costo_real", 0))
    return [{"name": k, "value": round(v, 2)} for k, v in sorted(data.items(), key=lambda x: x[1], reverse=True)[:top]]


def _cumplimiento_mensual(items):
    data = {}
    for item in items:
        fecha = item.fecha_cierre or item.fecha_actualizacion or item.fecha_creacion
        if not fecha:
            continue
        key = f"{fecha.year}-{str(fecha.month).zfill(2)}"
        if key not in data:
            data[key] = {"total": 0, "cerradas": 0}
        data[key]["total"] += 1
        if str(item.estado or "").upper() == "CERRADA":
            data[key]["cerradas"] += 1

    rows = []
    for key in sorted(data.keys())[-12:]:
        total = data[key]["total"]
        cerradas = data[key]["cerradas"]
        rows.append({
            "name": key,
            "value": round((cerradas / total) * 100, 1) if total else 0,
            "extra": {"total": total, "cerradas": cerradas},
        })
    return rows


def _semaforo_global(total, vencidas, criticas, sin_responsable, sin_seguimiento, cumplimiento, eficacia_promedio):
    score_riesgo = 0

    if total:
        score_riesgo += min(35, round((vencidas / total) * 60))
        score_riesgo += min(20, round((criticas / total) * 45))
        score_riesgo += min(15, round((sin_responsable / total) * 35))
        score_riesgo += min(15, round((sin_seguimiento / total) * 30))

    if cumplimiento < 50:
        score_riesgo += 20
    elif cumplimiento < 75:
        score_riesgo += 10

    if eficacia_promedio and eficacia_promedio < 50:
        score_riesgo += 15
    elif eficacia_promedio and eficacia_promedio < 80:
        score_riesgo += 7

    score_riesgo = min(score_riesgo, 100)

    if score_riesgo >= 70:
        return {
            "nivel": "CRITICO",
            "color": "ROJO",
            "score_riesgo": score_riesgo,
            "mensaje": "El centro de medidas correctivas requiere intervención inmediata.",
        }

    if score_riesgo >= 40:
        return {
            "nivel": "ATENCION",
            "color": "NARANJA",
            "score_riesgo": score_riesgo,
            "mensaje": "Existen desviaciones relevantes que deben gestionarse.",
        }

    if score_riesgo >= 20:
        return {
            "nivel": "PREVENTIVO",
            "color": "AMARILLO",
            "score_riesgo": score_riesgo,
            "mensaje": "Gestión estable con puntos preventivos por revisar.",
        }

    return {
        "nivel": "CONTROLADO",
        "color": "VERDE",
        "score_riesgo": score_riesgo,
        "mensaje": "Gestión de medidas correctivas bajo control.",
    }


def construir_bi_medidas_correctivas(db: Session, empresa_id: int | None = None) -> dict:
    query = (
        db.query(CapaSST)
        .options(
            joinedload(CapaSST.empresa),
            joinedload(CapaSST.sede),
            joinedload(CapaSST.area),
            joinedload(CapaSST.empleado),
        )
        .filter(CapaSST.activo.is_(True))
    )

    if empresa_id:
        query = query.filter(CapaSST.empresa_id == empresa_id)

    medidas = query.all()
    hoy = date.today()

    total = len(medidas)
    abiertas = sum(1 for x in medidas if str(x.estado or "").upper() not in {"CERRADA", "ANULADA"})
    cerradas = sum(1 for x in medidas if str(x.estado or "").upper() == "CERRADA")
    vencidas = sum(
        1 for x in medidas
        if x.fecha_compromiso and x.fecha_compromiso < hoy and str(x.estado or "").upper() not in {"CERRADA", "ANULADA"}
    )
    proximas_7 = sum(
        1 for x in medidas
        if x.fecha_compromiso and 0 <= (x.fecha_compromiso - hoy).days <= 7 and str(x.estado or "").upper() not in {"CERRADA", "ANULADA"}
    )
    proximas_15 = sum(
        1 for x in medidas
        if x.fecha_compromiso and 0 <= (x.fecha_compromiso - hoy).days <= 15 and str(x.estado or "").upper() not in {"CERRADA", "ANULADA"}
    )
    criticas = sum(1 for x in medidas if str(x.prioridad or "").upper() in {"CRITICA", "CRÍTICA"})
    alta = sum(1 for x in medidas if str(x.prioridad or "").upper() == "ALTA")
    sin_responsable = sum(1 for x in medidas if not x.responsable)

    seguimiento_counts = dict(
        db.query(CapaSeguimientoSST.capa_id, func.count(CapaSeguimientoSST.id))
        .filter(CapaSeguimientoSST.activo.is_(True))
        .group_by(CapaSeguimientoSST.capa_id)
        .all()
    )

    evidencias_counts = dict(
        db.query(ArchivoSST.referencia_id, func.count(ArchivoSST.id))
        .filter(
            ArchivoSST.modulo.in_(["CAPA", "MEDIDAS_CORRECTIVAS"]),
            ArchivoSST.activo.is_(True),
        )
        .group_by(ArchivoSST.referencia_id)
        .all()
    )

    sin_seguimiento = sum(1 for x in medidas if seguimiento_counts.get(x.id, 0) == 0 and str(x.estado or "").upper() not in {"CERRADA", "ANULADA"})
    sin_evidencia = sum(1 for x in medidas if evidencias_counts.get(x.id, 0) == 0 and str(x.estado or "").upper() in {"EN_EJECUCION", "VERIFICACION", "PENDIENTE_APROBACION"})

    cumplimiento = round((cerradas / total) * 100, 1) if total else 0
    avance_promedio = round(sum(_safe_float(x.avance) for x in medidas) / total, 1) if total else 0

    eficacia_estados = [_estado_eficacia(x) for x in medidas]
    eficaces = eficacia_estados.count("EFICAZ")
    parciales = eficacia_estados.count("PARCIAL")
    no_eficaces = eficacia_estados.count("NO_EFICAZ")
    pendientes_eficacia = eficacia_estados.count("PENDIENTE")

    porcentajes_eficacia = [
        _safe_float(getattr(x, "porcentaje_eficacia", None))
        for x in medidas
        if getattr(x, "porcentaje_eficacia", None) is not None
    ]
    eficacia_promedio = round(sum(porcentajes_eficacia) / len(porcentajes_eficacia), 1) if porcentajes_eficacia else 0

    costo_estimado = round(sum(_safe_float(getattr(x, "costo_estimado", 0)) for x in medidas), 2)
    costo_real = round(sum(_safe_float(getattr(x, "costo_real", 0)) for x in medidas), 2)
    desviacion_costo = round(costo_real - costo_estimado, 2)

    alertas_query = db.query(AlertaMedidaCorrectivaSST).filter(
        AlertaMedidaCorrectivaSST.activa.is_(True),
        AlertaMedidaCorrectivaSST.archivada.is_(False),
    )
    if empresa_id:
        alertas_query = alertas_query.filter(AlertaMedidaCorrectivaSST.empresa_id == empresa_id)

    alertas = alertas_query.all()
    alertas_total = len(alertas)
    alertas_criticas = sum(1 for x in alertas if str(x.prioridad or "").upper() == "CRITICA")
    alertas_altas = sum(1 for x in alertas if str(x.prioridad or "").upper() == "ALTA")
    alertas_pendientes = sum(1 for x in alertas if not x.leida)

    semaforo = _semaforo_global(
        total=total,
        vencidas=vencidas,
        criticas=criticas,
        sin_responsable=sin_responsable,
        sin_seguimiento=sin_seguimiento,
        cumplimiento=cumplimiento,
        eficacia_promedio=eficacia_promedio,
    )

    ranking_vencidas = []
    for x in medidas:
        if x.fecha_compromiso and x.fecha_compromiso < hoy and str(x.estado or "").upper() not in {"CERRADA", "ANULADA"}:
            ranking_vencidas.append({
                "id": x.id,
                "codigo": x.codigo,
                "titulo": x.titulo,
                "responsable": x.responsable or "Sin responsable",
                "dias_vencida": abs((x.fecha_compromiso - hoy).days),
                "prioridad": x.prioridad,
            })
    ranking_vencidas = sorted(ranking_vencidas, key=lambda x: x["dias_vencida"], reverse=True)[:10]

    recomendaciones = []
    if vencidas:
        recomendaciones.append("Priorizar medidas vencidas y registrar plan de recuperación.")
    if sin_responsable:
        recomendaciones.append("Asignar responsable a todas las medidas abiertas.")
    if sin_seguimiento:
        recomendaciones.append("Registrar seguimientos periódicos para las medidas abiertas.")
    if pendientes_eficacia:
        recomendaciones.append("Evaluar eficacia de las medidas con avance completo o cerradas.")
    if eficacia_promedio and eficacia_promedio < 80:
        recomendaciones.append("Revisar causas de baja eficacia y generar acciones complementarias.")
    if not recomendaciones:
        recomendaciones.append("Mantener control preventivo y seguimiento mensual de indicadores.")

    return {
        "kpis": {
            "total": total,
            "abiertas": abiertas,
            "cerradas": cerradas,
            "vencidas": vencidas,
            "proximas_7": proximas_7,
            "proximas_15": proximas_15,
            "criticas": criticas,
            "alta": alta,
            "sin_responsable": sin_responsable,
            "sin_seguimiento": sin_seguimiento,
            "sin_evidencia": sin_evidencia,
            "cumplimiento": cumplimiento,
            "avance_promedio": avance_promedio,
        },
        "eficacia": {
            "eficaces": eficaces,
            "parciales": parciales,
            "no_eficaces": no_eficaces,
            "pendientes": pendientes_eficacia,
            "promedio": eficacia_promedio,
        },
        "alertas": {
            "total": alertas_total,
            "pendientes": alertas_pendientes,
            "criticas": alertas_criticas,
            "altas": alertas_altas,
        },
        "costos": {
            "estimado": costo_estimado,
            "real": costo_real,
            "desviacion": desviacion_costo,
        },
        "semaforo": semaforo,
        "charts": {
            "por_estado": _bar(medidas, lambda x: x.estado),
            "por_prioridad": _bar(medidas, lambda x: x.prioridad),
            "por_origen": _bar(medidas, lambda x: x.origen),
            "por_area": _bar(medidas, lambda x: x.area.nombre if getattr(x, "area", None) else "Sin área"),
            "por_responsable": _bar(medidas, lambda x: x.responsable or "Sin responsable"),
            "eficacia": _bar(medidas, _estado_eficacia),
            "costo_por_area": _costo_por(medidas, lambda x: x.area.nombre if getattr(x, "area", None) else "Sin área"),
            "cumplimiento_mensual": _cumplimiento_mensual(medidas),
        },
        "ranking": {
            "vencidas": ranking_vencidas,
        },
        "recomendaciones": recomendaciones,
    }

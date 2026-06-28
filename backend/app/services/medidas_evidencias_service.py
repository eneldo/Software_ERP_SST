# ============================================================
# SERVICE EVIDENCIAS INTELIGENTES MEDIDAS CORRECTIVAS
# ERP SST PRO
# FASE 1.1.8.7.5.1 — URL robusta miniaturas reales
# Archivo: backend/app/services/medidas_evidencias_service.py
# ============================================================

from __future__ import annotations

from datetime import date
from pathlib import Path
import os

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.archivo_sst import ArchivoSST
from app.models.capa import CapaSST, CapaSeguimientoSST
from app.models.inspeccion import InspeccionSST, InspeccionHallazgoSST


UPLOAD_ROOT = Path(os.getenv("UPLOAD_DIR", "app/uploads")).resolve()


def _public_url(value: str | None) -> str | None:
    if not value:
        return None

    raw = str(value).strip()

    if not raw:
        return None

    if raw.startswith("/uploads/"):
        return raw

    normalized = raw.replace("\\", "/")

    if "/uploads/" in normalized:
        return normalized[normalized.index("/uploads/"):]

    if "/app/uploads/" in normalized:
        return "/uploads/" + normalized.split("/app/uploads/", 1)[1]

    return None


def _path_from_archivo(archivo: ArchivoSST) -> Path | None:
    for value in [archivo.ruta, archivo.url]:
        if not value:
            continue

        raw = str(value)
        if raw.startswith("/uploads/"):
            return (UPLOAD_ROOT / raw.replace("/uploads/", "", 1)).resolve()

        normalized = raw.replace("\\", "/")
        if "/app/uploads/" in normalized:
            return (UPLOAD_ROOT / normalized.split("/app/uploads/", 1)[1]).resolve()

        try:
            p = Path(raw)
            if p.is_absolute():
                return p.resolve()
        except Exception:
            continue

    return None


def _variant_url(archivo: ArchivoSST, suffix: str) -> str | None:
    path = _path_from_archivo(archivo)
    if not path:
        return None

    stem = Path(archivo.nombre_archivo or path.name).stem

    candidates = [
        path.parent / f"{stem}_{suffix}.webp",
        path.parent / f"{stem}_{suffix}.jpg",
        path.parent / f"{stem}_{suffix}.png",
    ]

    if suffix == "preview":
        candidates.extend([
            path.parent / "previews" / path.name,
            path.parent / "preview" / path.name,
        ])
    else:
        candidates.extend([
            path.parent / "thumbs" / path.name,
            path.parent / "thumbnails" / path.name,
            path.parent / "thumb" / path.name,
        ])

    for candidate in candidates:
        try:
            if candidate.exists():
                return _public_url(str(candidate))
        except Exception:
            continue

    return None


def archivo_to_item(archivo: ArchivoSST, origen_visual: str):
    base_url = _public_url(archivo.url) or _public_url(archivo.ruta)

    return {
        "id": archivo.id,
        "tipo": archivo.tipo,
        "nombre_original": archivo.nombre_original,
        "nombre_archivo": archivo.nombre_archivo,
        "url": base_url,
        "preview_url": _variant_url(archivo, "preview") or base_url,
        "thumbnail_url": _variant_url(archivo, "thumb") or base_url,
        "extension": archivo.extension or (Path(archivo.nombre_archivo or "").suffix.replace(".", "").lower() or None),
        "mime_type": archivo.mime_type,
        "tamano_bytes": archivo.tamano_bytes,
        "modulo": archivo.modulo,
        "referencia_id": archivo.referencia_id,
        "descripcion": archivo.descripcion,
        "origen_visual": origen_visual,
        "activo": archivo.activo,
        "fecha_creacion": archivo.fecha_creacion,
    }


def obtener_evidencias_medida(db: Session, medida_id: int) -> list[dict]:
    archivos = db.query(ArchivoSST).filter(
        ArchivoSST.modulo.in_(["CAPA", "MEDIDAS_CORRECTIVAS"]),
        ArchivoSST.referencia_id == medida_id,
        ArchivoSST.activo.is_(True),
    ).order_by(ArchivoSST.fecha_creacion.desc()).all()

    return [archivo_to_item(a, "MEDIDA_CORRECTIVA") for a in archivos]


def obtener_evidencias_origen(db: Session, medida: CapaSST) -> list[dict]:
    evidencias = []

    if medida.inspeccion_id:
        archivos = db.query(ArchivoSST).filter(
            ArchivoSST.modulo.in_(["INSPECCIONES", "INSPECCION_SST"]),
            ArchivoSST.referencia_id == medida.inspeccion_id,
            ArchivoSST.activo.is_(True),
        ).order_by(ArchivoSST.fecha_creacion.desc()).all()
        evidencias.extend([archivo_to_item(a, "INSPECCION_ORIGEN") for a in archivos])

    if medida.hallazgo_id:
        archivos = db.query(ArchivoSST).filter(
            ArchivoSST.modulo.in_(["HALLAZGOS", "HALLAZGO_SST", "INSPECCIONES_HALLAZGOS"]),
            ArchivoSST.referencia_id == medida.hallazgo_id,
            ArchivoSST.activo.is_(True),
        ).order_by(ArchivoSST.fecha_creacion.desc()).all()
        evidencias.extend([archivo_to_item(a, "HALLAZGO_ORIGEN") for a in archivos])

    if str(medida.origen or "").upper() in {"REPORTE_ANONIMO_SST", "REPORTE_INSEGURIDAD", "REPORTE_SST"}:
        archivos = db.query(ArchivoSST).filter(
            ArchivoSST.modulo.in_(["REPORTE_ANONIMO_SST", "REPORTE_INSEGURIDAD", "REPORTES_SST", "REPORTE_SST"]),
            ArchivoSST.activo.is_(True),
        ).order_by(ArchivoSST.fecha_creacion.desc()).limit(20).all()
        evidencias.extend([archivo_to_item(a, "REPORTE_ORIGEN") for a in archivos])

    seen = set()
    clean = []
    for item in evidencias:
        if item["id"] in seen:
            continue
        seen.add(item["id"])
        clean.append(item)

    return clean[:30]


def construir_trazabilidad_visual(db: Session, medida: CapaSST) -> list[dict]:
    eventos = []
    orden = 1

    eventos.append({
        "orden": orden,
        "fecha": medida.fecha_creacion,
        "tipo": "CREACION",
        "titulo": "Medida correctiva creada",
        "descripcion": f"{medida.codigo} · {medida.origen or 'MANUAL'}",
        "usuario": str(medida.usuario_id or ""),
        "estado": medida.estado,
        "icono": "plus",
        "color": "blue",
    })
    orden += 1

    if medida.inspeccion_id:
        inspeccion = db.query(InspeccionSST).filter(InspeccionSST.id == medida.inspeccion_id).first()
        eventos.append({
            "orden": orden,
            "fecha": getattr(inspeccion, "fecha_inspeccion", None) or getattr(inspeccion, "fecha_creacion", None),
            "tipo": "ORIGEN_INSPECCION",
            "titulo": "Origen: Inspección SST",
            "descripcion": getattr(inspeccion, "codigo", None) or f"Inspección #{medida.inspeccion_id}",
            "usuario": None,
            "estado": getattr(inspeccion, "estado", None),
            "icono": "clipboard",
            "color": "indigo",
        })
        orden += 1

    if medida.hallazgo_id:
        hallazgo = db.query(InspeccionHallazgoSST).filter(InspeccionHallazgoSST.id == medida.hallazgo_id).first()
        eventos.append({
            "orden": orden,
            "fecha": getattr(hallazgo, "fecha_creacion", None),
            "tipo": "ORIGEN_HALLAZGO",
            "titulo": "Origen: Hallazgo SST",
            "descripcion": getattr(hallazgo, "descripcion", None) or f"Hallazgo #{medida.hallazgo_id}",
            "usuario": None,
            "estado": getattr(hallazgo, "estado", None),
            "icono": "alert",
            "color": "orange",
        })
        orden += 1

    seguimientos = db.query(CapaSeguimientoSST).filter(
        CapaSeguimientoSST.capa_id == medida.id,
        CapaSeguimientoSST.activo.is_(True),
    ).order_by(CapaSeguimientoSST.fecha_seguimiento.asc(), CapaSeguimientoSST.id.asc()).all()

    for seguimiento in seguimientos:
        eventos.append({
            "orden": orden,
            "fecha": seguimiento.fecha_seguimiento or seguimiento.fecha_creacion,
            "tipo": "SEGUIMIENTO",
            "titulo": f"Seguimiento · avance {seguimiento.avance or 0}%",
            "descripcion": seguimiento.comentario or seguimiento.resultado or "Seguimiento registrado",
            "usuario": seguimiento.responsable or str(seguimiento.usuario_id or ""),
            "estado": "SEGUIMIENTO",
            "icono": "activity",
            "color": "green" if float(seguimiento.avance or 0) >= 100 else "blue",
        })
        orden += 1

    if medida.verificacion_eficacia:
        eventos.append({
            "orden": orden,
            "fecha": getattr(medida, "fecha_verificacion_eficacia", None) or medida.fecha_actualizacion,
            "tipo": "EFICACIA",
            "titulo": "Verificación de eficacia",
            "descripcion": medida.verificacion_eficacia,
            "usuario": str(getattr(medida, "verificada_por", "") or ""),
            "estado": "EFECTIVA" if medida.efectiva else "NO_EFECTIVA",
            "icono": "shield",
            "color": "green" if medida.efectiva else "red",
        })
        orden += 1

    if medida.fecha_cierre:
        eventos.append({
            "orden": orden,
            "fecha": medida.fecha_cierre,
            "tipo": "CIERRE",
            "titulo": "Medida cerrada",
            "descripcion": "Cierre registrado con trazabilidad SST.",
            "usuario": None,
            "estado": "CERRADA",
            "icono": "check",
            "color": "green",
        })

    return eventos


def calcular_semaforo_ejecutivo(db: Session, medida: CapaSST) -> dict:
    score = 0
    factores = []
    estado = str(medida.estado or "").upper()

    if estado == "CERRADA":
        if medida.efectiva is True:
            return {"nivel": "CONTROLADO", "color": "VERDE", "score": 100, "mensaje": "Medida cerrada y eficaz.", "factores": ["Cerrada", "Eficacia positiva"]}
        return {"nivel": "CERRADA_SIN_EFICACIA", "color": "AMARILLO", "score": 65, "mensaje": "Medida cerrada, pero la eficacia debe revisarse.", "factores": ["Cerrada", "Eficacia pendiente o no positiva"]}

    if not medida.responsable:
        score += 25
        factores.append("Sin responsable")

    if not medida.fecha_compromiso:
        score += 20
        factores.append("Sin fecha compromiso")
    else:
        dias = (medida.fecha_compromiso - date.today()).days
        if dias < 0:
            score += 40
            factores.append(f"Vencida hace {abs(dias)} día(s)")
        elif dias <= 7:
            score += 30
            factores.append(f"Vence en {dias} día(s)")
        elif dias <= 15:
            score += 18
            factores.append(f"Vence en {dias} día(s)")
        elif dias <= 30:
            score += 8
            factores.append(f"Vence en {dias} día(s)")

    total_seg = db.query(func.count(CapaSeguimientoSST.id)).filter(
        CapaSeguimientoSST.capa_id == medida.id,
        CapaSeguimientoSST.activo.is_(True),
    ).scalar() or 0

    if total_seg == 0:
        score += 20
        factores.append("Sin seguimientos")

    total_evi = db.query(func.count(ArchivoSST.id)).filter(
        ArchivoSST.modulo.in_(["CAPA", "MEDIDAS_CORRECTIVAS"]),
        ArchivoSST.referencia_id == medida.id,
        ArchivoSST.activo.is_(True),
    ).scalar() or 0

    if total_evi == 0 and estado in {"EN_EJECUCION", "VERIFICACION", "PENDIENTE_APROBACION"}:
        score += 20
        factores.append("Sin evidencias de ejecución")

    if str(medida.prioridad or "").upper() in {"CRITICA", "CRÍTICA"}:
        score += 20
        factores.append("Prioridad crítica")
    elif str(medida.prioridad or "").upper() == "ALTA":
        score += 10
        factores.append("Prioridad alta")

    if score >= 70:
        return {"nivel": "CRITICO", "color": "ROJO", "score": min(score, 100), "mensaje": "Requiere intervención inmediata.", "factores": factores}
    if score >= 35:
        return {"nivel": "ATENCION", "color": "NARANJA", "score": score, "mensaje": "Requiere seguimiento prioritario.", "factores": factores}
    if score >= 15:
        return {"nivel": "PREVENTIVO", "color": "AMARILLO", "score": score, "mensaje": "Mantener seguimiento preventivo.", "factores": factores}

    return {"nivel": "CONTROLADO", "color": "VERDE", "score": score, "mensaje": "Medida bajo control.", "factores": factores or ["Sin factores críticos"]}


def construir_paquete_inteligente(db: Session, medida: CapaSST) -> dict:
    evidencias_medida = obtener_evidencias_medida(db, medida.id)
    evidencias_origen = obtener_evidencias_origen(db, medida)
    trazabilidad = construir_trazabilidad_visual(db, medida)
    semaforo = calcular_semaforo_ejecutivo(db, medida)

    return {
        "medida_id": medida.id,
        "codigo": medida.codigo,
        "titulo": medida.titulo,
        "origen": medida.origen,
        "estado": medida.estado,
        "semaforo": semaforo,
        "evidencias_medida": evidencias_medida,
        "evidencias_origen": evidencias_origen,
        "trazabilidad_visual": trazabilidad,
        "resumen": {
            "total_evidencias_medida": len(evidencias_medida),
            "total_evidencias_origen": len(evidencias_origen),
            "total_eventos_trazabilidad": len(trazabilidad),
            "tiene_evidencia_origen": len(evidencias_origen) > 0,
            "tiene_evidencia_cierre": any(str(e.get("tipo") or "").upper().endswith("DESPUES") for e in evidencias_medida),
            "nivel_riesgo": semaforo["nivel"],
            "score": semaforo["score"],
        },
    }

# ============================================================
# ERP SST ENTERPRISE
# ------------------------------------------------------------
# Módulo      : Inspecciones SST
# Fase        : 1.1.8.7.9
# Archivo     : inspeccion_pdf_platinum.py
# Ubicación   : backend/app/services/pdf/
# Versión     : Platinum Final v1.0
# ------------------------------------------------------------
# Descripción:
# Generador principal del Reporte PDF Ejecutivo Platinum.
# Incluye portada premium, índice, dashboard, hallazgos,
# evidencias, CAPA completa, timeline, trazabilidad y firmas.
# ============================================================

# ============================================================
# IMPORTACIONES
# ============================================================

import hashlib
import io
import os
from datetime import date, datetime
from typing import Any, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
)
from sqlalchemy.orm import Session

from app.services.pdf.pdf_styles import (
    platinum_styles,
    PLATINUM_BORDER,
    PLATINUM_LIGHT,
    PLATINUM_SECONDARY,
)
from app.services.pdf.pdf_qr import generar_qr_temporal
from app.services.pdf.pdf_header_footer import draw_platinum_header_footer
from app.services.pdf.pdf_cover import build_cover
from app.services.pdf.pdf_index import build_index
from app.services.pdf.pdf_dashboard import build_dashboard
from app.services.pdf.pdf_capa_timeline import build_capa_timeline
from app.services.pdf.pdf_signature import build_signatures

# ============================================================
# HELPERS GENERALES
# ============================================================

def _safe(value: Any, default: str = "N/A") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _get(obj: Any, name: str, default: Any = None) -> Any:
    try:
        return getattr(obj, name, default)
    except Exception:
        return default


def _first(obj: Any, names: list[str], default: Any = None) -> Any:
    for name in names:
        value = _get(obj, name, None)
        if value not in (None, "", []):
            return value
    return default


def _date(value: Any) -> str:
    if not value:
        return "N/A"
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y %H:%M")
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
    text = str(value)
    try:
        if "T" in text:
            return datetime.fromisoformat(text.replace("Z", "")).strftime("%d/%m/%Y %H:%M")
    except Exception:
        pass
    return text[:19]


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:20].upper()


def _resolve_upload_path(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    if os.path.exists(path):
        return path
    clean = str(path).replace("\\", "/").lstrip("/")
    candidates = [
        os.path.join(os.getcwd(), clean),
        os.path.join(os.getcwd(), "app", clean),
        os.path.join(os.getcwd(), "uploads", os.path.basename(clean)),
        os.path.join(os.getcwd(), "app", "uploads", os.path.basename(clean)),
        os.path.join("/app", clean),
        os.path.join("/app/app", clean),
        os.path.join("/app/uploads", os.path.basename(clean)),
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return None


def _image_flowable(path: Optional[str], width=15 * cm, height=8.5 * cm):
    styles = platinum_styles()
    real = _resolve_upload_path(path)
    if not real:
        return Paragraph("Imagen no disponible o ruta no encontrada.", styles["small"])
    try:
        img = Image(real)
        img._restrictSize(width, height)
        return img
    except Exception:
        return Paragraph("No fue posible cargar la imagen.", styles["small"])


def _table(rows: list[list[Any]], col_widths=None):
    styles = platinum_styles()
    prepared = []
    for row in rows:
        prepared.append([Paragraph(_safe(row[0]), styles["normal"]), Paragraph(_safe(row[1]), styles["normal"])])
    table = Table(prepared, colWidths=col_widths or [5 * cm, 11.8 * cm])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, PLATINUM_BORDER),
        ("BACKGROUND", (0, 0), (0, -1), PLATINUM_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def _list(value: Any) -> list:
    if not value:
        return []
    try:
        return list(value)
    except Exception:
        return []

# ============================================================
# CONSULTA DE INSPECCIÓN
# ============================================================

def _obtener_inspeccion(db: Session, inspeccion_id: int):
    """Importa modelo de inspección de forma tolerante a nombres existentes."""
    for module_name in ["app.models.inspeccion", "app.models.inspecciones", "app.models.inspeccion_sst"]:
        try:
            module = __import__(module_name, fromlist=["InspeccionSST"])
            model = getattr(module, "InspeccionSST")
            item = db.query(model).filter(model.id == inspeccion_id).first()
            if item:
                return item
        except Exception:
            continue
    raise ValueError("Inspección no encontrada o modelo InspeccionSST no disponible.")

# ============================================================
# RELACIONES ROBUSTAS
# ============================================================

def _relaciones(inspeccion: Any) -> dict:
    return {
        "empresa": _first(inspeccion, ["empresa"], None),
        "sede": _first(inspeccion, ["sede"], None),
        "area": _first(inspeccion, ["area"], None),
        "hallazgos": _list(_first(inspeccion, ["hallazgos", "hallazgos_sst"], [])),
        "evidencias": _list(_first(inspeccion, ["evidencias", "archivos", "archivos_sst"], [])),
        "capas": _list(_first(inspeccion, ["capas", "acciones_correctivas", "medidas_correctivas"], [])),
    }

# ============================================================
# MÉTRICAS
# ============================================================

def _metricas(inspeccion: Any, relaciones: dict) -> dict:
    hallazgos = relaciones["hallazgos"]
    capas = relaciones["capas"]
    evidencias = relaciones["evidencias"]
    niveles = {}
    estados = {}
    abiertos = cerrados = vencidos = 0
    for h in hallazgos:
        estado = _safe(_first(h, ["estado"], "ABIERTO")).upper()
        nivel = _safe(_first(h, ["nivel_riesgo", "nivel", "prioridad"], "N/A")).upper()
        estados[estado] = estados.get(estado, 0) + 1
        niveles[nivel] = niveles.get(nivel, 0) + 1
        if "CERR" in estado or "FINAL" in estado:
            cerrados += 1
        else:
            abiertos += 1
        if "VENC" in estado:
            vencidos += 1
    total = len(hallazgos)
    cumplimiento = round((cerrados / total) * 100, 2) if total else float(_first(inspeccion, ["cumplimiento"], 100) or 100)
    return {
        "total_hallazgos": total,
        "abiertos": abiertos,
        "cerrados": cerrados,
        "vencidos": vencidos,
        "total_capas": len(capas),
        "total_evidencias": len(evidencias),
        "cumplimiento": cumplimiento,
        "nivel_riesgo": _safe(_first(inspeccion, ["nivel_riesgo", "riesgo", "prioridad"], "N/A")),
        "niveles": niveles,
        "estados": estados,
    }

# ============================================================
# SECCIONES PDF
# ============================================================

def _build_info_general(inspeccion: Any, info: dict):
    styles = platinum_styles()
    return [
        Paragraph("Información General de la Inspección", styles["section"]),
        _table([
            ["Código", info["codigo"]],
            ["Título", info["titulo"]],
            ["Descripción", _safe(_first(inspeccion, ["descripcion", "detalle"]))],
            ["Lugar", _safe(_first(inspeccion, ["lugar", "ubicacion"]))],
            ["Tipo inspección", _safe(_first(inspeccion, ["tipo_inspeccion", "tipo"]))],
            ["Fecha programada", _date(_first(inspeccion, ["fecha_programada"]))],
            ["Fecha inspección", info["fecha_inspeccion"]],
            ["Responsable", info["responsable"]],
            ["Estado", info["estado"]],
            ["Resultado", _safe(_first(inspeccion, ["resultado"]))],
            ["Nivel riesgo", info["nivel_riesgo"]],
            ["Cumplimiento", f"{_safe(_first(inspeccion, ['cumplimiento'], '0'))}%"],
            ["Observaciones", _safe(_first(inspeccion, ["observaciones"]))],
            ["Trazabilidad", _safe(_first(inspeccion, ["trazabilidad"]))],
        ])
    ]


def _build_hallazgos(hallazgos: list):
    styles = platinum_styles()
    story = [Paragraph("Hallazgos Identificados", styles["section"])]
    if not hallazgos:
        story.append(Paragraph("No se registran hallazgos asociados a la inspección.", styles["normal"]))
        return story
    for idx, h in enumerate(hallazgos, start=1):
        story.append(Paragraph(f"Hallazgo {idx}", styles["subsection"]))
        story.append(_table([
            ["Descripción", _safe(_first(h, ["descripcion", "hallazgo", "detalle"]))],
            ["Tipo hallazgo", _safe(_first(h, ["tipo_hallazgo", "tipo", "clasificacion"]))],
            ["Nivel de riesgo", _safe(_first(h, ["nivel_riesgo", "nivel", "prioridad"]))],
            ["Estado", _safe(_first(h, ["estado"]))],
            ["Responsable", _safe(_first(h, ["responsable"]))],
            ["Fecha compromiso", _date(_first(h, ["fecha_compromiso"]))],
            ["Fecha cierre", _date(_first(h, ["fecha_cierre"]))],
            ["Acción recomendada", _safe(_first(h, ["accion_recomendada", "accion"] ))],
            ["Observaciones", _safe(_first(h, ["observaciones"]))],
        ]))
        img = _first(h, ["imagen_url", "evidencia_url", "archivo_url", "ruta_archivo", "ruta"], None)
        if img:
            story.append(Spacer(1, 0.2 * cm))
            story.append(_image_flowable(img, width=14.8 * cm, height=8 * cm))
        story.append(Spacer(1, 0.3 * cm))
    return story


def _build_evidencias(title: str, evidencias: list):
    styles = platinum_styles()
    story = [Paragraph(title, styles["section"])]
    if not evidencias:
        story.append(Paragraph("No se registran evidencias para esta sección.", styles["normal"]))
        return story
    for idx, ev in enumerate(evidencias, start=1):
        path = _first(ev, ["ruta", "url", "archivo_url", "ruta_archivo", "path"], None)
        story.append(Paragraph(f"Evidencia {idx}: {_safe(_first(ev, ['nombre_archivo', 'filename', 'nombre']))}", styles["subsection"]))
        story.append(_table([
            ["Tipo", _safe(_first(ev, ["tipo", "tipo_evidencia"]))],
            ["Módulo", _safe(_first(ev, ["modulo", "origen"]))],
            ["Referencia", _safe(_first(ev, ["referencia_id", "entidad_id"]))],
            ["Descripción", _safe(_first(ev, ["descripcion"]))],
            ["Mime type", _safe(_first(ev, ["mime_type", "content_type"]))],
            ["Fecha carga", _date(_first(ev, ["fecha_carga", "created_at", "fecha"]))],
        ]))
        story.append(Spacer(1, 0.2 * cm))
        story.append(_image_flowable(path, width=15 * cm, height=8.5 * cm))
        story.append(Spacer(1, 0.35 * cm))
    return story


def _seguimientos_to_dicts(capa: Any) -> list[dict]:
    seguimientos = _list(_first(capa, ["seguimientos", "seguimientos_sst"], []))
    out = []
    for s in seguimientos:
        out.append({
            "fecha": _date(_first(s, ["fecha", "created_at"])),
            "responsable": _safe(_first(s, ["responsable", "usuario"])),
            "avance": _safe(_first(s, ["avance", "porcentaje_avance"], "0")),
            "estado": _safe(_first(s, ["estado", "resultado"])),
            "comentario": _safe(_first(s, ["comentario", "observaciones", "resultado"])),
        })
    return out


def _build_capas(capas: list):
    styles = platinum_styles()
    story = [Paragraph("CAPA Completa Asociada", styles["section"])]
    if not capas:
        story.append(Paragraph("No se registran acciones CAPA asociadas directamente a esta inspección.", styles["normal"]))
        return story
    for idx, capa in enumerate(capas, start=1):
        story.append(Paragraph(f"CAPA {idx}: {_safe(_first(capa, ['codigo']))}", styles["subsection"]))
        story.append(_table([
            ["Código", _safe(_first(capa, ["codigo"]))],
            ["Título", _safe(_first(capa, ["titulo", "nombre"]))],
            ["Descripción", _safe(_first(capa, ["descripcion", "detalle"]))],
            ["Tipo acción", _safe(_first(capa, ["tipo_accion", "tipo"]))],
            ["Origen", _safe(_first(capa, ["origen"]))],
            ["Prioridad", _safe(_first(capa, ["prioridad"]))],
            ["Estado", _safe(_first(capa, ["estado"]))],
            ["Responsable", _safe(_first(capa, ["responsable"]))],
            ["Fecha apertura", _date(_first(capa, ["fecha_apertura", "created_at"]))],
            ["Fecha compromiso", _date(_first(capa, ["fecha_compromiso"]))],
            ["Fecha cierre", _date(_first(capa, ["fecha_cierre"]))],
            ["Avance", f"{_safe(_first(capa, ['avance'], '0'))}%"],
        ]))
        story.append(Paragraph("Análisis de causa raíz", styles["subsection"]))
        story.append(_table([
            ["Causa raíz", _safe(_first(capa, ["causa_raiz"]))],
            ["Por qué 1", _safe(_first(capa, ["porque_1", "por_que_1"]))],
            ["Por qué 2", _safe(_first(capa, ["porque_2", "por_que_2"]))],
            ["Por qué 3", _safe(_first(capa, ["porque_3", "por_que_3"]))],
            ["Por qué 4", _safe(_first(capa, ["porque_4", "por_que_4"]))],
            ["Por qué 5", _safe(_first(capa, ["porque_5", "por_que_5"]))],
            ["Ishikawa método", _safe(_first(capa, ["ishikawa_metodo"]))],
            ["Ishikawa mano de obra", _safe(_first(capa, ["ishikawa_mano_obra"]))],
            ["Ishikawa maquinaria", _safe(_first(capa, ["ishikawa_maquinaria"]))],
            ["Ishikawa materiales", _safe(_first(capa, ["ishikawa_materiales"]))],
            ["Ishikawa medio ambiente", _safe(_first(capa, ["ishikawa_medio_ambiente"]))],
            ["Ishikawa medición", _safe(_first(capa, ["ishikawa_medicion"]))],
        ]))
        story.append(Paragraph("Plan de acción y eficacia", styles["subsection"]))
        story.append(_table([
            ["Acción inmediata", _safe(_first(capa, ["accion_inmediata"]))],
            ["Acción correctiva", _safe(_first(capa, ["accion_correctiva"]))],
            ["Acción preventiva", _safe(_first(capa, ["accion_preventiva"]))],
            ["Verificación eficacia", _safe(_first(capa, ["verificacion_eficacia"]))],
            ["Efectiva", "Sí" if _first(capa, ["efectiva", "eficaz"], False) else "No / Pendiente"],
            ["Observaciones", _safe(_first(capa, ["observaciones"]))],
        ]))
        story.extend(build_capa_timeline(_seguimientos_to_dicts(capa)))
        evidencias = _list(_first(capa, ["evidencias", "archivos", "archivos_sst"], []))
        if evidencias:
            story.extend(_build_evidencias("Evidencias CAPA", evidencias))
        traz = _safe(_first(capa, ["trazabilidad"]))
        if traz != "N/A":
            story.append(Paragraph("Trazabilidad CAPA", styles["subsection"]))
            story.append(Paragraph(traz, styles["normal_justify"]))
        story.append(Spacer(1, 0.5 * cm))
    return story


def _build_firmas(inspeccion: Any):
    firmas = [
        {"rol": "Inspector", "nombre": _safe(_first(inspeccion, ["firma_inspector_nombre", "inspector", "responsable"])), "fecha": _date(_first(inspeccion, ["firma_inspector_fecha"]))},
        {"rol": "Responsable Área", "nombre": _safe(_first(inspeccion, ["firma_responsable_area_nombre", "responsable_area"])), "fecha": _date(_first(inspeccion, ["firma_responsable_area_fecha"]))},
        {"rol": "Responsable SST", "nombre": _safe(_first(inspeccion, ["firma_sst_nombre", "responsable_sst"])), "fecha": _date(_first(inspeccion, ["firma_sst_fecha"]))},
        {"rol": "Cierre digital", "nombre": "Sí" if _first(inspeccion, ["cierre_digital"], False) else "No / Pendiente", "fecha": _date(_first(inspeccion, ["fecha_cierre", "fecha_cierre_digital"]))},
    ]
    return build_signatures(firmas)

# ============================================================
# SERVICIO PRINCIPAL
# ============================================================

def generar_reporte_inspeccion_platinum_pdf(
    db: Session,
    inspeccion_id: int,
    usuario: str = "Sistema",
    base_url: Optional[str] = None,
) -> bytes:
    """Genera PDF Ejecutivo Platinum final de inspección SST."""
    inspeccion = _obtener_inspeccion(db, inspeccion_id)
    rel = _relaciones(inspeccion)
    empresa_obj, sede_obj, area_obj = rel["empresa"], rel["sede"], rel["area"]
    codigo = _safe(_first(inspeccion, ["codigo", "codigo_inspeccion"], f"INSP-SST-{inspeccion_id:03d}"))
    fecha_generacion = _now()
    hash_doc = _hash(f"{codigo}-{inspeccion_id}-{fecha_generacion}-{usuario}")
    info = {
        "empresa": _safe(_first(empresa_obj, ["razon_social", "nombre"], _first(inspeccion, ["empresa_nombre"], "Empresa no registrada"))),
        "sede": _safe(_first(sede_obj, ["nombre"], _first(inspeccion, ["sede_nombre"], "Sede principal"))),
        "area": _safe(_first(area_obj, ["nombre"], _first(inspeccion, ["area_nombre"], "N/A"))),
        "codigo": codigo,
        "titulo": _safe(_first(inspeccion, ["titulo", "nombre"], "Inspección SST")),
        "fecha_inspeccion": _date(_first(inspeccion, ["fecha_inspeccion", "fecha"])),
        "estado": _safe(_first(inspeccion, ["estado"], "N/A")),
        "nivel_riesgo": _safe(_first(inspeccion, ["nivel_riesgo", "riesgo", "prioridad"], "N/A")),
        "responsable": _safe(_first(inspeccion, ["responsable", "inspector"], "N/A")),
        "usuario": usuario,
        "fecha_generacion": fecha_generacion,
        "hash": hash_doc,
    }
    metadata = {"codigo": codigo, "empresa": info["empresa"], "usuario": usuario, "fecha_generacion": fecha_generacion, "hash": hash_doc}
    qr_payload = base_url or f"ERP-SST://inspecciones/{inspeccion_id}/platinum/{hash_doc}"
    qr_path = generar_qr_temporal(qr_payload)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.25 * cm,
        leftMargin=1.25 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.6 * cm,
        title=f"Reporte Platinum {codigo}",
        author="ERP SST Enterprise",
    )
    story = []
    story.extend(build_cover(info, qr_path))
    story.append(PageBreak())
    story.extend(build_index())
    story.append(PageBreak())
    story.extend(build_dashboard(_metricas(inspeccion, rel)))
    story.append(PageBreak())
    story.extend(_build_info_general(inspeccion, info))
    story.append(PageBreak())
    story.extend(_build_hallazgos(rel["hallazgos"]))
    story.append(PageBreak())
    story.extend(_build_evidencias("Evidencias Fotográficas de la Inspección", rel["evidencias"]))
    story.append(PageBreak())
    story.extend(_build_capas(rel["capas"]))
    story.append(PageBreak())
    story.extend(_build_firmas(inspeccion))

    doc.build(
        story,
        onFirstPage=lambda canvas, d: draw_platinum_header_footer(canvas, d, metadata),
        onLaterPages=lambda canvas, d: draw_platinum_header_footer(canvas, d, metadata),
    )
    value = buffer.getvalue()
    buffer.close()
    return value

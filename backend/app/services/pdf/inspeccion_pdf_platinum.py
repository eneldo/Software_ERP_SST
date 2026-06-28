# ============================================================
# ERP SST ENTERPRISE
# ------------------------------------------------------------
# Módulo      : Inspecciones SST
# Fase        : 1.1.8.7.8
# Archivo     : inspeccion_pdf_platinum.py
# Ubicación   : backend/app/services/pdf/
# Versión     : Enterprise Platinum
# ------------------------------------------------------------
# Descripción:
# Genera el Reporte PDF Ejecutivo Platinum de Inspecciones SST,
# incluyendo evidencia real de inspección, hallazgos, CAPA completa,
# seguimientos CAPA, evidencias CAPA, firmas y trazabilidad.
# ============================================================

# ============================================================
# IMPORTACIONES
# ============================================================

import hashlib
import io
import os
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.services.pdf.pdf_qr import generar_qr_temporal
from app.services.pdf.pdf_styles import (
    PLATINUM_ACCENT,
    PLATINUM_BORDER,
    PLATINUM_DANGER,
    PLATINUM_LIGHT,
    PLATINUM_MUTED,
    PLATINUM_PRIMARY,
    PLATINUM_SECONDARY,
    PLATINUM_SUCCESS,
    PLATINUM_WARNING,
    get_platinum_styles,
)


# ============================================================
# CONSTANTES
# ============================================================

UPLOAD_ROOT_CANDIDATES = [
    os.getcwd(),
    os.path.join(os.getcwd(), "app"),
    os.path.join(os.getcwd(), "uploads"),
    os.path.join(os.getcwd(), "app", "uploads"),
    "/app",
    "/app/app",
    "/app/uploads",
    "/app/app/uploads",
]

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


# ============================================================
# HELPERS GENERALES
# ============================================================

def _safe(value: Any, default: str = "N/A") -> str:
    """Convierte cualquier valor a texto seguro para PDF."""
    if value is None:
        return default
    if isinstance(value, Decimal):
        return str(float(value))
    text = str(value).strip()
    return text if text else default


def _fecha(value: Any) -> str:
    """Formatea fechas y datetimes sin romper si llega texto."""
    if not value:
        return "N/A"
    try:
        if isinstance(value, datetime):
            return value.strftime("%d/%m/%Y %H:%M")
        if isinstance(value, date):
            return value.strftime("%d/%m/%Y")
        return str(value)[:10]
    except Exception:
        return "N/A"


def _now_text() -> str:
    """Fecha/hora actual para metadata del reporte."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _hash_documento(text: str) -> str:
    """Hash corto para trazabilidad documental."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:20].upper()


def _get_attr(obj: Any, attr: str, default: Any = None) -> Any:
    """Obtiene un atributo sin romper si el objeto no lo tiene."""
    try:
        return getattr(obj, attr, default)
    except Exception:
        return default


def _as_list(value: Any) -> List[Any]:
    """Convierte relaciones SQLAlchemy o None en lista segura."""
    if value is None:
        return []
    try:
        return list(value)
    except Exception:
        return []


def _unique_by_id(items: Iterable[Any]) -> List[Any]:
    """Elimina duplicados por id conservando orden."""
    output = []
    seen = set()
    for item in items:
        item_id = _get_attr(item, "id", id(item))
        if item_id in seen:
            continue
        seen.add(item_id)
        output.append(item)
    return output


def _nombre_empresa(empresa: Any, inspeccion: Any) -> str:
    return _safe(
        _get_attr(empresa, "razon_social")
        or _get_attr(empresa, "nombre")
        or _get_attr(inspeccion, "empresa_nombre")
        or "Empresa no registrada"
    )


def _estado_color(estado: str):
    estado = (estado or "").upper()
    if "CERR" in estado or "FINAL" in estado or "EFICAZ" in estado:
        return PLATINUM_SUCCESS
    if "VENC" in estado or "CRIT" in estado:
        return PLATINUM_DANGER
    if "PROCES" in estado or "SEGUIMIENTO" in estado or "VERIFIC" in estado:
        return PLATINUM_WARNING
    return PLATINUM_ACCENT


def _riesgo_color(nivel: str):
    nivel = (nivel or "").upper()
    if "CRIT" in nivel or "ALTO" in nivel:
        return PLATINUM_DANGER
    if "MED" in nivel:
        return PLATINUM_WARNING
    if "BAJO" in nivel:
        return PLATINUM_SUCCESS
    return PLATINUM_MUTED


# ============================================================
# RESOLUCIÓN DE ARCHIVOS / EVIDENCIAS
# ============================================================

def _resolve_upload_path(path: Optional[str]) -> Optional[str]:
    """
    Resuelve rutas locales para evidencias.

    Soporta:
    - rutas absolutas
    - /uploads/archivo.jpg
    - uploads/archivo.jpg
    - archivos guardados bajo app/uploads
    """
    if not path:
        return None

    normalized = str(path).replace("\\", "/").strip()

    if os.path.exists(normalized):
        return normalized

    clean = normalized.lstrip("/")
    filename = os.path.basename(clean)

    possible_paths = []

    for root in UPLOAD_ROOT_CANDIDATES:
        possible_paths.extend([
            os.path.join(root, clean),
            os.path.join(root, filename),
            os.path.join(root, "uploads", filename),
            os.path.join(root, "evidencias", filename),
        ])

    for candidate in possible_paths:
        if os.path.exists(candidate):
            return candidate

    return None


def _is_image_file(path_or_name: Optional[str], mime_type: Optional[str] = None) -> bool:
    """Determina si una evidencia es imagen."""
    if mime_type and str(mime_type).lower().startswith("image/"):
        return True
    extension = os.path.splitext(str(path_or_name or ""))[1].lower()
    return extension in IMAGE_EXTENSIONS


def _image_flowable(path: Optional[str], max_width: float = 15 * cm, max_height: float = 8.5 * cm):
    """Inserta una imagen real o muestra aviso si no existe."""
    styles = get_platinum_styles()
    real_path = _resolve_upload_path(path)

    if not real_path or not os.path.exists(real_path):
        return Paragraph("Evidencia no disponible en disco o ruta no encontrada.", styles["small"])

    if not _is_image_file(real_path):
        return Paragraph(f"Archivo documental asociado: {os.path.basename(real_path)}", styles["small"])

    try:
        img = Image(real_path)
        img._restrictSize(max_width, max_height)
        return img
    except Exception:
        return Paragraph("No fue posible renderizar la imagen de evidencia.", styles["small"])


# ============================================================
# IMPORTACIÓN SEGURA DE MODELOS
# ============================================================

def _get_model_inspeccion():
    from app.models.inspeccion import InspeccionSST
    return InspeccionSST


def _get_model_capa():
    from app.models.capa import CapaSST
    return CapaSST


def _get_model_archivo():
    from app.models.archivo_sst import ArchivoSST
    return ArchivoSST


# ============================================================
# CONSULTAS BASE
# ============================================================

def _obtener_inspeccion(db: Session, inspeccion_id: int):
    """Obtiene la inspección principal."""
    InspeccionSST = _get_model_inspeccion()
    return db.query(InspeccionSST).filter(InspeccionSST.id == inspeccion_id).first()


def _obtener_evidencias_por_referencias(
    db: Session,
    empresa_id: Optional[int],
    referencias: List[Dict[str, Any]],
) -> List[Any]:
    """
    Busca evidencias en archivos_sst por módulo y referencia.

    referencias esperadas:
    [
      {"modulos": ["INSPECCION_SST"], "id": 1},
      {"modulos": ["HALLAZGO_INSPECCION"], "id": 5},
    ]
    """
    ArchivoSST = _get_model_archivo()

    conditions = []
    for ref in referencias:
        ref_id = ref.get("id")
        modulos = ref.get("modulos") or []
        if ref_id is None:
            continue
        conditions.append(
            (ArchivoSST.referencia_id == ref_id) & (ArchivoSST.modulo.in_(modulos))
        )

    if not conditions:
        return []

    query = db.query(ArchivoSST).filter(or_(*conditions))

    if empresa_id:
        query = query.filter(ArchivoSST.empresa_id == empresa_id)

    query = query.filter(ArchivoSST.activo == True)  # noqa: E712
    query = query.order_by(ArchivoSST.fecha_creacion.asc())

    return query.all()


def _obtener_capas_completas(db: Session, inspeccion: Any, hallazgos: List[Any]) -> List[Any]:
    """Obtiene CAPA asociadas por inspección_id y por hallazgo_id."""
    CapaSST = _get_model_capa()

    hallazgo_ids = [_get_attr(h, "id") for h in hallazgos if _get_attr(h, "id")]

    query = db.query(CapaSST).filter(CapaSST.activo == True)  # noqa: E712

    conditions = [CapaSST.inspeccion_id == _get_attr(inspeccion, "id")]

    if hallazgo_ids:
        conditions.append(CapaSST.hallazgo_id.in_(hallazgo_ids))

    query = query.filter(or_(*conditions))
    query = query.order_by(CapaSST.fecha_apertura.asc(), CapaSST.id.asc())

    return query.all()


def _construir_contexto_pdf(db: Session, inspeccion_id: int) -> Dict[str, Any]:
    """Arma toda la información necesaria para el reporte Platinum."""
    inspeccion = _obtener_inspeccion(db, inspeccion_id)

    if not inspeccion:
        raise ValueError("Inspección no encontrada.")

    hallazgos = _as_list(_get_attr(inspeccion, "hallazgos", []))
    empresa_id = _get_attr(inspeccion, "empresa_id")

    capas = _obtener_capas_completas(db, inspeccion, hallazgos)

    inspeccion_refs = [
        {
            "id": _get_attr(inspeccion, "id"),
            "modulos": [
                "INSPECCION_SST",
                "INSPECCION",
                "INSPECCIONES_SST",
                "EVIDENCIA_INSPECCION",
            ],
        }
    ]

    hallazgo_refs = [
        {
            "id": _get_attr(h, "id"),
            "modulos": [
                "INSPECCION_HALLAZGO_SST",
                "HALLAZGO_INSPECCION",
                "HALLAZGO_SST",
                "EVIDENCIA_HALLAZGO",
            ],
        }
        for h in hallazgos
    ]

    capa_refs = [
        {
            "id": _get_attr(c, "id"),
            "modulos": [
                "CAPA",
                "CAPA_SST",
                "MEDIDA_CORRECTIVA",
                "EVIDENCIA_CAPA",
                "MEDIDA_CORRECTIVA_EVIDENCIA",
            ],
        }
        for c in capas
    ]

    evidencias_inspeccion = _obtener_evidencias_por_referencias(db, empresa_id, inspeccion_refs)
    evidencias_hallazgos = _obtener_evidencias_por_referencias(db, empresa_id, hallazgo_refs)
    evidencias_capas = _obtener_evidencias_por_referencias(db, empresa_id, capa_refs)

    return {
        "inspeccion": inspeccion,
        "empresa": _get_attr(inspeccion, "empresa"),
        "sede": _get_attr(inspeccion, "sede"),
        "area": _get_attr(inspeccion, "area"),
        "hallazgos": hallazgos,
        "capas": capas,
        "evidencias_inspeccion": evidencias_inspeccion,
        "evidencias_hallazgos": evidencias_hallazgos,
        "evidencias_capas": evidencias_capas,
        "todas_evidencias": _unique_by_id(
            evidencias_inspeccion + evidencias_hallazgos + evidencias_capas
        ),
    }


# ============================================================
# COMPONENTES VISUALES PDF
# ============================================================

def _header_footer(canvas, doc, metadata: Dict[str, str]):
    """Encabezado y pie corporativo para todas las páginas."""
    canvas.saveState()

    width, height = A4

    canvas.setFillColor(PLATINUM_PRIMARY)
    canvas.rect(0, height - 1.25 * cm, width, 1.25 * cm, fill=True, stroke=False)

    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(1.2 * cm, height - 0.75 * cm, "ERP SST ENTERPRISE · REPORTE EJECUTIVO PLATINUM")

    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(
        width - 1.2 * cm,
        height - 0.75 * cm,
        f"Código: {_safe(metadata.get('codigo'))} · Página {doc.page}",
    )

    canvas.setStrokeColor(PLATINUM_BORDER)
    canvas.line(1.2 * cm, 1.35 * cm, width - 1.2 * cm, 1.35 * cm)

    canvas.setFillColor(PLATINUM_MUTED)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(
        1.2 * cm,
        0.9 * cm,
        f"Generado: {_safe(metadata.get('fecha_generacion'))} · Usuario: {_safe(metadata.get('usuario'))}",
    )
    canvas.drawRightString(
        width - 1.2 * cm,
        0.9 * cm,
        f"Hash: {_safe(metadata.get('hash'))}",
    )

    canvas.restoreState()


def _tabla_info(rows: List[List[Any]], col_widths: Optional[List[float]] = None):
    """Tabla estándar de campos y valores."""
    styles = get_platinum_styles()
    data = [
        [Paragraph(f"<b>{_safe(k)}</b>", styles["normal"]), Paragraph(_safe(v), styles["normal"])]
        for k, v in rows
    ]

    table = Table(data, colWidths=col_widths or [5 * cm, 11 * cm])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, PLATINUM_BORDER),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def _card_kpi(label: str, value: Any, color=PLATINUM_SECONDARY):
    """Tarjeta KPI para dashboard ejecutivo."""
    styles = get_platinum_styles()

    table = Table(
        [[Paragraph(str(value), styles["kpi_value"])], [Paragraph(label, styles["kpi_label"])]],
        colWidths=[4.1 * cm],
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PLATINUM_LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.8, color),
        ("LINEABOVE", (0, 0), (-1, 0), 4, color),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def _pie_chart(title: str, data_dict: Dict[str, int]):
    """Gráfico circular sencillo."""
    drawing = Drawing(230, 160)

    if not data_dict:
        data_dict = {"Sin datos": 1}

    pie = Pie()
    pie.x = 65
    pie.y = 15
    pie.width = 110
    pie.height = 110
    pie.data = list(data_dict.values())
    pie.labels = list(data_dict.keys())
    pie.slices.strokeWidth = 0.5

    palette = [PLATINUM_ACCENT, PLATINUM_SUCCESS, PLATINUM_WARNING, PLATINUM_DANGER, PLATINUM_MUTED]
    for i in range(len(pie.data)):
        pie.slices[i].fillColor = palette[i % len(palette)]

    drawing.add(String(15, 145, title, fontName="Helvetica-Bold", fontSize=9, fillColor=PLATINUM_PRIMARY))
    drawing.add(pie)
    return drawing


def _bar_chart(title: str, data_dict: Dict[str, int]):
    """Gráfico de barras sencillo."""
    drawing = Drawing(430, 180)

    if not data_dict:
        data_dict = {"Sin datos": 0}

    max_value = max(list(data_dict.values()) + [1])

    chart = VerticalBarChart()
    chart.x = 45
    chart.y = 35
    chart.height = 100
    chart.width = 340
    chart.data = [list(data_dict.values())]
    chart.categoryAxis.categoryNames = list(data_dict.keys())
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max_value + 1
    chart.valueAxis.valueStep = 1
    chart.bars[0].fillColor = PLATINUM_ACCENT

    drawing.add(String(10, 160, title, fontName="Helvetica-Bold", fontSize=10, fillColor=PLATINUM_PRIMARY))
    drawing.add(chart)
    return drawing


# ============================================================
# SECCIONES PDF
# ============================================================

def _agregar_portada(story: List[Any], contexto: Dict[str, Any], metadata: Dict[str, str], base_url: Optional[str]):
    """Portada ejecutiva del reporte."""
    styles = get_platinum_styles()
    inspeccion = contexto["inspeccion"]
    empresa = contexto["empresa"]
    sede = contexto["sede"]
    area = contexto["area"]

    codigo = metadata["codigo"]
    hash_doc = metadata["hash"]

    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph("REPORTE PDF EJECUTIVO PLATINUM", styles["title"]))
    story.append(Paragraph("Inspección SST · Evidencias reales · Hallazgos · CAPA completa · Seguimientos", styles["subtitle"]))
    story.append(Spacer(1, 0.7 * cm))

    story.append(_tabla_info([
        ["Empresa", _nombre_empresa(empresa, inspeccion)],
        ["Sede", _safe(_get_attr(sede, "nombre") or "Sede principal")],
        ["Área", _safe(_get_attr(area, "nombre"))],
        ["Código inspección", codigo],
        ["Título", _safe(_get_attr(inspeccion, "titulo"))],
        ["Fecha inspección", _fecha(_get_attr(inspeccion, "fecha_inspeccion"))],
        ["Estado", _safe(_get_attr(inspeccion, "estado"))],
        ["Nivel de riesgo", _safe(_get_attr(inspeccion, "nivel_riesgo"))],
        ["Responsable", _safe(_get_attr(inspeccion, "responsable"))],
        ["Generado por", _safe(metadata.get("usuario"))],
        ["Fecha generación", _safe(metadata.get("fecha_generacion"))],
        ["Hash documento", hash_doc],
    ]))

    story.append(Spacer(1, 0.8 * cm))

    qr_data = base_url or f"ERP-SST-PRO://inspecciones/{_get_attr(inspeccion, 'id')}/platinum/{hash_doc}"
    qr_path = generar_qr_temporal(qr_data)

    qr_table = Table([
        [
            Paragraph(
                "<b>Verificación documental</b><br/>Código QR de trazabilidad para validar el reporte generado.",
                styles["normal"],
            ),
            Image(qr_path, width=3.2 * cm, height=3.2 * cm),
        ]
    ], colWidths=[12 * cm, 4 * cm])
    qr_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, PLATINUM_BORDER),
        ("BACKGROUND", (0, 0), (-1, -1), PLATINUM_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(qr_table)
    story.append(PageBreak())


def _agregar_dashboard(story: List[Any], contexto: Dict[str, Any]):
    """Dashboard ejecutivo con KPIs y gráficos."""
    styles = get_platinum_styles()

    inspeccion = contexto["inspeccion"]
    hallazgos = contexto["hallazgos"]
    capas = contexto["capas"]
    evidencias = contexto["todas_evidencias"]

    estados: Dict[str, int] = {}
    niveles = {"CRÍTICO": 0, "ALTO": 0, "MEDIO": 0, "BAJO": 0}
    abiertos = 0
    cerrados = 0
    vencidos = 0

    for hallazgo in hallazgos:
        estado = _safe(_get_attr(hallazgo, "estado")).upper()
        nivel = _safe(_get_attr(hallazgo, "nivel_riesgo")).upper()
        estados[estado] = estados.get(estado, 0) + 1

        if "CERR" in estado:
            cerrados += 1
        else:
            abiertos += 1

        if "VENC" in estado:
            vencidos += 1

        if "CRIT" in nivel:
            niveles["CRÍTICO"] += 1
        elif "ALTO" in nivel:
            niveles["ALTO"] += 1
        elif "MED" in nivel:
            niveles["MEDIO"] += 1
        elif "BAJO" in nivel:
            niveles["BAJO"] += 1

    cumplimiento = round((cerrados / len(hallazgos)) * 100, 2) if hallazgos else 100

    story.append(Paragraph("1. Dashboard Ejecutivo SST", styles["section"]))

    table = Table([
        [
            _card_kpi("Hallazgos", len(hallazgos), PLATINUM_ACCENT),
            _card_kpi("Abiertos", abiertos, PLATINUM_WARNING),
            _card_kpi("Cerrados", cerrados, PLATINUM_SUCCESS),
            _card_kpi("Vencidos", vencidos, PLATINUM_DANGER),
        ],
        [
            _card_kpi("CAPA", len(capas), PLATINUM_SECONDARY),
            _card_kpi("Evidencias", len(evidencias), PLATINUM_ACCENT),
            _card_kpi("Cumplimiento", f"{cumplimiento}%", PLATINUM_SUCCESS if cumplimiento >= 80 else PLATINUM_WARNING),
            _card_kpi("Riesgo", _safe(_get_attr(inspeccion, "nivel_riesgo")), _riesgo_color(_safe(_get_attr(inspeccion, "nivel_riesgo")))),
        ],
    ], colWidths=[4.2 * cm, 4.2 * cm, 4.2 * cm, 4.2 * cm])
    table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(table)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Table([
        [_pie_chart("Distribución por nivel de riesgo", {k: v for k, v in niveles.items() if v > 0}), _pie_chart("Distribución por estado", estados)]
    ], colWidths=[8.3 * cm, 8.3 * cm]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(_bar_chart("Hallazgos por nivel", {k: v for k, v in niveles.items() if v > 0}))
    story.append(PageBreak())


def _agregar_info_general(story: List[Any], contexto: Dict[str, Any]):
    """Información base de la inspección."""
    styles = get_platinum_styles()
    inspeccion = contexto["inspeccion"]

    story.append(Paragraph("2. Información General de la Inspección", styles["section"]))
    story.append(_tabla_info([
        ["Código", _safe(_get_attr(inspeccion, "codigo"))],
        ["Título", _safe(_get_attr(inspeccion, "titulo"))],
        ["Descripción", _safe(_get_attr(inspeccion, "descripcion"))],
        ["Lugar", _safe(_get_attr(inspeccion, "lugar"))],
        ["Tipo inspección", _safe(_get_attr(inspeccion, "tipo_inspeccion"))],
        ["Fecha programada", _fecha(_get_attr(inspeccion, "fecha_programada"))],
        ["Fecha inspección", _fecha(_get_attr(inspeccion, "fecha_inspeccion"))],
        ["Responsable", _safe(_get_attr(inspeccion, "responsable"))],
        ["Estado", _safe(_get_attr(inspeccion, "estado"))],
        ["Resultado", _safe(_get_attr(inspeccion, "resultado"))],
        ["Nivel riesgo", _safe(_get_attr(inspeccion, "nivel_riesgo"))],
        ["Cumplimiento", f"{_safe(_get_attr(inspeccion, 'cumplimiento'), '0')}%"],
        ["Observaciones", _safe(_get_attr(inspeccion, "observaciones"))],
        ["Trazabilidad", _safe(_get_attr(inspeccion, "trazabilidad"))],
    ]))
    story.append(PageBreak())


def _agregar_hallazgos(story: List[Any], contexto: Dict[str, Any]):
    """Hallazgos con sus evidencias relacionadas."""
    styles = get_platinum_styles()
    hallazgos = contexto["hallazgos"]
    evidencias_hallazgos = contexto["evidencias_hallazgos"]

    story.append(Paragraph("3. Hallazgos Identificados", styles["section"]))

    if not hallazgos:
        story.append(Paragraph("No se registran hallazgos asociados a esta inspección.", styles["normal"]))
        story.append(PageBreak())
        return

    for idx, hallazgo in enumerate(hallazgos, start=1):
        story.append(Paragraph(f"Hallazgo {idx}", styles["subsection"]))
        story.append(_tabla_info([
            ["Descripción", _safe(_get_attr(hallazgo, "descripcion"))],
            ["Tipo hallazgo", _safe(_get_attr(hallazgo, "tipo_hallazgo"))],
            ["Nivel de riesgo", _safe(_get_attr(hallazgo, "nivel_riesgo"))],
            ["Estado", _safe(_get_attr(hallazgo, "estado"))],
            ["Responsable", _safe(_get_attr(hallazgo, "responsable"))],
            ["Fecha compromiso", _fecha(_get_attr(hallazgo, "fecha_compromiso"))],
            ["Fecha cierre", _fecha(_get_attr(hallazgo, "fecha_cierre"))],
            ["Acción recomendada", _safe(_get_attr(hallazgo, "accion_recomendada"))],
            ["Observaciones", _safe(_get_attr(hallazgo, "observaciones"))],
        ]))

        relacionadas = [e for e in evidencias_hallazgos if _get_attr(e, "referencia_id") == _get_attr(hallazgo, "id")]
        if relacionadas:
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph("Evidencias del hallazgo", styles["subsection"]))
            _agregar_bloque_evidencias(story, relacionadas, max_items=3)

        story.append(PageBreak())


def _agregar_bloque_evidencias(story: List[Any], evidencias: List[Any], max_items: Optional[int] = None):
    """Renderiza una lista de evidencias con metadata e imagen."""
    styles = get_platinum_styles()

    items = evidencias[:max_items] if max_items else evidencias

    if not items:
        story.append(Paragraph("No se registran evidencias para esta sección.", styles["normal"]))
        return

    for idx, evidencia in enumerate(items, start=1):
        ruta = _get_attr(evidencia, "ruta") or _get_attr(evidencia, "url") or _get_attr(evidencia, "nombre_archivo")
        nombre = _safe(_get_attr(evidencia, "nombre_original") or _get_attr(evidencia, "nombre_archivo"))

        story.append(Paragraph(f"Evidencia {idx}: {nombre}", styles["subsection"]))
        story.append(_tabla_info([
            ["Tipo", _safe(_get_attr(evidencia, "tipo"))],
            ["Módulo", _safe(_get_attr(evidencia, "modulo"))],
            ["Referencia", _safe(_get_attr(evidencia, "referencia_id"))],
            ["Descripción", _safe(_get_attr(evidencia, "descripcion"))],
            ["Mime type", _safe(_get_attr(evidencia, "mime_type"))],
            ["Fecha carga", _fecha(_get_attr(evidencia, "fecha_creacion"))],
        ]))
        story.append(Spacer(1, 0.2 * cm))
        story.append(_image_flowable(ruta, max_width=15 * cm, max_height=8.5 * cm))
        story.append(Spacer(1, 0.35 * cm))


def _agregar_evidencias_inspeccion(story: List[Any], contexto: Dict[str, Any]):
    """Evidencias asociadas directamente a la inspección."""
    styles = get_platinum_styles()
    story.append(Paragraph("4. Evidencias Fotográficas de la Inspección", styles["section"]))
    _agregar_bloque_evidencias(story, contexto["evidencias_inspeccion"])
    story.append(PageBreak())


def _agregar_capas_completas(story: List[Any], contexto: Dict[str, Any]):
    """CAPA completa: causa raíz, 5 porqués, Ishikawa, acciones, seguimientos y evidencias."""
    styles = get_platinum_styles()
    capas = contexto["capas"]
    evidencias_capas = contexto["evidencias_capas"]

    story.append(Paragraph("5. CAPA Completa Asociada", styles["section"]))

    if not capas:
        story.append(Paragraph("No se registran acciones CAPA asociadas a esta inspección o a sus hallazgos.", styles["normal"]))
        story.append(PageBreak())
        return

    for idx, capa in enumerate(capas, start=1):
        story.append(Paragraph(f"CAPA {idx}: {_safe(_get_attr(capa, 'codigo'))}", styles["subsection"]))

        story.append(_tabla_info([
            ["Código", _safe(_get_attr(capa, "codigo"))],
            ["Título", _safe(_get_attr(capa, "titulo"))],
            ["Descripción", _safe(_get_attr(capa, "descripcion"))],
            ["Tipo acción", _safe(_get_attr(capa, "tipo_accion"))],
            ["Origen", _safe(_get_attr(capa, "origen"))],
            ["Prioridad", _safe(_get_attr(capa, "prioridad"))],
            ["Estado", _safe(_get_attr(capa, "estado"))],
            ["Responsable", _safe(_get_attr(capa, "responsable"))],
            ["Fecha apertura", _fecha(_get_attr(capa, "fecha_apertura"))],
            ["Fecha compromiso", _fecha(_get_attr(capa, "fecha_compromiso"))],
            ["Fecha cierre", _fecha(_get_attr(capa, "fecha_cierre"))],
            ["Avance", f"{_safe(_get_attr(capa, 'avance'), '0')}%"],
        ]))

        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph("Análisis de causa raíz", styles["subsection"]))
        story.append(_tabla_info([
            ["Causa raíz", _safe(_get_attr(capa, "causa_raiz"))],
            ["Por qué 1", _safe(_get_attr(capa, "porque_1"))],
            ["Por qué 2", _safe(_get_attr(capa, "porque_2"))],
            ["Por qué 3", _safe(_get_attr(capa, "porque_3"))],
            ["Por qué 4", _safe(_get_attr(capa, "porque_4"))],
            ["Por qué 5", _safe(_get_attr(capa, "porque_5"))],
        ]))

        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph("Ishikawa", styles["subsection"]))
        story.append(_tabla_info([
            ["Método", _safe(_get_attr(capa, "ishikawa_metodo"))],
            ["Mano de obra", _safe(_get_attr(capa, "ishikawa_mano_obra"))],
            ["Maquinaria", _safe(_get_attr(capa, "ishikawa_maquinaria"))],
            ["Materiales", _safe(_get_attr(capa, "ishikawa_materiales"))],
            ["Medio ambiente", _safe(_get_attr(capa, "ishikawa_medio_ambiente"))],
            ["Medición", _safe(_get_attr(capa, "ishikawa_medicion"))],
        ]))

        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph("Plan de acción y eficacia", styles["subsection"]))
        story.append(_tabla_info([
            ["Acción inmediata", _safe(_get_attr(capa, "accion_inmediata"))],
            ["Acción correctiva", _safe(_get_attr(capa, "accion_correctiva"))],
            ["Acción preventiva", _safe(_get_attr(capa, "accion_preventiva"))],
            ["Verificación eficacia", _safe(_get_attr(capa, "verificacion_eficacia"))],
            ["Efectiva", "Sí" if _get_attr(capa, "efectiva") is True else "No" if _get_attr(capa, "efectiva") is False else "Pendiente"],
            ["Observaciones", _safe(_get_attr(capa, "observaciones"))],
        ]))

        seguimientos = _as_list(_get_attr(capa, "seguimientos", []))
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph("Seguimientos CAPA", styles["subsection"]))
        _agregar_seguimientos_capa(story, seguimientos)

        evidencia_capa = [e for e in evidencias_capas if _get_attr(e, "referencia_id") == _get_attr(capa, "id")]
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph("Evidencias CAPA", styles["subsection"]))
        _agregar_bloque_evidencias(story, evidencia_capa, max_items=4)

        if _safe(_get_attr(capa, "trazabilidad"), ""):
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph("Trazabilidad CAPA", styles["subsection"]))
            story.append(Paragraph(_safe(_get_attr(capa, "trazabilidad")), styles["small"]))

        story.append(PageBreak())


def _agregar_seguimientos_capa(story: List[Any], seguimientos: List[Any]):
    """Tabla de seguimientos de una CAPA."""
    styles = get_platinum_styles()

    if not seguimientos:
        story.append(Paragraph("No se registran seguimientos CAPA.", styles["normal"]))
        return

    data = [[
        Paragraph("<b>Fecha</b>", styles["normal"]),
        Paragraph("<b>Responsable</b>", styles["normal"]),
        Paragraph("<b>Avance</b>", styles["normal"]),
        Paragraph("<b>Resultado / Comentario</b>", styles["normal"]),
    ]]

    for seguimiento in seguimientos:
        data.append([
            Paragraph(_fecha(_get_attr(seguimiento, "fecha_seguimiento")), styles["normal"]),
            Paragraph(_safe(_get_attr(seguimiento, "responsable")), styles["normal"]),
            Paragraph(f"{_safe(_get_attr(seguimiento, 'avance'), '0')}%", styles["normal"]),
            Paragraph(
                f"<b>{_safe(_get_attr(seguimiento, 'resultado'))}</b><br/>{_safe(_get_attr(seguimiento, 'comentario'))}",
                styles["normal"],
            ),
        ])

    table = Table(data, colWidths=[2.8 * cm, 4 * cm, 2.2 * cm, 7.2 * cm])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, PLATINUM_BORDER),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(table)


def _agregar_firmas(story: List[Any], contexto: Dict[str, Any]):
    """Sección final de firmas y cierre documental."""
    styles = get_platinum_styles()
    inspeccion = contexto["inspeccion"]

    story.append(Paragraph("6. Firmas y Validación", styles["section"]))

    firmas = [
        ["Inspector", _safe(_get_attr(inspeccion, "firma_inspector_nombre") or _get_attr(inspeccion, "responsable")), _fecha(_get_attr(inspeccion, "firma_inspector_fecha"))],
        ["Responsable Área", _safe(_get_attr(inspeccion, "firma_responsable_area_nombre")), _fecha(_get_attr(inspeccion, "firma_responsable_area_fecha"))],
        ["Responsable SST", _safe(_get_attr(inspeccion, "firma_sst_nombre")), _fecha(_get_attr(inspeccion, "firma_sst_fecha"))],
        ["Cierre digital", "Sí" if _get_attr(inspeccion, "cierre_digital") else "No", _fecha(_get_attr(inspeccion, "cierre_digital_fecha"))],
    ]

    data = []
    for cargo, nombre, fecha_firma in firmas:
        data.append([
            Paragraph("<br/><br/>______________________________", styles["normal"]),
            Paragraph(f"<b>{cargo}</b><br/>{nombre}<br/>Fecha: {fecha_firma}", styles["normal"]),
        ])

    table = Table(data, colWidths=[8 * cm, 8 * cm])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, PLATINUM_BORDER),
        ("BACKGROUND", (0, 0), (-1, -1), PLATINUM_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "Este documento fue generado automáticamente por ERP SST Enterprise. "
        "Consolida la inspección, evidencias, hallazgos, CAPA, seguimientos, eficacia y trazabilidad.",
        styles["small"],
    ))


# ============================================================
# GENERADOR PRINCIPAL
# ============================================================

def generar_reporte_inspeccion_platinum_pdf(
    db: Session,
    inspeccion_id: int,
    usuario: str = "Sistema",
    base_url: Optional[str] = None,
) -> bytes:
    """
    Genera el PDF Ejecutivo Platinum.

    Usado por:
    GET /inspecciones-exportaciones-platinum/{id}/pdf-platinum
    """
    contexto = _construir_contexto_pdf(db, inspeccion_id)
    inspeccion = contexto["inspeccion"]

    codigo = _safe(_get_attr(inspeccion, "codigo") or f"INSP-SST-{inspeccion_id:03d}")
    fecha_generacion = _now_text()
    hash_doc = _hash_documento(f"{codigo}-{fecha_generacion}-{usuario}-{inspeccion_id}")

    metadata = {
        "codigo": codigo,
        "fecha_generacion": fecha_generacion,
        "usuario": usuario or "Sistema",
        "hash": hash_doc,
    }

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.3 * cm,
        leftMargin=1.3 * cm,
        topMargin=1.9 * cm,
        bottomMargin=1.7 * cm,
        title=f"Reporte Platinum {codigo}",
        author="ERP SST Enterprise",
    )

    story: List[Any] = []

    _agregar_portada(story, contexto, metadata, base_url)
    _agregar_dashboard(story, contexto)
    _agregar_info_general(story, contexto)
    _agregar_hallazgos(story, contexto)
    _agregar_evidencias_inspeccion(story, contexto)
    _agregar_capas_completas(story, contexto)
    _agregar_firmas(story, contexto)

    doc.build(
        story,
        onFirstPage=lambda canvas, doc_obj: _header_footer(canvas, doc_obj, metadata),
        onLaterPages=lambda canvas, doc_obj: _header_footer(canvas, doc_obj, metadata),
    )

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

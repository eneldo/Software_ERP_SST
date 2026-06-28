# ============================================================
# SERVICE REPORTE PDF EJECUTIVO MEDIDAS CORRECTIVAS
# ERP SST PRO
# FIX FASE 1.1.8.7.6 — Compatible con columnas opcionales
# Archivo: backend/app/services/medidas_correctivas_pdf_service.py
# ============================================================

from __future__ import annotations

import os
from datetime import date, datetime
from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
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

from sqlalchemy.orm import Session

from app.models.archivo_sst import ArchivoSST
from app.models.capa import CapaSST, CapaSeguimientoSST


UPLOAD_ROOT = Path(os.getenv("UPLOAD_DIR", "app/uploads")).resolve()


def _safe(value: Any, default: str = "—") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _get(obj: Any, attr: str, default: Any = None) -> Any:
    return getattr(obj, attr, default)


def _fmt_date(value: Any) -> str:
    if not value:
        return "—"
    if isinstance(value, (date, datetime)):
        return value.strftime("%d/%m/%Y")
    return str(value)


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _fmt_money(value: Any) -> str:
    number = _num(value)
    return f"${number:,.0f}".replace(",", ".")


def _fmt_percent(value: Any) -> str:
    return f"{_num(value):.1f}%"


def _public_to_path(value: str | None) -> Path | None:
    if not value:
        return None

    raw = str(value).strip()
    if not raw:
        return None

    if raw.startswith("/uploads/"):
        return (UPLOAD_ROOT / raw.replace("/uploads/", "", 1)).resolve()

    normalized = raw.replace("\\", "/")

    if "/app/uploads/" in normalized:
        return (UPLOAD_ROOT / normalized.split("/app/uploads/", 1)[1]).resolve()

    if "/uploads/" in normalized:
        return (UPLOAD_ROOT / normalized.split("/uploads/", 1)[1]).resolve()

    try:
        p = Path(raw)
        if p.exists():
            return p
    except Exception:
        return None

    return None


def _estado_eficacia(item: CapaSST) -> tuple[str, str]:
    porcentaje = _get(item, "porcentaje_eficacia", None)
    pct = _num(porcentaje, -1) if porcentaje is not None else None

    if _get(item, "efectiva", None) is True or (pct is not None and pct >= 80):
        return "EFICAZ", "La medida se considera eficaz."

    if pct is not None and pct >= 50:
        return "PARCIAL", "La eficacia es parcial; requiere seguimiento adicional."

    if pct is not None and pct < 50:
        return "NO EFICAZ", "La medida no controló completamente la causa raíz."

    if _get(item, "efectiva", None) is False and _get(item, "verificacion_eficacia", None):
        return "NO EFICAZ", "La verificación registrada indica no eficacia."

    return "PENDIENTE", "La eficacia aún no ha sido evaluada."


def _semaforo_medida(item: CapaSST, total_seguimientos: int, total_evidencias: int) -> tuple[str, str, list[str]]:
    estado = str(_get(item, "estado", "") or "").upper()
    factores = []
    score = 0

    if estado == "CERRADA":
        if _get(item, "efectiva", None) is True:
            return "CONTROLADO", "VERDE", ["Medida cerrada", "Eficacia positiva"]
        return "CERRADA SIN EFICACIA", "AMARILLO", ["Medida cerrada", "Eficacia pendiente o no positiva"]

    if not _get(item, "responsable", None):
        score += 25
        factores.append("Sin responsable")

    fecha_compromiso = _get(item, "fecha_compromiso", None)
    if not fecha_compromiso:
        score += 20
        factores.append("Sin fecha compromiso")
    else:
        dias = (fecha_compromiso - date.today()).days
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

    if total_seguimientos == 0:
        score += 20
        factores.append("Sin seguimientos")

    if total_evidencias == 0 and estado in {"EN_EJECUCION", "VERIFICACION", "PENDIENTE_APROBACION"}:
        score += 20
        factores.append("Sin evidencias de ejecución")

    prioridad = str(_get(item, "prioridad", "") or "").upper()
    if prioridad in {"CRITICA", "CRÍTICA"}:
        score += 20
        factores.append("Prioridad crítica")
    elif prioridad == "ALTA":
        score += 10
        factores.append("Prioridad alta")

    if score >= 70:
        return "CRÍTICO", "ROJO", factores
    if score >= 35:
        return "ATENCIÓN", "NARANJA", factores
    if score >= 15:
        return "PREVENTIVO", "AMARILLO", factores

    return "CONTROLADO", "VERDE", factores or ["Sin factores críticos"]


def _header_footer(canvas, doc):
    canvas.saveState()
    width, height = doc.pagesize

    canvas.setFillColor(colors.HexColor("#0f2d6b"))
    canvas.rect(0, height - 1.25 * cm, width, 1.25 * cm, fill=1, stroke=0)

    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(1.3 * cm, height - 0.78 * cm, "ERP SST PRO · Reporte Ejecutivo de Medidas Correctivas")

    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(width - 1.3 * cm, height - 0.78 * cm, datetime.now().strftime("%d/%m/%Y %H:%M"))

    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.setFont("Helvetica", 7)
    canvas.drawString(1.3 * cm, 0.8 * cm, "Documento generado automáticamente por ERP SST PRO.")
    canvas.drawRightString(width - 1.3 * cm, 0.8 * cm, f"Página {doc.page}")

    canvas.restoreState()


def _styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="TitleERP",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=colors.HexColor("#0f172a"),
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=10,
    ))

    styles.add(ParagraphStyle(
        name="SubTitleERP",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=colors.HexColor("#475569"),
        leading=12,
        alignment=TA_CENTER,
        spaceAfter=12,
    ))

    styles.add(ParagraphStyle(
        name="SectionERP",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=colors.HexColor("#1d4ed8"),
        leading=15,
        spaceBefore=8,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="SmallERP",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        textColor=colors.HexColor("#334155"),
        leading=10,
        alignment=TA_LEFT,
    ))

    styles.add(ParagraphStyle(
        name="BadgeERP",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        textColor=colors.HexColor("#0f172a"),
        leading=10,
        alignment=TA_CENTER,
    ))

    return styles


def _table(data, col_widths=None, header=True):
    table = Table(data, colWidths=col_widths, hAlign="LEFT")
    style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]

    if header:
        style.extend([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef4ff")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
        ])

    table.setStyle(TableStyle(style))
    return table


def _evidencia_image_flow(archivo: ArchivoSST, max_width=7.5 * cm, max_height=5.2 * cm):
    path = _public_to_path(_get(archivo, "url", None)) or _public_to_path(_get(archivo, "ruta", None))
    if not path or not path.exists():
        return None

    mime = str(_get(archivo, "mime_type", "") or "").lower()
    ext = str(path.suffix or "").lower()

    if not (mime.startswith("image/") or ext in {".png", ".jpg", ".jpeg", ".webp"}):
        return None

    try:
        img = Image(str(path))
        img._restrictSize(max_width, max_height)
        return img
    except Exception:
        return None


def generar_pdf_medida_correctiva(db: Session, medida_id: int) -> bytes:
    medida = db.query(CapaSST).filter(CapaSST.id == medida_id, CapaSST.activo.is_(True)).first()

    if not medida:
        raise ValueError("Medida correctiva no encontrada")

    seguimientos = (
        db.query(CapaSeguimientoSST)
        .filter(CapaSeguimientoSST.capa_id == medida.id, CapaSeguimientoSST.activo.is_(True))
        .order_by(CapaSeguimientoSST.fecha_seguimiento.asc(), CapaSeguimientoSST.id.asc())
        .all()
    )

    evidencias = (
        db.query(ArchivoSST)
        .filter(
            ArchivoSST.modulo.in_(["CAPA", "MEDIDAS_CORRECTIVAS"]),
            ArchivoSST.referencia_id == medida.id,
            ArchivoSST.activo.is_(True),
        )
        .order_by(ArchivoSST.fecha_creacion.desc())
        .all()
    )

    eficacia_estado, eficacia_msg = _estado_eficacia(medida)
    semaforo, semaforo_color, factores = _semaforo_medida(medida, len(seguimientos), len(evidencias))

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.2 * cm,
        leftMargin=1.2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.3 * cm,
        title=f"Reporte Ejecutivo {_safe(_get(medida, 'codigo', medida.id))}",
    )

    styles = _styles()
    flow = []

    flow.append(Paragraph("REPORTE PDF EJECUTIVO DE MEDIDAS CORRECTIVAS", styles["TitleERP"]))
    flow.append(Paragraph(f"Código: {_safe(_get(medida, 'codigo', None))} · Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["SubTitleERP"]))

    flow.append(Paragraph("1. Resumen ejecutivo", styles["SectionERP"]))
    resumen_data = [
        ["Indicador", "Resultado", "Detalle"],
        ["Estado", _safe(_get(medida, "estado", None)), f"Avance {_fmt_percent(_get(medida, 'avance', 0))}"],
        ["Semáforo", semaforo, f"Color {semaforo_color} · {', '.join(factores)}"],
        ["Eficacia", eficacia_estado, eficacia_msg],
        ["Prioridad", _safe(_get(medida, "prioridad", None)), f"Tipo acción: {_safe(_get(medida, 'tipo_accion', None))}"],
        ["Responsable", _safe(_get(medida, "responsable", None)), f"Compromiso: {_fmt_date(_get(medida, 'fecha_compromiso', None))}"],
        ["Costo", _fmt_money(_get(medida, "costo_real", 0)), f"Estimado: {_fmt_money(_get(medida, 'costo_estimado', 0))}"],
    ]
    flow.append(_table(resumen_data, [4.0 * cm, 4.0 * cm, 9.2 * cm]))
    flow.append(Spacer(1, 0.25 * cm))

    flow.append(Paragraph("2. Identificación de la medida", styles["SectionERP"]))
    detalle_data = [
        ["Campo", "Información"],
        ["Título", Paragraph(_safe(_get(medida, "titulo", None)), styles["SmallERP"])],
        ["Descripción", Paragraph(_safe(_get(medida, "descripcion", None)), styles["SmallERP"])],
        ["Origen", _safe(_get(medida, "origen", None))],
        ["Empresa", _safe(_get(_get(medida, "empresa", None), "nombre", None))],
        ["Sede", _safe(_get(_get(medida, "sede", None), "nombre", None))],
        ["Área", _safe(_get(_get(medida, "area", None), "nombre", None))],
        ["Fecha apertura", _fmt_date(_get(medida, "fecha_apertura", None))],
        ["Fecha cierre", _fmt_date(_get(medida, "fecha_cierre", None))],
    ]
    flow.append(_table(detalle_data, [4.2 * cm, 13.0 * cm]))
    flow.append(Spacer(1, 0.25 * cm))

    flow.append(Paragraph("3. Análisis de causa raíz", styles["SectionERP"]))
    causa_data = [
        ["Elemento", "Detalle"],
        ["Causa raíz", Paragraph(_safe(_get(medida, "causa_raiz", None)), styles["SmallERP"])],
        ["Por qué 1", Paragraph(_safe(_get(medida, "porque_1", None)), styles["SmallERP"])],
        ["Por qué 2", Paragraph(_safe(_get(medida, "porque_2", None)), styles["SmallERP"])],
        ["Por qué 3", Paragraph(_safe(_get(medida, "porque_3", None)), styles["SmallERP"])],
        ["Por qué 4", Paragraph(_safe(_get(medida, "porque_4", None)), styles["SmallERP"])],
        ["Por qué 5", Paragraph(_safe(_get(medida, "porque_5", None)), styles["SmallERP"])],
    ]
    flow.append(_table(causa_data, [4.2 * cm, 13.0 * cm]))
    flow.append(Spacer(1, 0.25 * cm))

    flow.append(Paragraph("4. Plan de acción", styles["SectionERP"]))
    acciones_data = [
        ["Tipo", "Acción"],
        ["Acción inmediata", Paragraph(_safe(_get(medida, "accion_inmediata", None)), styles["SmallERP"])],
        ["Acción correctiva", Paragraph(_safe(_get(medida, "accion_correctiva", None)), styles["SmallERP"])],
        ["Acción preventiva", Paragraph(_safe(_get(medida, "accion_preventiva", None)), styles["SmallERP"])],
    ]
    flow.append(_table(acciones_data, [4.2 * cm, 13.0 * cm]))

    flow.append(PageBreak())

    flow.append(Paragraph("5. Seguimientos", styles["SectionERP"]))
    if seguimientos:
        seguimiento_data = [["Fecha", "Responsable", "Avance", "Comentario / Resultado"]]
        for seg in seguimientos:
            comentario = _safe(_get(seg, "comentario", None) or _get(seg, "resultado", None))
            seguimiento_data.append([
                _fmt_date(_get(seg, "fecha_seguimiento", None)),
                _safe(_get(seg, "responsable", None)),
                _fmt_percent(_get(seg, "avance", 0)),
                Paragraph(comentario, styles["SmallERP"]),
            ])
        flow.append(_table(seguimiento_data, [2.7 * cm, 3.4 * cm, 2.2 * cm, 8.9 * cm]))
    else:
        flow.append(Paragraph("No existen seguimientos registrados.", styles["SmallERP"]))

    flow.append(Spacer(1, 0.25 * cm))

    flow.append(Paragraph("6. Verificación de eficacia", styles["SectionERP"]))
    eficacia_data = [
        ["Resultado", eficacia_estado],
        ["Porcentaje", _fmt_percent(_get(medida, "porcentaje_eficacia", 0))],
        ["Fecha verificación", _fmt_date(_get(medida, "fecha_verificacion_eficacia", None))],
        ["Verificación", Paragraph(_safe(_get(medida, "verificacion_eficacia", None)), styles["SmallERP"])],
        ["Observaciones", Paragraph(_safe(_get(medida, "observaciones", None)), styles["SmallERP"])],
    ]
    flow.append(_table(eficacia_data, [4.2 * cm, 13.0 * cm]))
    flow.append(Spacer(1, 0.25 * cm))

    flow.append(Paragraph("7. Trazabilidad técnica", styles["SectionERP"]))
    trazabilidad_text = _safe(_get(medida, "trazabilidad", None), "Sin trazabilidad registrada.")
    flow.append(_table([["Trazabilidad"], [Paragraph(trazabilidad_text.replace("\n", "<br/>"), styles["SmallERP"])]], [17.2 * cm]))

    flow.append(PageBreak())
    flow.append(Paragraph("8. Evidencias fotográficas y documentales", styles["SectionERP"]))

    if evidencias:
        cards = []
        row = []
        for archivo in evidencias:
            img = _evidencia_image_flow(archivo)
            nombre = Paragraph(
                f"<b>{_safe(_get(archivo, 'nombre_original', None))}</b><br/>"
                f"{_safe(_get(archivo, 'modulo', None))} · {_safe(_get(archivo, 'tipo', None))}<br/>"
                f"{_safe(_get(archivo, 'mime_type', None))}",
                styles["SmallERP"],
            )
            cell = [img, Spacer(1, 0.12 * cm), nombre] if img else [Paragraph("Archivo documental", styles["BadgeERP"]), Spacer(1, 0.12 * cm), nombre]
            row.append(cell)
            if len(row) == 2:
                cards.append(row)
                row = []
        if row:
            row.append("")
            cards.append(row)

        evidence_table = Table(cards, colWidths=[8.3 * cm, 8.3 * cm], hAlign="LEFT")
        evidence_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOX", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        flow.append(evidence_table)
    else:
        flow.append(Paragraph("No existen evidencias asociadas a la medida.", styles["SmallERP"]))

    flow.append(PageBreak())
    flow.append(Paragraph("9. Cierre ejecutivo", styles["SectionERP"]))
    cierre_data = [
        ["Concepto", "Resultado"],
        ["Semáforo", semaforo],
        ["Eficacia", eficacia_estado],
        ["Cumplimiento", "Cerrada" if str(_get(medida, "estado", "") or "").upper() == "CERRADA" else "Pendiente / En gestión"],
        ["Conclusión", Paragraph("Este reporte consolida el ciclo de vida de la medida correctiva, sus acciones, seguimientos, evidencias y verificación de eficacia para fines de auditoría y control SST.", styles["SmallERP"])],
    ]
    flow.append(_table(cierre_data, [4.2 * cm, 13.0 * cm]))

    doc.build(flow, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return buffer.getvalue()

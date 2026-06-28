# ============================================================
# ERP SST ENTERPRISE
# FASE 1.1.8.7.9 — DASHBOARD PDF PLATINUM
# Archivo: backend/app/services/pdf/pdf_dashboard.py
# ============================================================

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from app.services.pdf.pdf_styles import (
    platinum_styles,
    PLATINUM_ACCENT,
    PLATINUM_SUCCESS,
    PLATINUM_WARNING,
    PLATINUM_DANGER,
    PLATINUM_MUTED,
    PLATINUM_LIGHT,
    PLATINUM_BORDER,
    PLATINUM_PRIMARY,
    PLATINUM_SECONDARY,
)


def kpi_card(label: str, value, color=PLATINUM_ACCENT):
    styles = platinum_styles()
    table = Table([
        [Paragraph(str(value), styles["kpi_value"])],
        [Paragraph(label, styles["kpi_label"])],
    ], colWidths=[4.05 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PLATINUM_LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.7, color),
        ("LINEABOVE", (0, 0), (-1, 0), 4, color),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def pie_chart(title: str, values: dict[str, int]):
    drawing = Drawing(235, 160)
    values = {k: v for k, v in (values or {}).items() if v is not None}
    if not values:
        values = {"Sin datos": 1}
    pie = Pie()
    pie.x = 65
    pie.y = 18
    pie.width = 110
    pie.height = 110
    pie.data = list(values.values())
    pie.labels = list(values.keys())
    colors = [PLATINUM_ACCENT, PLATINUM_SUCCESS, PLATINUM_WARNING, PLATINUM_DANGER, PLATINUM_MUTED]
    for i in range(len(pie.data)):
        pie.slices[i].fillColor = colors[i % len(colors)]
    drawing.add(String(10, 145, title, fontName="Helvetica-Bold", fontSize=9, fillColor=PLATINUM_PRIMARY))
    drawing.add(pie)
    return drawing


def bar_chart(title: str, values: dict[str, int]):
    drawing = Drawing(430, 175)
    if not values:
        values = {"Sin datos": 0}
    bc = VerticalBarChart()
    bc.x = 42
    bc.y = 35
    bc.height = 100
    bc.width = 345
    bc.data = [list(values.values())]
    bc.categoryAxis.categoryNames = list(values.keys())
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = max(list(values.values()) + [1]) + 1
    bc.valueAxis.valueStep = 1
    bc.bars[0].fillColor = PLATINUM_ACCENT
    drawing.add(String(10, 158, title, fontName="Helvetica-Bold", fontSize=10, fillColor=PLATINUM_PRIMARY))
    drawing.add(bc)
    return drawing


def build_dashboard(metrics: dict):
    styles = platinum_styles()
    story = [Paragraph("Dashboard Ejecutivo SST", styles["section"])]
    cumplimiento = metrics.get("cumplimiento", 0)
    cumplimiento_color = PLATINUM_SUCCESS if float(cumplimiento or 0) >= 80 else PLATINUM_WARNING
    kpis = Table([
        [
            kpi_card("Hallazgos", metrics.get("total_hallazgos", 0), PLATINUM_ACCENT),
            kpi_card("Abiertos", metrics.get("abiertos", 0), PLATINUM_WARNING),
            kpi_card("Cerrados", metrics.get("cerrados", 0), PLATINUM_SUCCESS),
            kpi_card("Vencidos", metrics.get("vencidos", 0), PLATINUM_DANGER),
        ],
        [
            kpi_card("CAPA", metrics.get("total_capas", 0), PLATINUM_SECONDARY),
            kpi_card("Evidencias", metrics.get("total_evidencias", 0), PLATINUM_ACCENT),
            kpi_card("Cumplimiento", f"{cumplimiento}%", cumplimiento_color),
            kpi_card("Riesgo", metrics.get("nivel_riesgo", "N/A"), PLATINUM_MUTED),
        ],
    ], colWidths=[4.2 * cm, 4.2 * cm, 4.2 * cm, 4.2 * cm])
    kpis.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(kpis)
    story.append(Spacer(1, 0.5 * cm))
    charts = Table([[pie_chart("Distribución por nivel de riesgo", metrics.get("niveles", {})), pie_chart("Distribución por estado", metrics.get("estados", {}))]], colWidths=[8.4 * cm, 8.4 * cm])
    charts.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.3, PLATINUM_BORDER), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(charts)
    story.append(Spacer(1, 0.3 * cm))
    story.append(bar_chart("Hallazgos por nivel", metrics.get("niveles", {})))
    return story

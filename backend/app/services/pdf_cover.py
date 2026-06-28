# ============================================================
# ERP SST ENTERPRISE
# FASE 1.1.8.7.9 — PORTADA PREMIUM PDF PLATINUM
# Archivo: backend/app/services/pdf/pdf_cover.py
# ============================================================

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image

from app.services.pdf.pdf_styles import (
    platinum_styles,
    PLATINUM_PRIMARY,
    PLATINUM_ACCENT,
    PLATINUM_LIGHT,
    PLATINUM_BORDER,
    PLATINUM_WHITE,
)


def build_cover(info: dict, qr_path: str | None = None):
    """Construye portada ejecutiva Premium."""
    styles = platinum_styles()
    story = []

    story.append(Spacer(1, 0.8 * cm))

    hero = Table(
        [[
            Paragraph("REPORTE PDF EJECUTIVO PLATINUM", styles["cover_title"]),
        ], [
            Paragraph("Inspección SST · Evidencias · CAPA · Seguimientos · Trazabilidad", styles["cover_subtitle"]),
        ]],
        colWidths=[17 * cm],
        rowHeights=[1.2 * cm, 0.8 * cm],
    )
    hero.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PLATINUM_PRIMARY),
        ("BOX", (0, 0), (-1, -1), 1, PLATINUM_PRIMARY),
        ("LINEBELOW", (0, 1), (-1, 1), 4, PLATINUM_ACCENT),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(hero)
    story.append(Spacer(1, 0.7 * cm))

    rows = [
        ["Empresa", info.get("empresa", "N/A")],
        ["Sede", info.get("sede", "N/A")],
        ["Área", info.get("area", "N/A")],
        ["Código inspección", info.get("codigo", "N/A")],
        ["Título", info.get("titulo", "N/A")],
        ["Fecha inspección", info.get("fecha_inspeccion", "N/A")],
        ["Estado", info.get("estado", "N/A")],
        ["Nivel de riesgo", info.get("nivel_riesgo", "N/A")],
        ["Responsable", info.get("responsable", "N/A")],
        ["Generado por", info.get("usuario", "Sistema")],
        ["Fecha generación", info.get("fecha_generacion", "N/A")],
        ["Hash documental", info.get("hash", "N/A")],
    ]

    table_rows = [[Paragraph(f"<b>{a}</b>", styles["normal"]), Paragraph(str(b), styles["normal"])] for a, b in rows]
    t = Table(table_rows, colWidths=[5 * cm, 12 * cm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, PLATINUM_BORDER),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e2e8f0")),
        ("BACKGROUND", (1, 0), (1, -1), PLATINUM_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5 * cm))

    if qr_path:
        qr = Table([[Paragraph("<b>Verificación documental</b><br/>Código QR de trazabilidad para validar origen, fecha, usuario y hash del reporte.", styles["normal"]), Image(qr_path, 3 * cm, 3 * cm)]], colWidths=[13.5 * cm, 3.5 * cm])
        qr.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.5, PLATINUM_BORDER),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(qr)

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("Documento generado automáticamente por ERP SST Enterprise. Uso recomendado para auditorías internas, revisión gerencial y trazabilidad del SG-SST.", styles["small_center"]))
    return story

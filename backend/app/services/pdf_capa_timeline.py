# ============================================================
# ERP SST ENTERPRISE
# FASE 1.1.8.7.9 — TIMELINE CAPA PDF PLATINUM
# Archivo: backend/app/services/pdf/pdf_capa_timeline.py
# ============================================================

from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from app.services.pdf.pdf_styles import platinum_styles, PLATINUM_BORDER, PLATINUM_LIGHT, PLATINUM_ACCENT, PLATINUM_SUCCESS


def build_capa_timeline(seguimientos: list[dict]):
    """Crea timeline visual de seguimientos CAPA."""
    styles = platinum_styles()
    story = [Paragraph("Timeline de Seguimientos CAPA", styles["subsection"])]
    if not seguimientos:
        story.append(Paragraph("No se registran seguimientos CAPA.", styles["normal"]))
        return story
    rows = []
    for idx, seg in enumerate(seguimientos, start=1):
        bullet = f"● {idx}"
        fecha = seg.get("fecha", "N/A")
        responsable = seg.get("responsable", "N/A")
        avance = seg.get("avance", "0")
        estado = seg.get("estado", "EN_SEGUIMIENTO")
        comentario = seg.get("comentario", "N/A")
        rows.append([
            Paragraph(f"<b>{bullet}</b>", styles["normal"]),
            Paragraph(f"<b>{fecha}</b><br/>{responsable}<br/>Avance: {avance}%", styles["normal"]),
            Paragraph(f"<b>{estado}</b><br/>{comentario}", styles["normal"]),
        ])
    table = Table(rows, colWidths=[1.5 * cm, 4.2 * cm, 11.2 * cm])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, PLATINUM_BORDER),
        ("BACKGROUND", (0, 0), (0, -1), PLATINUM_ACCENT),
        ("BACKGROUND", (1, 0), (-1, -1), PLATINUM_LIGHT),
        ("TEXTCOLOR", (0, 0), (0, -1), PLATINUM_SUCCESS),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3 * cm))
    return story

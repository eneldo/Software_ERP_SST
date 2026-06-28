# ============================================================
# ERP SST ENTERPRISE
# FASE 1.1.8.7.9 — FIRMAS PDF PLATINUM
# Archivo: backend/app/services/pdf/pdf_signature.py
# ============================================================

from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from app.services.pdf.pdf_styles import platinum_styles, PLATINUM_BORDER, PLATINUM_LIGHT, PLATINUM_SECONDARY


def build_signatures(firmas: list[dict]):
    """Construye bloque corporativo de firmas."""
    styles = platinum_styles()
    story = [Paragraph("Firmas y Validación Digital", styles["section"])]
    if not firmas:
        firmas = [{"rol": "Inspector", "nombre": "N/A", "fecha": "N/A"}, {"rol": "Responsable SST", "nombre": "N/A", "fecha": "N/A"}]
    rows = []
    for f in firmas:
        rows.append([
            Paragraph("<br/><br/>______________________________", styles["normal"]),
            Paragraph(f"<b>{f.get('rol','N/A')}</b><br/>{f.get('nombre','N/A')}<br/>Fecha: {f.get('fecha','N/A')}", styles["normal"]),
        ])
    table = Table(rows, colWidths=[8 * cm, 8.8 * cm])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, PLATINUM_BORDER),
        ("BACKGROUND", (0, 0), (-1, -1), PLATINUM_LIGHT),
        ("LINEABOVE", (0, 0), (-1, 0), 3, PLATINUM_SECONDARY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.35 * cm))
    story.append(Paragraph("Este reporte consolida la inspección, hallazgos, evidencias, CAPA, seguimientos, eficacia y trazabilidad para fines de auditoría y control SST.", styles["small"]))
    return story

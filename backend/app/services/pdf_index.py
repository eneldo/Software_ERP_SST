# ============================================================
# ERP SST ENTERPRISE
# FASE 1.1.8.7.9 — ÍNDICE PDF PLATINUM
# Archivo: backend/app/services/pdf/pdf_index.py
# ============================================================

from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from app.services.pdf.pdf_styles import platinum_styles, PLATINUM_BORDER, PLATINUM_LIGHT, PLATINUM_SECONDARY


def build_index(sections: list[tuple[str, str]] | None = None):
    """Construye índice visual. Las páginas son referenciales por ser generación dinámica."""
    styles = platinum_styles()
    sections = sections or [
        ("1", "Portada corporativa"),
        ("2", "Índice del reporte"),
        ("3", "Dashboard ejecutivo SST"),
        ("4", "Información general de la inspección"),
        ("5", "Hallazgos identificados"),
        ("6", "Evidencias fotográficas"),
        ("7", "CAPA completa asociada"),
        ("8", "Seguimientos y trazabilidad CAPA"),
        ("9", "Firmas y validación digital"),
    ]
    story = [Paragraph("Índice del Reporte", styles["section"]), Spacer(1, 0.2 * cm)]
    rows = [[Paragraph("<b>Sección</b>", styles["normal"]), Paragraph("<b>Contenido</b>", styles["normal"])]]
    for num, text in sections:
        rows.append([Paragraph(num, styles["normal"]), Paragraph(text, styles["normal"])])
    table = Table(rows, colWidths=[3 * cm, 13.8 * cm])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, PLATINUM_BORDER),
        ("BACKGROUND", (0, 0), (-1, 0), PLATINUM_SECONDARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), PLATINUM_LIGHT),
        ("BACKGROUND", (0, 1), (-1, -1), PLATINUM_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("Nota: La numeración final de páginas se calcula automáticamente en el encabezado del documento. Este índice resume la estructura ejecutiva del reporte.", styles["small"]))
    return story

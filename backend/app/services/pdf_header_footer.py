# ============================================================
# ERP SST ENTERPRISE
# ------------------------------------------------------------
# Módulo      : Inspecciones SST
# Fase        : 1.1.8.7.9
# Archivo     : pdf_header_footer.py
# Ubicación   : backend/app/services/pdf/
# ------------------------------------------------------------
# Descripción:
# Encabezado y pie de página corporativo para PDF Platinum.
# ============================================================

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors

from app.services.pdf.pdf_styles import (
    PLATINUM_PRIMARY,
    PLATINUM_ACCENT,
    PLATINUM_MUTED,
    PLATINUM_BORDER,
)


def draw_platinum_header_footer(canvas, doc, metadata: dict):
    """Dibuja encabezado y pie corporativo en cada página."""
    canvas.saveState()
    width, height = A4

    codigo = metadata.get("codigo", "N/A")
    empresa = metadata.get("empresa", "ERP SST Enterprise")
    usuario = metadata.get("usuario", "Sistema")
    fecha = metadata.get("fecha_generacion", "")
    hash_doc = metadata.get("hash", "")

    # Encabezado principal
    canvas.setFillColor(PLATINUM_PRIMARY)
    canvas.rect(0, height - 1.22 * cm, width, 1.22 * cm, fill=True, stroke=False)

    # Línea de acento
    canvas.setFillColor(PLATINUM_ACCENT)
    canvas.rect(0, height - 1.27 * cm, width, 0.05 * cm, fill=True, stroke=False)

    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(1.2 * cm, height - 0.74 * cm, "ERP SST ENTERPRISE · REPORTE EJECUTIVO PLATINUM")

    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(width - 1.2 * cm, height - 0.74 * cm, f"Código: {codigo} · Página {doc.page}")

    # Pie de página
    canvas.setStrokeColor(PLATINUM_BORDER)
    canvas.line(1.2 * cm, 1.32 * cm, width - 1.2 * cm, 1.32 * cm)

    canvas.setFillColor(PLATINUM_MUTED)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(1.2 * cm, 0.9 * cm, f"{empresa} · Generado: {fecha} · Usuario: {usuario}")
    canvas.drawRightString(width - 1.2 * cm, 0.9 * cm, f"Hash: {hash_doc}")

    canvas.restoreState()

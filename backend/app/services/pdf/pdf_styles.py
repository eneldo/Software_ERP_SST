# ============================================================
# ERP SST ENTERPRISE
# ------------------------------------------------------------
# Módulo      : Inspecciones SST
# Fase        : 1.1.8.7.9
# Archivo     : pdf_styles.py
# Ubicación   : backend/app/services/pdf/
# Versión     : Enterprise Platinum Final
# ------------------------------------------------------------
# Descripción:
# Estilos centralizados para el Reporte PDF Ejecutivo Platinum.
# ============================================================

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

# ============================================================
# PALETA CORPORATIVA PLATINUM
# ============================================================

PLATINUM_PRIMARY = colors.HexColor("#0f172a")
PLATINUM_SECONDARY = colors.HexColor("#1e3a8a")
PLATINUM_ACCENT = colors.HexColor("#2563eb")
PLATINUM_ACCENT_2 = colors.HexColor("#0891b2")
PLATINUM_SUCCESS = colors.HexColor("#16a34a")
PLATINUM_WARNING = colors.HexColor("#f59e0b")
PLATINUM_DANGER = colors.HexColor("#dc2626")
PLATINUM_MUTED = colors.HexColor("#64748b")
PLATINUM_SOFT = colors.HexColor("#e2e8f0")
PLATINUM_LIGHT = colors.HexColor("#f8fafc")
PLATINUM_WHITE = colors.white
PLATINUM_BORDER = colors.HexColor("#cbd5e1")
PLATINUM_DARK_BORDER = colors.HexColor("#94a3b8")

RISK_COLORS = {
    "CRITICO": PLATINUM_DANGER,
    "CRÍTICO": PLATINUM_DANGER,
    "ALTO": PLATINUM_DANGER,
    "MEDIO": PLATINUM_WARNING,
    "BAJO": PLATINUM_SUCCESS,
}

STATUS_COLORS = {
    "CERRADA": PLATINUM_SUCCESS,
    "CERRADO": PLATINUM_SUCCESS,
    "FINALIZADA": PLATINUM_SUCCESS,
    "ABIERTA": PLATINUM_WARNING,
    "ABIERTO": PLATINUM_WARNING,
    "EN_PROCESO": PLATINUM_ACCENT,
    "EN SEGUIMIENTO": PLATINUM_ACCENT,
    "VERIFICACION": PLATINUM_ACCENT_2,
    "VERIFICACIÓN": PLATINUM_ACCENT_2,
    "VENCIDA": PLATINUM_DANGER,
    "VENCIDO": PLATINUM_DANGER,
}

# ============================================================
# FUNCIONES DE ESTILO
# ============================================================

def platinum_styles():
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "cover_title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=29,
            textColor=PLATINUM_WHITE,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=PLATINUM_SOFT,
            alignment=TA_CENTER,
            spaceAfter=10,
        ),
        # Backwards compatibility: some callers expect `subtitle` key
        "subtitle": ParagraphStyle(
            "subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=PLATINUM_SOFT,
            alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=26,
            textColor=PLATINUM_PRIMARY,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "section": ParagraphStyle(
            "section",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=PLATINUM_SECONDARY,
            spaceBefore=10,
            spaceAfter=8,
        ),
        "subsection": ParagraphStyle(
            "subsection",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=PLATINUM_PRIMARY,
            spaceBefore=8,
            spaceAfter=6,
        ),
        "normal": ParagraphStyle(
            "normal",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11.5,
            textColor=PLATINUM_PRIMARY,
            alignment=TA_LEFT,
        ),
        "normal_justify": ParagraphStyle(
            "normal_justify",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11.5,
            textColor=PLATINUM_PRIMARY,
            alignment=TA_JUSTIFY,
        ),
        "small": ParagraphStyle(
            "small",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=PLATINUM_MUTED,
        ),
        "small_center": ParagraphStyle(
            "small_center",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=PLATINUM_MUTED,
            alignment=TA_CENTER,
        ),
        "kpi_value": ParagraphStyle(
            "kpi_value",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=PLATINUM_SECONDARY,
            alignment=TA_CENTER,
        ),
        "kpi_label": ParagraphStyle(
            "kpi_label",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=PLATINUM_MUTED,
            alignment=TA_CENTER,
        ),
        "index_line": ParagraphStyle(
            "index_line",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=PLATINUM_PRIMARY,
        ),
        "footer": ParagraphStyle(
            "footer",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=PLATINUM_MUTED,
            alignment=TA_RIGHT,
        ),
    }


def risk_color(value: str):
    value = (value or "").upper().strip()
    return RISK_COLORS.get(value, PLATINUM_MUTED)


def status_color(value: str):
    value = (value or "").upper().strip()
    return STATUS_COLORS.get(value, PLATINUM_ACCENT)


# Backwards compatibility: alias expected by older modules
def get_platinum_styles():
    """
    Compat wrapper for legacy callers that import `get_platinum_styles`.
    Returns the dict produced by `platinum_styles()`.
    """
    return platinum_styles()

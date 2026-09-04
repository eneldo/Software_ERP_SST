# ============================================================
# SERVICIO PDF CORPORATIVO SST
# FASE 2.2.1C - Motor de Exportación Corporativo SST
# ============================================================

from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.units import cm


def generar_pdf_corporativo(
    titulo: str,
    codigo: str,
    empresa,
    configuracion=None,
    columnas=None,
    filas=None,
    orientacion: str = "vertical",
    encabezado_extra: list = None,
    firma_representante: dict = None,
    firma_responsable: dict = None,
):
    """
    Genera PDF corporativo reutilizable para documentos SG-SST.
    """

    buffer = BytesIO()

    page_size = landscape(A4) if orientacion == "horizontal" else A4

    doc = SimpleDocTemplate(
        buffer,
        pagesize=page_size,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    elementos = []

    prefijo = configuracion.prefijo_documental if configuracion else "SGSST"
    version = configuracion.version_documental if configuracion else "1.0"
    pie = (
        configuracion.pie_documental
        if configuracion
        else "Documento controlado generado desde ERP SST PRO."
    )

    encabezado = [
        [
            Paragraph(f"<b>{empresa.nombre}</b><br/>NIT: {empresa.nit}", styles["Normal"]),
            Paragraph(
                f"<b>{titulo}</b><br/>Código: {prefijo}-{codigo}<br/>Versión: {version}",
                styles["Normal"],
            ),
        ]
    ]

    tabla_encabezado = Table(encabezado, colWidths=[9 * cm, 8 * cm])
    tabla_encabezado.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    elementos.append(tabla_encabezado)
    elementos.append(Spacer(1, 18))

    if encabezado_extra:
        for linea in encabezado_extra:
            elementos.append(Paragraph(linea, styles["Normal"]))
        elementos.append(Spacer(1, 10))

    elementos.append(Paragraph(f"<b>{titulo}</b>", styles["Title"]))
    elementos.append(Spacer(1, 12))

    columnas = columnas or []
    filas = filas or []

    data = [columnas] + filas if columnas else filas

    if data:
        tabla = Table(data, repeatRows=1)
        tabla.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elementos.append(tabla)

    elementos.append(Spacer(1, 35))

    firmas = [
        [
            Paragraph(
                "<br/><br/>_________________________<br/>"
                f"<b>Representante Legal / Empleador</b><br/>"
                f"{firma_representante.get('nombre', '')}<br/>"
                f"<i>{firma_representante.get('cargo', '')}</i>" if firma_representante else
                "<br/><br/>_________________________<br/><b>Representante Legal</b>",
                styles["Normal"],
            ),
            Paragraph(
                "<br/><br/>_________________________<br/>"
                f"<b>Responsable SG-SST</b><br/>"
                f"{firma_responsable.get('nombre', '')}<br/>"
                f"<i>{firma_responsable.get('cargo', '')}</i>" if firma_responsable else
                "<br/><br/>_________________________<br/><b>Responsable SST</b>",
                styles["Normal"],
            ),
        ]
    ]

    tabla_firmas = Table(firmas, colWidths=[8 * cm, 8 * cm])
    tabla_firmas.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    elementos.append(tabla_firmas)
    elementos.append(Spacer(1, 20))

    elementos.append(
        Paragraph(
            f"{pie}<br/>Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            styles["Normal"],
        )
    )

    doc.build(elementos)

    buffer.seek(0)
    return buffer
# ============================================================
# SERVICE PDF ENTERPRISE AVANZADO
# AUDITORÍA SST
# FASE 1.7.4.2.5.1
# Logo + QR + KPI + Evidencias + Firma + SHA256 + Código Validación
# Archivo: backend/app/services/auditoria_pdf_service.py
# ============================================================

from io import BytesIO
from datetime import datetime
from pathlib import Path
import os
import re

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    Image,
    KeepTogether,
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.barcode.qr import QrCodeWidget

from app.models.auditoria_sst import AuditoriaSST
from app.models.auditoria_hallazgo_evidencia import AuditoriaHallazgoEvidenciaSST
from app.models.firma_digital import FirmaDigitalSST
from app.models.documento_validacion import DocumentoValidacionSST
from app.services.documento_validacion_service import (
    calcular_hash_sha256,
    generar_codigo_validacion,
)


BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads"))
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")


# ============================================================
# UTILIDADES
# ============================================================

def texto(valor, defecto=""):
    return str(valor) if valor not in [None, ""] else defecto


def normalizar_fecha(valor):
    return str(valor) if valor else "Sin fecha"


def limpiar_html(valor):
    if not valor:
        return ""
    return re.sub(r"<[^>]*>", "", str(valor))


def path_seguro(valor):
    if not valor:
        return None

    valor = str(valor).strip().replace("\\", "/")

    if valor.startswith("http://") or valor.startswith("https://"):
        return None

    if valor.startswith("/uploads/"):
        posible = BASE_DIR / valor.lstrip("/")
    elif valor.startswith("uploads/"):
        posible = BASE_DIR / valor
    else:
        posible = Path(valor)

    if posible.exists():
        return posible

    posible_upload = UPLOAD_DIR / valor.lstrip("/")
    if posible_upload.exists():
        return posible_upload

    return None


def buscar_logo_empresa(empresa):
    if not empresa:
        return None

    for campo in ["logo_url", "logo", "ruta_logo", "logo_path", "imagen_logo"]:
        ruta = path_seguro(getattr(empresa, campo, None))
        if ruta:
            return ruta

    return None


def buscar_firma_auditor(db: Session, auditoria):
    if not auditoria.usuario_id:
        return None

    firma = (
        db.query(FirmaDigitalSST)
        .filter(
            FirmaDigitalSST.usuario_id == auditoria.usuario_id,
            FirmaDigitalSST.activo == True,
        )
        .order_by(FirmaDigitalSST.id.desc())
        .first()
    )

    if not firma:
        return None

    return path_seguro(firma.url) or path_seguro(firma.archivo)


def evidencia_como_imagen(hallazgo):
    ruta = path_seguro(getattr(hallazgo, "evidencia", None))

    if not ruta:
        return None

    if ruta.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
        return ruta

    return None


def obtener_imagenes_hallazgo(db: Session, hallazgo_id: int):
    evidencias = (
        db.query(AuditoriaHallazgoEvidenciaSST)
        .filter(
            AuditoriaHallazgoEvidenciaSST.hallazgo_id == hallazgo_id,
            AuditoriaHallazgoEvidenciaSST.activo == True,
        )
        .order_by(AuditoriaHallazgoEvidenciaSST.id.asc())
        .all()
    )

    imagenes = []

    for evidencia in evidencias:
        ruta = path_seguro(evidencia.url) or path_seguro(evidencia.archivo)

        if not ruta:
            continue

        if ruta.suffix.lower() not in [".png", ".jpg", ".jpeg", ".webp"]:
            continue

        imagenes.append(
            {
                "ruta": ruta,
                "descripcion": evidencia.descripcion,
                "nombre_original": evidencia.nombre_original,
                "tipo": evidencia.tipo,
            }
        )

    return imagenes


def calcular_resumen_hallazgos(hallazgos):
    activos = [h for h in hallazgos if getattr(h, "activo", True)]

    total = len(activos)
    no_conformidades = len([h for h in activos if h.tipo_hallazgo == "NO_CONFORMIDAD"])
    observaciones = len([h for h in activos if h.tipo_hallazgo == "OBSERVACION"])
    oportunidades = len([h for h in activos if h.tipo_hallazgo == "OPORTUNIDAD_MEJORA"])

    abiertos = len([h for h in activos if h.estado == "ABIERTO"])
    en_proceso = len([h for h in activos if h.estado == "EN_PROCESO"])
    cerrados = len([h for h in activos if h.estado == "CERRADO"])
    planes_generados = len([h for h in activos if h.plan_mejoramiento_id])

    cumplimiento = round((cerrados / total) * 100, 2) if total else 0

    riesgo = "BAJO"

    if no_conformidades > 0 or abiertos >= 3:
        riesgo = "ALTO"
    elif abiertos > 0 or en_proceso > 0:
        riesgo = "MEDIO"

    return {
        "total": total,
        "no_conformidades": no_conformidades,
        "observaciones": observaciones,
        "oportunidades": oportunidades,
        "abiertos": abiertos,
        "en_proceso": en_proceso,
        "cerrados": cerrados,
        "planes_generados": planes_generados,
        "cumplimiento": cumplimiento,
        "riesgo": riesgo,
    }


def registrar_validacion_pdf(
    db: Session,
    auditoria,
    codigo_validacion: str,
    pdf: bytes,
):
    hash_pdf = calcular_hash_sha256(pdf)

    nombre_archivo = f"auditoria_sst_{auditoria.id}.pdf"

    registro = DocumentoValidacionSST(
        codigo_validacion=codigo_validacion,
        tipo_documento="AUDITORIA_SST",
        referencia_id=auditoria.id,
        empresa_id=auditoria.empresa_id,
        usuario_id=auditoria.usuario_id,
        nombre_archivo=nombre_archivo,
        hash_sha256=hash_pdf,
        url_archivo=None,
        estado="VALIDO",
        observacion="PDF de auditoría SST generado automáticamente desde ERP SST PRO.",
    )

    db.add(registro)
    db.commit()
    db.refresh(registro)

    return registro


# ============================================================
# ESTILOS PDF
# ============================================================

def crear_estilos():
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="TituloPrincipal",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=22,
            leading=28,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=16,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SubTitulo",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1d4ed8"),
            spaceAfter=10,
        )
    )

    styles.add(
        ParagraphStyle(
            name="Seccion",
            parent=styles["Heading1"],
            fontSize=15,
            leading=20,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=12,
            spaceAfter=10,
        )
    )

    styles.add(
        ParagraphStyle(
            name="Texto",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
            alignment=TA_LEFT,
        )
    )

    styles.add(
        ParagraphStyle(
            name="TextoCentro",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
            alignment=TA_CENTER,
        )
    )

    styles.add(
        ParagraphStyle(
            name="Mini",
            parent=styles["Normal"],
            fontSize=7,
            leading=9,
            textColor=colors.HexColor("#64748b"),
        )
    )

    return styles


def encabezado_pie(canvas, doc):
    canvas.saveState()

    width, height = A4

    canvas.setFillColor(colors.HexColor("#0f172a"))
    canvas.rect(0, height - 1.2 * cm, width, 1.2 * cm, fill=True, stroke=False)

    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(
        1.5 * cm,
        height - 0.75 * cm,
        "ERP SST PRO · Reporte Profesional de Auditoría SST",
    )

    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(width - 1.5 * cm, height - 0.75 * cm, f"Página {doc.page}")

    canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
    canvas.line(1.5 * cm, 1.25 * cm, width - 1.5 * cm, 1.25 * cm)

    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(
        width / 2,
        0.8 * cm,
        "Documento generado automáticamente por ERP SST PRO · Sistema de Gestión de Seguridad y Salud en el Trabajo",
    )

    canvas.restoreState()


def tabla_estandar(data, col_widths=None, header=True):
    table = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)

    style = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#334155")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]

    if header:
        style.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )

    table.setStyle(TableStyle(style))
    return table


# ============================================================
# QR Y GRÁFICAS
# ============================================================

def crear_qr(validacion_texto):
    qr = QrCodeWidget(validacion_texto)

    dibujo = Drawing(3.4 * cm, 3.4 * cm)
    qr.barWidth = 3.4 * cm
    qr.barHeight = 3.4 * cm
    dibujo.add(qr)

    return dibujo


def crear_grafica_kpi(resumen):
    datos = [
        resumen["total"],
        resumen["abiertos"],
        resumen["en_proceso"],
        resumen["cerrados"],
        resumen["planes_generados"],
    ]

    dibujo = Drawing(16 * cm, 7 * cm)

    chart = VerticalBarChart()
    chart.x = 1.2 * cm
    chart.y = 1.2 * cm
    chart.height = 4.7 * cm
    chart.width = 13.5 * cm
    chart.data = [datos]
    chart.categoryAxis.categoryNames = [
        "Total",
        "Abiertos",
        "Proceso",
        "Cerrados",
        "Planes",
    ]

    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(datos + [1])
    chart.valueAxis.valueStep = 1

    chart.bars[0].fillColor = colors.HexColor("#2563eb")

    chart.categoryAxis.labels.fontSize = 7
    chart.valueAxis.labels.fontSize = 7

    dibujo.add(chart)

    return dibujo


# ============================================================
# PDF PRINCIPAL
# ============================================================

def generar_pdf_auditoria(db: Session, auditoria_id: int):
    auditoria = (
        db.query(AuditoriaSST)
        .options(
            joinedload(AuditoriaSST.hallazgos),
            joinedload(AuditoriaSST.empresa),
        )
        .filter(
            AuditoriaSST.id == auditoria_id,
            AuditoriaSST.activo == True,
        )
        .first()
    )

    if not auditoria:
        raise HTTPException(
            status_code=404,
            detail="Auditoría SST no encontrada",
        )

    styles = crear_estilos()
    resumen = calcular_resumen_hallazgos(auditoria.hallazgos or [])

    empresa = auditoria.empresa
    empresa_nombre = texto(getattr(empresa, "nombre", None), "Empresa no registrada")
    empresa_nit = texto(getattr(empresa, "nit", None), "NIT no registrado")
    logo_empresa = buscar_logo_empresa(empresa)
    firma_auditor = buscar_firma_auditor(db, auditoria)

    codigo_validacion = generar_codigo_validacion(
        tipo="AUDITORIA_SST",
        referencia_id=auditoria.id,
    )

    url_validacion = f"{PUBLIC_BASE_URL}/validar/documento/{codigo_validacion}"

    validacion_qr = (
        f"ERP SST PRO\n"
        f"Documento: Auditoría SST\n"
        f"Código validación: {codigo_validacion}\n"
        f"Auditoría: {auditoria.codigo}\n"
        f"Empresa: {empresa_nombre}\n"
        f"NIT: {empresa_nit}\n"
        f"URL: {url_validacion}"
    )

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=2.0 * cm,
        bottomMargin=1.8 * cm,
        title=f"Reporte Auditoría SST {auditoria.codigo}",
    )

    elementos = []

    # ========================================================
    # PORTADA
    # ========================================================

    logo_elemento = (
        Image(str(logo_empresa), width=3.5 * cm, height=2.2 * cm, kind="proportional")
        if logo_empresa
        else Paragraph("<b>ERP SST PRO</b>", styles["SubTitulo"])
    )

    titulo_elemento = Paragraph(
        "REPORTE PROFESIONAL DE AUDITORÍA SST",
        styles["TituloPrincipal"],
    )

    elementos.append(
        tabla_estandar(
            [[logo_elemento, titulo_elemento]],
            col_widths=[4 * cm, 12 * cm],
            header=False,
        )
    )

    elementos.append(Spacer(1, 0.7 * cm))

    portada_data = [
        ["Código Auditoría", texto(auditoria.codigo)],
        ["Código Validación", codigo_validacion],
        ["Nombre Auditoría", texto(auditoria.nombre)],
        ["Empresa", empresa_nombre],
        ["NIT", empresa_nit],
        ["Tipo Auditoría", texto(auditoria.tipo_auditoria)],
        ["Estado", texto(auditoria.estado)],
        ["Auditor líder", texto(auditoria.auditor_lider, "Sin auditor líder")],
        ["Fecha generación", datetime.now().strftime("%Y-%m-%d %H:%M")],
    ]

    elementos.append(tabla_estandar(portada_data, col_widths=[5 * cm, 11 * cm], header=False))
    elementos.append(Spacer(1, 0.6 * cm))

    riesgo_color = {
        "ALTO": "#dc2626",
        "MEDIO": "#d97706",
        "BAJO": "#16a34a",
    }.get(resumen["riesgo"], "#334155")

    elementos.append(
        Paragraph(
            f"<b>Nivel de riesgo:</b> "
            f"<font color='{riesgo_color}'>{resumen['riesgo']}</font>",
            styles["SubTitulo"],
        )
    )

    elementos.append(Spacer(1, 0.5 * cm))

    elementos.append(
        Paragraph(
            "Este informe consolida los resultados de la auditoría SST, "
            "incluyendo hallazgos, no conformidades, estado de cierre, "
            "planes de mejoramiento asociados, evidencias fotográficas, "
            "conclusiones, recomendaciones, firma electrónica, código único "
            "de validación documental y QR de verificación.",
            styles["Texto"],
        )
    )

    elementos.append(Spacer(1, 0.7 * cm))

    elementos.append(
        tabla_estandar(
            [
                [
                    crear_qr(validacion_qr),
                    Paragraph(
                        "<b>QR de validación documental</b><br/>"
                        f"Código único: <b>{codigo_validacion}</b><br/>"
                        "Escanee este código o consulte el endpoint de validación documental.",
                        styles["Texto"],
                    ),
                ]
            ],
            col_widths=[4 * cm, 12 * cm],
            header=False,
        )
    )

    elementos.append(PageBreak())

    # ========================================================
    # RESUMEN + GRÁFICA
    # ========================================================

    elementos.append(Paragraph("1. Resumen Ejecutivo", styles["Seccion"]))

    resumen_data = [
        ["Indicador", "Valor"],
        ["Total hallazgos", resumen["total"]],
        ["No conformidades", resumen["no_conformidades"]],
        ["Observaciones", resumen["observaciones"]],
        ["Oportunidades de mejora", resumen["oportunidades"]],
        ["Hallazgos abiertos", resumen["abiertos"]],
        ["Hallazgos en proceso", resumen["en_proceso"]],
        ["Hallazgos cerrados", resumen["cerrados"]],
        ["Planes de mejoramiento generados", resumen["planes_generados"]],
        ["Cumplimiento hallazgos", f"{resumen['cumplimiento']}%"],
        ["Riesgo", resumen["riesgo"]],
    ]

    elementos.append(tabla_estandar(resumen_data, col_widths=[9 * cm, 7 * cm]))
    elementos.append(Spacer(1, 0.5 * cm))
    elementos.append(Paragraph("Gráfica KPI de Hallazgos", styles["SubTitulo"]))
    elementos.append(crear_grafica_kpi(resumen))
    elementos.append(Spacer(1, 0.6 * cm))

    # ========================================================
    # INFORMACIÓN GENERAL
    # ========================================================

    elementos.append(Paragraph("2. Información General de la Auditoría", styles["Seccion"]))

    info_data = [
        ["Campo", "Detalle"],
        ["Objetivo", texto(auditoria.objetivo, "Sin objetivo registrado")],
        ["Alcance", texto(auditoria.alcance, "Sin alcance registrado")],
        ["Criterio", texto(auditoria.criterio, "Sin criterio registrado")],
        ["Equipo auditor", texto(auditoria.equipo_auditor, "Sin equipo auditor registrado")],
        ["Fecha programada", normalizar_fecha(auditoria.fecha_programada)],
        ["Fecha inicio", normalizar_fecha(auditoria.fecha_inicio)],
        ["Fecha cierre", normalizar_fecha(auditoria.fecha_cierre)],
    ]

    elementos.append(tabla_estandar(info_data, col_widths=[5 * cm, 11 * cm]))
    elementos.append(Spacer(1, 0.6 * cm))

    # ========================================================
    # TIMELINE
    # ========================================================

    elementos.append(Paragraph("3. Timeline de Auditoría", styles["Seccion"]))

    timeline_data = [
        ["Etapa", "Estado / Fecha"],
        ["Programación", normalizar_fecha(auditoria.fecha_programada)],
        ["Inicio auditoría", normalizar_fecha(auditoria.fecha_inicio)],
        ["Registro de hallazgos", f"{resumen['total']} hallazgos registrados"],
        ["Planes generados", f"{resumen['planes_generados']} planes generados"],
        ["Cierre auditoría", f"{resumen['cumplimiento']}% de hallazgos cerrados"],
    ]

    elementos.append(tabla_estandar(timeline_data, col_widths=[6 * cm, 10 * cm]))
    elementos.append(PageBreak())

    # ========================================================
    # HALLAZGOS
    # ========================================================

    elementos.append(Paragraph("4. Hallazgos de Auditoría", styles["Seccion"]))

    hallazgos = [h for h in auditoria.hallazgos if getattr(h, "activo", True)]

    if not hallazgos:
        elementos.append(Paragraph("No se registraron hallazgos para esta auditoría.", styles["Texto"]))
    else:
        hallazgos_data = [
            ["Código", "Tipo", "Requisito", "Descripción", "Responsable", "Estado", "Plan"]
        ]

        for h in hallazgos:
            hallazgos_data.append(
                [
                    texto(h.codigo),
                    texto(h.tipo_hallazgo),
                    texto(h.requisito, "N/A"),
                    texto(h.descripcion),
                    texto(h.responsable, "Sin responsable"),
                    texto(h.estado),
                    f"PM ID {h.plan_mejoramiento_id}" if h.plan_mejoramiento_id else "Sin plan",
                ]
            )

        elementos.append(
            tabla_estandar(
                hallazgos_data,
                col_widths=[
                    2.1 * cm,
                    2.3 * cm,
                    2.5 * cm,
                    4.3 * cm,
                    2.3 * cm,
                    1.8 * cm,
                    2.0 * cm,
                ],
            )
        )

    elementos.append(Spacer(1, 0.6 * cm))

    # ========================================================
    # DETALLE + EVIDENCIAS
    # ========================================================

    elementos.append(
        Paragraph(
            "5. Detalle de No Conformidades y Evidencias Fotográficas",
            styles["Seccion"],
        )
    )

    no_conformidades = [h for h in hallazgos if h.tipo_hallazgo == "NO_CONFORMIDAD"]

    if not no_conformidades:
        elementos.append(Paragraph("No se registraron no conformidades.", styles["Texto"]))
    else:
        for h in no_conformidades:
            bloque = [
                Paragraph(
                    f"<b>{texto(h.codigo)}</b> · {texto(h.requisito, 'Sin requisito')}",
                    styles["SubTitulo"],
                ),
                Paragraph(f"<b>Descripción:</b> {texto(h.descripcion)}", styles["Texto"]),
                Paragraph(
                    f"<b>Evidencia textual:</b> {texto(h.evidencia, 'Sin evidencia registrada')}",
                    styles["Texto"],
                ),
                Paragraph(f"<b>Causa:</b> {texto(h.causa, 'Sin causa registrada')}", styles["Texto"]),
                Paragraph(
                    f"<b>Acción recomendada:</b> {texto(h.accion_recomendada, 'Sin acción recomendada')}",
                    styles["Texto"],
                ),
            ]

            imagen_antigua = evidencia_como_imagen(h)

            if imagen_antigua:
                bloque.append(Spacer(1, 0.2 * cm))
                bloque.append(
                    Paragraph(
                        "<b>Evidencia fotográfica registrada en el campo evidencia:</b>",
                        styles["Texto"],
                    )
                )
                bloque.append(
                    Image(
                        str(imagen_antigua),
                        width=11 * cm,
                        height=7 * cm,
                        kind="proportional",
                    )
                )

            imagenes = obtener_imagenes_hallazgo(db, h.id)

            if imagenes:
                bloque.append(Spacer(1, 0.3 * cm))
                bloque.append(
                    Paragraph(
                        f"<b>Evidencias fotográficas adjuntas ({len(imagenes)})</b>",
                        styles["Texto"],
                    )
                )

                for idx, evidencia in enumerate(imagenes, start=1):
                    try:
                        bloque.append(Spacer(1, 0.15 * cm))
                        bloque.append(
                            Paragraph(
                                f"Fotografía {idx}: {texto(evidencia.get('descripcion'), 'Sin descripción')}",
                                styles["Mini"],
                            )
                        )
                        bloque.append(
                            Image(
                                str(evidencia["ruta"]),
                                width=11 * cm,
                                height=7 * cm,
                                kind="proportional",
                            )
                        )
                    except Exception:
                        bloque.append(
                            Paragraph(
                                f"No fue posible insertar la fotografía {idx}.",
                                styles["Mini"],
                            )
                        )
            else:
                bloque.append(Spacer(1, 0.2 * cm))
                bloque.append(
                    Paragraph(
                        "No hay evidencias fotográficas adjuntas para este hallazgo.",
                        styles["Mini"],
                    )
                )

            bloque.append(Spacer(1, 0.5 * cm))
            elementos.append(KeepTogether(bloque))

    elementos.append(PageBreak())

    # ========================================================
    # PLANES
    # ========================================================

    elementos.append(Paragraph("6. Planes de Mejoramiento Asociados", styles["Seccion"]))

    planes = [h for h in hallazgos if h.plan_mejoramiento_id]

    if not planes:
        elementos.append(
            Paragraph(
                "No hay planes de mejoramiento asociados a los hallazgos.",
                styles["Texto"],
            )
        )
    else:
        planes_data = [["Hallazgo", "Tipo", "Plan asociado", "Estado hallazgo"]]

        for h in planes:
            planes_data.append(
                [
                    texto(h.codigo),
                    texto(h.tipo_hallazgo),
                    f"PM ID {h.plan_mejoramiento_id}",
                    texto(h.estado),
                ]
            )

        elementos.append(tabla_estandar(planes_data, col_widths=[4 * cm, 4 * cm, 4 * cm, 4 * cm]))

    elementos.append(Spacer(1, 0.8 * cm))

    # ========================================================
    # CONCLUSIONES Y RECOMENDACIONES
    # ========================================================

    elementos.append(Paragraph("7. Conclusiones", styles["Seccion"]))
    elementos.append(Paragraph(texto(auditoria.conclusiones, "Sin conclusiones registradas."), styles["Texto"]))

    elementos.append(Spacer(1, 0.6 * cm))

    elementos.append(Paragraph("8. Recomendaciones", styles["Seccion"]))
    elementos.append(Paragraph(texto(auditoria.recomendaciones, "Sin recomendaciones registradas."), styles["Texto"]))

    elementos.append(Spacer(1, 1.0 * cm))

    # ========================================================
    # FIRMAS
    # ========================================================

    elementos.append(Paragraph("9. Firmas y Validación", styles["Seccion"]))

    firma_auditor_elemento = "\n\n____________________________"

    if firma_auditor:
        firma_auditor_elemento = Image(
            str(firma_auditor),
            width=5.5 * cm,
            height=2.0 * cm,
            kind="proportional",
        )

    firmas = [
        ["AUDITOR LÍDER", "REPRESENTANTE SST"],
        [firma_auditor_elemento, "\n\n____________________________"],
        [
            texto(auditoria.auditor_lider, "Nombre auditor"),
            empresa_nombre,
        ],
    ]

    elementos.append(tabla_estandar(firmas, col_widths=[8 * cm, 8 * cm], header=False))
    elementos.append(Spacer(1, 0.6 * cm))

    # ========================================================
    # VALIDACIÓN DOCUMENTAL
    # ========================================================

    elementos.append(Paragraph("10. Validación Documental", styles["Seccion"]))

    validacion_data = [
        ["Código único de validación", codigo_validacion],
        ["Tipo documento", "AUDITORIA_SST"],
        ["Referencia", f"Auditoría ID {auditoria.id} · {auditoria.codigo}"],
        ["Estado inicial", "VALIDO"],
        ["SHA256", "Registrado automáticamente en base de datos al generar el PDF."],
        ["URL validación", url_validacion],
    ]

    elementos.append(tabla_estandar(validacion_data, col_widths=[5 * cm, 11 * cm], header=False))

    doc.build(
        elementos,
        onFirstPage=encabezado_pie,
        onLaterPages=encabezado_pie,
    )

    pdf = buffer.getvalue()
    buffer.close()

    registrar_validacion_pdf(
        db=db,
        auditoria=auditoria,
        codigo_validacion=codigo_validacion,
        pdf=pdf,
    )

    return pdf
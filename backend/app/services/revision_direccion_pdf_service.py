# ============================================================
# USO DEL ARCHIVO:
# Genera el PDF Enterprise del módulo Revisión por la Dirección SST.
#
# Incluye:
# - Logo de empresa
# - Código único de validación documental
# - QR de validación
# - Registro SHA256 en documentos_validacion_sst
# - Firma digital del Gerente si existe firma activa
# - Firma digital del Responsable SST si existe firma activa
#
# Ubicación:
# backend/app/services/revision_direccion_pdf_service.py
#
# FASE 1.8.4.1 — Firma Gerente + Doble Firma Electrónica
# ============================================================

from io import BytesIO
from datetime import datetime
from pathlib import Path
import os

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
    Table,
    TableStyle,
    Image,
    PageBreak,
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget

from app.models.revision_direccion import RevisionDireccionSST
from app.models.firma_digital import FirmaDigitalSST
from app.models.documento_validacion import DocumentoValidacionSST
from app.services.documento_validacion_service import (
    calcular_hash_sha256,
    generar_codigo_validacion,
)


BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads"))
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")


def texto(valor, defecto=""):
    return str(valor) if valor not in [None, ""] else defecto


def path_seguro(valor):
    if not valor:
        return None

    valor_original = str(valor).strip()

    if valor_original.startswith("http://") or valor_original.startswith("https://"):
        return None

    ruta_directa = Path(valor_original)
    if ruta_directa.exists():
        return ruta_directa

    valor_normalizado = valor_original.replace("\\", "/")

    if valor_normalizado.startswith("/uploads/"):
        ruta_upload = BASE_DIR / valor_normalizado.lstrip("/")
        if ruta_upload.exists():
            return ruta_upload

    if valor_normalizado.startswith("uploads/"):
        ruta_upload = BASE_DIR / valor_normalizado
        if ruta_upload.exists():
            return ruta_upload

    ruta_upload_dir = UPLOAD_DIR / valor_normalizado.lstrip("/")
    if ruta_upload_dir.exists():
        return ruta_upload_dir

    return None


def buscar_logo_empresa(empresa):
    if not empresa:
        return None

    for campo in ["logo", "logo_url", "ruta_logo", "logo_path", "imagen_logo"]:
        ruta = path_seguro(getattr(empresa, campo, None))
        if ruta:
            return ruta

    return None


def buscar_firma_usuario(db: Session, usuario_id: int | None, etiqueta: str):
    if not usuario_id:
        print(f"PDF RD | {etiqueta}: sin usuario_id.")
        return None

    firma = (
        db.query(FirmaDigitalSST)
        .filter(
            FirmaDigitalSST.usuario_id == usuario_id,
            FirmaDigitalSST.activo == True,
        )
        .order_by(FirmaDigitalSST.id.desc())
        .first()
    )

    if not firma:
        print(f"PDF RD | {etiqueta}: usuario {usuario_id} no tiene firma activa.")
        return None

    ruta_archivo = path_seguro(firma.archivo)
    ruta_url = path_seguro(firma.url)

    print("=" * 80)
    print(f"PDF RD | FIRMA ENCONTRADA - {etiqueta}")
    print("usuario_id:", usuario_id)
    print("firma_id:", firma.id)
    print("archivo BD:", firma.archivo)
    print("url BD:", firma.url)
    print("ruta_archivo:", ruta_archivo)
    print("ruta_url:", ruta_url)
    print("=" * 80)

    return ruta_archivo or ruta_url


def crear_imagen_segura(ruta, width, height):
    if not ruta:
        return Paragraph("____________________________", estilos()["TextoCentroRD"])

    try:
        return Image(
            str(ruta),
            width=width,
            height=height,
            kind="proportional",
        )
    except Exception as error:
        print("=" * 80)
        print("PDF RD | ERROR INSERTANDO IMAGEN")
        print("ruta:", ruta)
        print("error:", error)
        print("=" * 80)
        return Paragraph("____________________________", estilos()["TextoCentroRD"])


def crear_qr(validacion_texto):
    qr = QrCodeWidget(validacion_texto)

    dibujo = Drawing(3.2 * cm, 3.2 * cm)
    qr.barWidth = 3.2 * cm
    qr.barHeight = 3.2 * cm
    dibujo.add(qr)

    return dibujo


def registrar_validacion_pdf(
    db: Session,
    revision: RevisionDireccionSST,
    codigo_validacion: str,
    pdf: bytes,
):
    hash_pdf = calcular_hash_sha256(pdf)

    registro = DocumentoValidacionSST(
        codigo_validacion=codigo_validacion,
        tipo_documento="REVISION_DIRECCION_SST",
        referencia_id=revision.id,
        empresa_id=revision.empresa_id,
        usuario_id=revision.usuario_id,
        nombre_archivo=f"revision_direccion_{revision.id}.pdf",
        hash_sha256=hash_pdf,
        url_archivo=None,
        estado="VALIDO",
        observacion=(
            "Acta de Revisión por la Dirección SST generada automáticamente "
            "desde ERP SST PRO."
        ),
    )

    db.add(registro)
    db.commit()
    db.refresh(registro)

    return registro


def estilos():
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="TituloRD",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=20,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
        )
    )

    styles.add(
        ParagraphStyle(
            name="SeccionRD",
            parent=styles["Heading2"],
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#1d4ed8"),
            spaceBefore=10,
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="TextoRD",
            parent=styles["Normal"],
            alignment=TA_LEFT,
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#334155"),
        )
    )

    styles.add(
        ParagraphStyle(
            name="TextoCentroRD",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#334155"),
        )
    )

    styles.add(
        ParagraphStyle(
            name="MiniRD",
            parent=styles["Normal"],
            fontSize=7,
            leading=9,
            textColor=colors.HexColor("#64748b"),
        )
    )

    return styles


def header_footer(canvas, doc):
    canvas.saveState()

    width, height = A4

    canvas.setFillColor(colors.HexColor("#0f172a"))
    canvas.rect(0, height - 1.15 * cm, width, 1.15 * cm, fill=True, stroke=False)

    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.drawString(
        1.4 * cm,
        height - 0.72 * cm,
        "ERP SST PRO · Acta Revisión por la Dirección SST Enterprise",
    )

    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(
        width - 1.4 * cm,
        height - 0.72 * cm,
        f"Página {doc.page}",
    )

    canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
    canvas.line(1.4 * cm, 1.2 * cm, width - 1.4 * cm, 1.2 * cm)

    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(
        width / 2,
        0.75 * cm,
        "Documento generado automáticamente por ERP SST PRO · Validación documental SHA256",
    )

    canvas.restoreState()


def tabla(data, col_widths=None, header=True):
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)

    style = [
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
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

    t.setStyle(TableStyle(style))
    return t


def generar_pdf_revision_direccion(db: Session, revision_id: int) -> bytes:
    revision = (
        db.query(RevisionDireccionSST)
        .options(
            joinedload(RevisionDireccionSST.empresa),
            joinedload(RevisionDireccionSST.compromisos),
        )
        .filter(
            RevisionDireccionSST.id == revision_id,
            RevisionDireccionSST.activo == True,
        )
        .first()
    )

    if not revision:
        raise HTTPException(
            status_code=404,
            detail="Revisión por la Dirección no encontrada",
        )

    styles = estilos()

    empresa = revision.empresa
    logo = buscar_logo_empresa(empresa)

    gerente_firma_usuario_id = revision.gerente_usuario_id
    responsable_firma_usuario_id = (
        revision.responsable_sst_usuario_id or revision.usuario_id
    )

    firma_gerente = buscar_firma_usuario(
        db=db,
        usuario_id=gerente_firma_usuario_id,
        etiqueta="GERENTE",
    )

    firma_responsable_sst = buscar_firma_usuario(
        db=db,
        usuario_id=responsable_firma_usuario_id,
        etiqueta="RESPONSABLE SST",
    )

    codigo_validacion = generar_codigo_validacion(
        tipo="REVISION_DIRECCION_SST",
        referencia_id=revision.id,
    )

    url_validacion = f"{PUBLIC_BASE_URL}/validar/documento/{codigo_validacion}"

    validacion_qr = (
        f"ERP SST PRO\n"
        f"Documento: Revisión por la Dirección SST\n"
        f"Código validación: {codigo_validacion}\n"
        f"Revisión: {revision.codigo}\n"
        f"Empresa: {texto(getattr(empresa, 'nombre', None), 'Empresa no registrada')}\n"
        f"NIT: {texto(getattr(empresa, 'nit', None), 'NIT no registrado')}\n"
        f"URL: {url_validacion}"
    )

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.4 * cm,
        leftMargin=1.4 * cm,
        topMargin=1.9 * cm,
        bottomMargin=1.6 * cm,
        title=f"Acta Revisión Dirección {revision.codigo}",
    )

    elementos = []

    logo_el = (
        crear_imagen_segura(
            ruta=logo,
            width=3.6 * cm,
            height=2.0 * cm,
        )
        if logo
        else Paragraph("<b>ERP SST PRO</b>", styles["SeccionRD"])
    )

    elementos.append(
        tabla(
            [[logo_el, Paragraph("ACTA DE REVISIÓN POR LA DIRECCIÓN SST ENTERPRISE", styles["TituloRD"])]],
            col_widths=[4 * cm, 12 * cm],
            header=False,
        )
    )

    elementos.append(Spacer(1, 0.4 * cm))

    datos_generales = [
        ["Código acta", texto(revision.codigo)],
        ["Código validación", codigo_validacion],
        ["Título", texto(revision.titulo)],
        ["Empresa", texto(getattr(empresa, "nombre", None), "Empresa no registrada")],
        ["NIT", texto(getattr(empresa, "nit", None), "NIT no registrado")],
        ["Fecha revisión", texto(revision.fecha_revision)],
        ["Periodo evaluado", texto(revision.periodo_evaluado, "No registrado")],
        ["Estado revisión", texto(revision.estado)],
        ["Estado documental", "VALIDO"],
        ["Fecha generación", datetime.now().strftime("%Y-%m-%d %H:%M")],
    ]

    elementos.append(tabla(datos_generales, col_widths=[5 * cm, 11 * cm], header=False))
    elementos.append(Spacer(1, 0.4 * cm))

    elementos.append(
        tabla(
            [
                [
                    crear_qr(validacion_qr),
                    Paragraph(
                        "<b>QR de Validación Documental</b><br/>"
                        f"Código único: <b>{codigo_validacion}</b><br/>"
                        "Este documento queda registrado con hash SHA256 "
                        "en la base documental del ERP SST PRO.",
                        styles["TextoRD"],
                    ),
                ]
            ],
            col_widths=[4 * cm, 12 * cm],
            header=False,
        )
    )

    elementos.append(Paragraph("1. Participantes", styles["SeccionRD"]))

    elementos.append(
        tabla(
            [
                ["Gerente", texto(revision.gerente, "No registrado")],
                ["Responsable SST", texto(revision.responsable_sst, "No registrado")],
                ["Participantes", texto(revision.participantes, "No registrados")],
            ],
            col_widths=[5 * cm, 11 * cm],
            header=False,
        )
    )

    elementos.append(Paragraph("2. Objetivo, Alcance y Agenda", styles["SeccionRD"]))

    elementos.append(
        tabla(
            [
                ["Objetivo", texto(revision.objetivo, "Sin objetivo registrado")],
                ["Alcance", texto(revision.alcance, "Sin alcance registrado")],
                ["Agenda", texto(revision.agenda, "Sin agenda registrada")],
            ],
            col_widths=[5 * cm, 11 * cm],
            header=False,
        )
    )

    elementos.append(Paragraph("3. Entradas para la Revisión", styles["SeccionRD"]))

    entradas = [
        ["Auditorías SST", texto(revision.resumen_auditorias, "Sin información")],
        ["Indicadores SST", texto(revision.resumen_indicadores, "Sin información")],
        ["Planes de mejora", texto(revision.resumen_planes_mejora, "Sin información")],
        ["Accidentes / Incidentes", texto(revision.resumen_accidentes, "Sin información")],
        ["Capacitaciones", texto(revision.resumen_capacitaciones, "Sin información")],
        ["Cumplimiento legal", texto(revision.resumen_cumplimiento_legal, "Sin información")],
    ]

    elementos.append(tabla(entradas, col_widths=[5 * cm, 11 * cm], header=False))
    elementos.append(PageBreak())

    elementos.append(
        Paragraph(
            "4. Conclusiones, Decisiones y Recomendaciones",
            styles["SeccionRD"],
        )
    )

    elementos.append(
        tabla(
            [
                ["Conclusiones", texto(revision.conclusiones, "Sin conclusiones")],
                ["Decisiones", texto(revision.decisiones, "Sin decisiones")],
                ["Recomendaciones", texto(revision.recomendaciones, "Sin recomendaciones")],
            ],
            col_widths=[5 * cm, 11 * cm],
            header=False,
        )
    )

    elementos.append(Paragraph("5. Compromisos Gerenciales", styles["SeccionRD"]))

    compromisos = [c for c in revision.compromisos if getattr(c, "activo", True)]

    if compromisos:
        data = [["Compromiso", "Responsable", "Fecha", "Prioridad", "Estado"]]

        for c in compromisos:
            data.append(
                [
                    texto(c.compromiso),
                    texto(c.responsable, "Sin responsable"),
                    texto(c.fecha_compromiso, "Sin fecha"),
                    texto(c.prioridad),
                    texto(c.estado),
                ]
            )

        elementos.append(
            tabla(
                data,
                col_widths=[5.6 * cm, 3.2 * cm, 2.5 * cm, 2.2 * cm, 2.5 * cm],
            )
        )
    else:
        elementos.append(Paragraph("No hay compromisos registrados.", styles["TextoRD"]))

    elementos.append(Spacer(1, 0.5 * cm))

    resumen = [
        ["Total compromisos", texto(revision.total_compromisos, "0")],
        ["Pendientes", texto(revision.compromisos_pendientes, "0")],
        ["Cerrados", texto(revision.compromisos_cerrados, "0")],
        ["Cumplimiento", f"{texto(revision.porcentaje_cumplimiento, '0')}%"],
    ]

    elementos.append(tabla(resumen, col_widths=[5 * cm, 11 * cm], header=False))
    elementos.append(Spacer(1, 0.8 * cm))

    elementos.append(Paragraph("6. Firmas", styles["SeccionRD"]))

    firma_gerente_el = crear_imagen_segura(
        ruta=firma_gerente,
        width=5.5 * cm,
        height=2.0 * cm,
    )

    firma_responsable_el = crear_imagen_segura(
        ruta=firma_responsable_sst,
        width=5.5 * cm,
        height=2.0 * cm,
    )

    tabla_firmas = Table(
        [
            [
                Paragraph("<b>GERENTE</b>", styles["TextoCentroRD"]),
                Paragraph("<b>RESPONSABLE SST</b>", styles["TextoCentroRD"]),
            ],
            [
                firma_gerente_el,
                firma_responsable_el,
            ],
            [
                Paragraph(texto(revision.gerente, "Nombre gerente"), styles["TextoCentroRD"]),
                Paragraph(texto(revision.responsable_sst, "Nombre responsable SST"), styles["TextoCentroRD"]),
            ],
        ],
        colWidths=[8 * cm, 8 * cm],
        rowHeights=[0.8 * cm, 2.5 * cm, 0.8 * cm],
    )

    tabla_firmas.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    elementos.append(tabla_firmas)
    elementos.append(Spacer(1, 0.6 * cm))

    elementos.append(Paragraph("7. Validación Documental", styles["SeccionRD"]))

    validacion_data = [
        [
            Paragraph("Código único", styles["TextoRD"]),
            Paragraph(codigo_validacion, styles["TextoRD"]),
        ],
        [
            Paragraph("Tipo documento", styles["TextoRD"]),
            Paragraph("REVISION_DIRECCION_SST", styles["TextoRD"]),
        ],
        [
            Paragraph("Referencia", styles["TextoRD"]),
            Paragraph(f"Revisión ID {revision.id} · {revision.codigo}", styles["TextoRD"]),
        ],
        [
            Paragraph("Estado", styles["TextoRD"]),
            Paragraph("VALIDO", styles["TextoRD"]),
        ],
        [
            Paragraph("SHA256", styles["TextoRD"]),
            Paragraph(
                "Registrado automáticamente en base de datos al generar el PDF.",
                styles["TextoRD"],
            ),
        ],
        [
            Paragraph("URL validación", styles["TextoRD"]),
            Paragraph(url_validacion, styles["TextoRD"]),
        ],
    ]

    tabla_validacion = Table(
        validacion_data,
        colWidths=[5 * cm, 11 * cm],
    )

    tabla_validacion.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    elementos.append(tabla_validacion)
    elementos.append(Spacer(1, 0.4 * cm))

    elementos.append(
        Paragraph(
            f"Acta generada por ERP SST PRO · Código: {revision.codigo} · "
            f"Validación: {codigo_validacion} · "
            f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            styles["MiniRD"],
        )
    )

    doc.build(
        elementos,
        onFirstPage=header_footer,
        onLaterPages=header_footer,
    )

    pdf = buffer.getvalue()
    buffer.close()

    registrar_validacion_pdf(
        db=db,
        revision=revision,
        codigo_validacion=codigo_validacion,
        pdf=pdf,
    )

    return pdf
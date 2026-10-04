# ============================================================
# ROUTER COMITÉS SST - COPASST / VIGÍA SST
# FASE auditoría - H-008
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.auth.dependencies import require_roles
from app.models.empresa import Empresa
from app.models.comite_sst import ComiteSST, ComiteIntegranteSST, ComiteReunionSST
from app.models.configuracion_documental import ConfiguracionDocumental

from app.schemas.comite_sst_schema import (
    ComiteCreate,
    ComiteUpdate,
    ComiteResponse,
    ComiteIntegranteCreate,
    ComiteIntegranteResponse,
    ComiteReunionCreate,
    ComiteReunionResponse,
)
from app.routers.empresas import validar_acceso_empresa


router = APIRouter(
    prefix="/sst/comites",
    tags=["SST - Comités COPASST / Vigía"],
)

ROLES_LECTURA = [
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "RESPONSABLE_SST",
    "COORDINADOR_SST",
    "COPASST",
    "VIGIA_SST",
]
ROLES_ESCRITURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]


def serializar_comite(comite: ComiteSST) -> dict:
    return {
        "id": comite.id,
        "empresa_id": comite.empresa_id,
        "tipo_comite": comite.tipo_comite,
        "nombre": comite.nombre,
        "descripcion": comite.descripcion,
        "fecha_constitucion": comite.fecha_constitucion,
        "fecha_fin_periodo": comite.fecha_fin_periodo,
        "vigente": comite.vigente,
        "observaciones": comite.observaciones,
        "activo": comite.activo,
        "fecha_creacion": comite.fecha_creacion,
        "fecha_actualizacion": comite.fecha_actualizacion,
        "total_integrantes": len([i for i in comite.integrantes if i.activo])
        if comite.integrantes
        else 0,
        "total_reuniones": len([r for r in comite.reuniones if r.activo])
        if comite.reuniones
        else 0,
    }


@router.get("/", response_model=list[ComiteResponse])
def listar_comites(
    empresa_id: int,
    tipo_comite: str | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    validar_acceso_empresa(usuario, empresa_id)
    query = (
        db.query(ComiteSST)
        .options(
            joinedload(ComiteSST.integrantes),
            joinedload(ComiteSST.reuniones),
        )
        .filter(ComiteSST.empresa_id == empresa_id, ComiteSST.activo)
    )
    if tipo_comite:
        query = query.filter(ComiteSST.tipo_comite == tipo_comite.upper())
    comites = query.order_by(ComiteSST.id.desc()).all()
    return [serializar_comite(c) for c in comites]


@router.post("/", response_model=ComiteResponse)
def crear_comite(
    data: ComiteCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    validar_acceso_empresa(usuario, data.empresa_id)

    comite = ComiteSST(
        empresa_id=data.empresa_id,
        usuario_id=usuario.id,
        tipo_comite=data.tipo_comite.upper(),
        nombre=data.nombre,
        descripcion=data.descripcion,
        fecha_constitucion=data.fecha_constitucion,
        fecha_fin_periodo=data.fecha_fin_periodo,
        observaciones=data.observaciones,
    )
    db.add(comite)
    db.commit()
    db.refresh(comite)
    return serializar_comite(comite)


@router.get("/{comite_id}", response_model=ComiteResponse)
def obtener_comite(
    comite_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    comite = (
        db.query(ComiteSST)
        .options(
            joinedload(ComiteSST.integrantes),
            joinedload(ComiteSST.reuniones),
        )
        .filter(ComiteSST.id == comite_id)
        .first()
    )
    if not comite:
        raise HTTPException(status_code=404, detail="Comité no encontrado")
    validar_acceso_empresa(usuario, comite.empresa_id)
    return serializar_comite(comite)


@router.put("/{comite_id}", response_model=ComiteResponse)
def actualizar_comite(
    comite_id: int,
    data: ComiteUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    comite = db.query(ComiteSST).filter(ComiteSST.id == comite_id).first()
    if not comite:
        raise HTTPException(status_code=404, detail="Comité no encontrado")
    validar_acceso_empresa(usuario, comite.empresa_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(comite, key, value)

    db.commit()
    db.refresh(comite)

    comite = (
        db.query(ComiteSST)
        .options(joinedload(ComiteSST.integrantes), joinedload(ComiteSST.reuniones))
        .filter(ComiteSST.id == comite_id)
        .first()
    )
    return serializar_comite(comite)


@router.delete("/{comite_id}")
def eliminar_comite(
    comite_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    comite = db.query(ComiteSST).filter(ComiteSST.id == comite_id).first()
    if not comite:
        raise HTTPException(status_code=404, detail="Comité no encontrado")
    validar_acceso_empresa(usuario, comite.empresa_id)
    comite.activo = False
    db.commit()
    return {"mensaje": "Comité desactivado correctamente"}


# ============================================================
# INTEGRANTES
# ============================================================


@router.get("/{comite_id}/integrantes", response_model=list[ComiteIntegranteResponse])
def listar_integrantes(
    comite_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    comite = db.query(ComiteSST).filter(ComiteSST.id == comite_id).first()
    if not comite:
        raise HTTPException(status_code=404, detail="Comité no encontrado")
    validar_acceso_empresa(usuario, comite.empresa_id)
    integrantes = (
        db.query(ComiteIntegranteSST)
        .filter(
            ComiteIntegranteSST.comite_id == comite_id,
            ComiteIntegranteSST.activo,
        )
        .all()
    )
    return integrantes


@router.post("/{comite_id}/integrantes", response_model=ComiteIntegranteResponse)
def agregar_integrante(
    comite_id: int,
    data: ComiteIntegranteCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    comite = db.query(ComiteSST).filter(ComiteSST.id == comite_id).first()
    if not comite:
        raise HTTPException(status_code=404, detail="Comité no encontrado")
    validar_acceso_empresa(usuario, comite.empresa_id)

    integrante = ComiteIntegranteSST(
        comite_id=comite_id,
        empresa_id=comite.empresa_id,
        **data.model_dump(),
    )
    db.add(integrante)
    db.commit()
    db.refresh(integrante)
    return integrante


@router.delete("/{comite_id}/integrantes/{integrante_id}")
def eliminar_integrante(
    comite_id: int,
    integrante_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    integrante = (
        db.query(ComiteIntegranteSST)
        .filter(
            ComiteIntegranteSST.id == integrante_id,
            ComiteIntegranteSST.comite_id == comite_id,
        )
        .first()
    )
    if not integrante:
        raise HTTPException(status_code=404, detail="Integrante no encontrado")
    validar_acceso_empresa(usuario, integrante.empresa_id)
    integrante.activo = False
    db.commit()
    return {"mensaje": "Integrante removido correctamente"}


# ============================================================
# REUNIONES
# ============================================================


@router.get("/{comite_id}/reuniones", response_model=list[ComiteReunionResponse])
def listar_reuniones(
    comite_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    comite = db.query(ComiteSST).filter(ComiteSST.id == comite_id).first()
    if not comite:
        raise HTTPException(status_code=404, detail="Comité no encontrado")
    validar_acceso_empresa(usuario, comite.empresa_id)
    reuniones = (
        db.query(ComiteReunionSST)
        .filter(
            ComiteReunionSST.comite_id == comite_id, ComiteReunionSST.activo
        )
        .order_by(ComiteReunionSST.fecha_reunion.desc())
        .all()
    )
    return reuniones


@router.post("/{comite_id}/reuniones", response_model=ComiteReunionResponse)
def crear_reunion(
    comite_id: int,
    data: ComiteReunionCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    comite = db.query(ComiteSST).filter(ComiteSST.id == comite_id).first()
    if not comite:
        raise HTTPException(status_code=404, detail="Comité no encontrado")
    validar_acceso_empresa(usuario, comite.empresa_id)

    reunion = ComiteReunionSST(
        comite_id=comite_id,
        empresa_id=comite.empresa_id,
        usuario_id=usuario.id,
        **data.model_dump(),
    )
    db.add(reunion)
    db.commit()
    db.refresh(reunion)
    return reunion


@router.put("/{comite_id}/reuniones/{reunion_id}", response_model=ComiteReunionResponse)
def actualizar_reunion(
    comite_id: int,
    reunion_id: int,
    data: ComiteReunionCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    reunion = (
        db.query(ComiteReunionSST)
        .filter(
            ComiteReunionSST.id == reunion_id, ComiteReunionSST.comite_id == comite_id
        )
        .first()
    )
    if not reunion:
        raise HTTPException(status_code=404, detail="Reunión no encontrada")
    validar_acceso_empresa(usuario, reunion.empresa_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(reunion, key, value)

    db.commit()
    db.refresh(reunion)
    return reunion


@router.get("/{comite_id}/acta-constitucion-pdf")
def exportar_acta_constitucion_pdf(
    comite_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    from io import BytesIO
    from datetime import datetime
    from html import escape
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    from fastapi.responses import Response

    comite = (
        db.query(ComiteSST)
        .options(joinedload(ComiteSST.empresa), joinedload(ComiteSST.integrantes))
        .filter(ComiteSST.id == comite_id, ComiteSST.activo.is_(True))
        .first()
    )
    if not comite:
        raise HTTPException(status_code=404, detail="Comité no encontrado")
    validar_acceso_empresa(usuario, comite.empresa_id)

    empresa = (
        comite.empresa
        or db.query(Empresa).filter(Empresa.id == comite.empresa_id).first()
    )
    configuracion = (
        db.query(ConfiguracionDocumental)
        .filter(ConfiguracionDocumental.empresa_id == comite.empresa_id)
        .order_by(ConfiguracionDocumental.id.desc())
        .first()
    )

    prefijo = configuracion.prefijo_documental if configuracion else "SGSST"
    version = configuracion.version_documental if configuracion else "1.0"

    normativas = {
        "COPASST": (
            "la Resolución 2013 de 1986 y el Decreto 1072 de 2015, "
            "en especial las disposiciones del Libro 2, Parte 2, Título 4, "
            "Capítulo 6, que exigen la conformación "
            "del Comité Paritario de Seguridad y Salud en el Trabajo (COPASST) "
            "con participación equitativa de representantes del empleador y de los trabajadores."
        ),
        "VIGIA_SST": (
            "el Decreto 1072 de 2015 (artículo 2.2.4.6) y la Resolución 2013 de 1986, "
            "que disponen la designación de un Vigía de Seguridad y Salud en el Trabajo "
            "para las empresas que cuentan con menos de diez (10) trabajadores, "
            "cuando no se requiere la conformación de un comité paritario."
        ),
        "CONVIVENCIA": (
            "la Ley 1010 de 2006, la Resolución 652 de 2012 y su modificación "
            "mediante la Resolución 1356 de 2012, que ordenan la "
            "conformación del Comité de Convivencia Laboral con representantes "
            "del empleador y de los trabajadores, y su facultad respecto de la "
            "prevención y tratamiento del acoso laboral."
        ),
    }
    normativa = normativas.get(
        comite.tipo_comite, "el Decreto 1072 de 2015 (SG-SST)"
    )

    integrantes = [i for i in (comite.integrantes or []) if i.activo]
    presidente = next(
        (i for i in integrantes if i.rol_comite == "PRESIDENTE"), None
    )
    secretario = next(
        (i for i in integrantes if i.rol_comite == "SECRETARIO"), None
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=42,
        leftMargin=42,
        topMargin=42,
        bottomMargin=42,
    )
    styles = getSampleStyleSheet()
    cuerpo = ParagraphStyle(
        "Cuerpo", parent=styles["Normal"], alignment=TA_JUSTIFY, spaceAfter=8, leading=13
    )
    encabezado = ParagraphStyle(
        "Encabezado", parent=styles["Normal"], alignment=TA_CENTER, spaceAfter=2
    )
    firma = ParagraphStyle(
        "Firma", parent=styles["Normal"], alignment=TA_CENTER, spaceBefore=6
    )

    nombre_empresa = escape(empresa.nombre if empresa else "")
    nit_empresa = escape(str(empresa.nit) if empresa and empresa.nit else "")
    hoy = datetime.now().strftime("%d/%m/%Y")
    fecha_acta = (
        comite.fecha_constitucion.strftime("%d/%m/%Y")
        if comite.fecha_constitucion
        else hoy
    )
    nombre_comite = escape(comite.nombre or "")
    tipo = escape(comite.tipo_comite or "")

    story = [
        Paragraph("ACTA DE CONSTITUCIÓN Y CONFORMACIÓN", styles["Title"]),
        Paragraph(nombre_comite, encabezado),
        Paragraph(
            f"{prefijo}-ACTA-{comite.id} | Versión {version}",
            encabezado,
        ),
        Spacer(1, 16),
        Paragraph(
            f"En concordancia con la normatividad vigente y de conformidad con el día "
            f"{fecha_acta}, se reunieron los representantes del empleador y de los "
            f"trabajadores de la empresa <b>{nombre_empresa}</b>, identificada con NIT "
            f"<b>{nit_empresa}</b>, con el fin de dar cumplimiento a lo dispuesto en "
            f"{normativa}.",
            cuerpo,
        ),
        Spacer(1, 4),
    ]

    datos = Table(
        [
            ["Empresa", nombre_empresa, "Tipo de comité", tipo],
            ["NIT", nit_empresa, "Fecha de constitución", str(comite.fecha_constitucion or "")],
            [
                "Fin del período",
                str(comite.fecha_fin_periodo or "No definido"),
                "Estado",
                "VIGENTE" if comite.vigente else "INACTIVO",
            ],
        ],
        colWidths=[90, 160, 100, 160],
    )
    datos.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#1D4ED8")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(datos)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Integrantes designados", styles["Heading2"]))
    filas = [["Nombre", "Documento", "Cargo", "Rol", "Representa"]]
    if integrantes:
        for item in integrantes:
            filas.append(
                [
                    escape(item.nombre or ""),
                    escape(item.documento or ""),
                    escape(item.cargo or ""),
                    escape(item.rol_comite or ""),
                    escape(item.representa or ""),
                ]
            )
    else:
        filas.append(["", "", "", "", ""])
    tabla = Table(filas, colWidths=[135, 75, 110, 80, 90], repeatRows=1)
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1D4ED8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(tabla)

    if comite.observaciones:
        story.append(Spacer(1, 12))
        story.append(Paragraph("Observaciones", styles["Heading2"]))
        story.append(
            Paragraph(escape(str(comite.observaciones)).replace("\n", "<br/>"), cuerpo)
        )

    story.append(Spacer(1, 28))
    story.append(Paragraph("Firmas de los representantes", styles["Heading2"]))
    story.append(Spacer(1, 8))

    firmas = Table(
        [
            [
                Paragraph("<b>Por el empleador</b>", firma),
                Paragraph("<b>Por los trabajadores</b>", firma),
            ],
            [
                Paragraph(
                    f"<br/><br/>{escape(presidente.nombre or '____________________') if presidente else '____________________'}"
                    f"<br/>{escape(presidente.rol_comite or '') if presidente else ''} — Empresa",
                    firma,
                ),
                Paragraph(
                    f"<br/><br/>{escape(secretario.nombre or '____________________') if secretario else '____________________'}"
                    f"<br/>{escape(secretario.rol_comite or '') if secretario else ''} — Trabajadores",
                    firma,
                ),
            ],
        ],
        colWidths=[260, 260],
    )
    firmas.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(firmas)

    story.append(Spacer(1, 18))
    story.append(
        Paragraph(
            f"Documento generado electrónicamente el {hoy} desde el Sistema de Gestión "
            f"de Seguridad y Salud en el Trabajo. Validez de acuerdo con la normatividad "
            f"vigente en materia de SG-SST.",
            ParagraphStyle(
                "Pie", parent=styles["Normal"], fontSize=8, textColor=colors.grey
            ),
        )
    )

    doc.build(story)
    buffer.seek(0)

    return Response(
        content=buffer.read(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f"attachment; filename=acta_constitucion_{comite.tipo_comite.lower()}_{comite.id}.pdf"
            )
        },
    )

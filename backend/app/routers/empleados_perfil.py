# ============================================================
# ROUTER PERFIL SOCIODEMOGRÁFICO EMPLEADO - ERP SST PRO
# Encuesta integral de perfil sociodemográfico, salud y hoja de vida
# ============================================================

import io
import logging
from calendar import monthrange
from datetime import date, datetime
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.auth.dependencies import require_roles
from app.database import get_db
from app.models.empleado import Empleado
from app.models.empleado_perfil_sociodemografico import EmpleadoPerfilSociodemografico
from sqlalchemy.orm import joinedload
from app.schemas.empleado_perfil_schema import (
    EmpleadoPerfilCreate,
    EmpleadoPerfilResponse,
    EmpleadoPerfilUpdate,
)

router = APIRouter(
    prefix="/empleados-perfil",
    tags=["Perfil Sociodemográfico Empleado"],
)
ROLES_SST = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]
logger = logging.getLogger("app.empleados_perfil")

_MESES = [
    (1, "Ene", "Enero"),
    (2, "Feb", "Febrero"),
    (3, "Mar", "Marzo"),
    (4, "Abr", "Abril"),
    (5, "May", "Mayo"),
    (6, "Jun", "Junio"),
    (7, "Jul", "Julio"),
    (8, "Ago", "Agosto"),
    (9, "Sep", "Septiembre"),
    (10, "Oct", "Octubre"),
    (11, "Nov", "Noviembre"),
    (12, "Dic", "Diciembre"),
]


def _empresa_id_autorizada(usuario, empresa_id: int | None) -> int | None:
    if str(getattr(usuario, "rol", "") or "").upper() == "SUPER_ADMIN":
        return empresa_id
    usuario_empresa_id = getattr(usuario, "empresa_id", None)
    if usuario_empresa_id is None:
        raise HTTPException(status_code=403, detail="Usuario sin empresa asignada")
    if empresa_id is not None and int(usuario_empresa_id) != int(empresa_id):
        raise HTTPException(status_code=403, detail="No tiene permisos sobre esta empresa")
    return int(usuario_empresa_id)


# ── Helpers ─────────────────────────────────────────────────
def _get_perfil_or_404(empleado_id: int, db: Session, empresa_id: int | None = None):
    q = db.query(EmpleadoPerfilSociodemografico).filter(
        EmpleadoPerfilSociodemografico.empleado_id == empleado_id
    )
    if empresa_id:
        q = q.filter(EmpleadoPerfilSociodemografico.empresa_id == empresa_id)
    return q.first()


def _ensure_empleado(exists: bool, empleado_id: int, db: Session):
    if not exists:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")


def _fecha_corte(anio: int, mes: int | None) -> date:
    numero_mes = mes or 12
    return date(anio, numero_mes, monthrange(anio, numero_mes)[1])


def _estado_empleado_al_corte(empleado: Empleado, fecha_corte: date) -> tuple[str, bool]:
    if empleado.fecha_retiro is not None:
        estado = "INACTIVO" if empleado.fecha_retiro <= fecha_corte else "ACTIVO"
        return estado, False

    estado_laboral = str(empleado.estado_laboral or "").strip().upper()
    historico_incompleto = estado_laboral != "ACTIVO" or empleado.activo is False
    return ("INACTIVO" if historico_incompleto else "ACTIVO"), historico_incompleto


def _empleados_al_corte(empleados: list[Empleado], fecha_corte: date) -> list[Empleado]:
    return [
        empleado
        for empleado in empleados
        if empleado.fecha_ingreso is not None and empleado.fecha_ingreso <= fecha_corte
    ]


def _construir_dashboard(
    empleados: list[Empleado],
    perfiles: list[EmpleadoPerfilSociodemografico],
    anio: int,
    mes: int | None,
) -> dict:
    fecha_corte = _fecha_corte(anio, mes)
    empleados_periodo = _empleados_al_corte(empleados, fecha_corte)
    perfiles_por_empleado = {perfil.empleado_id: perfil for perfil in perfiles}

    estados = [_estado_empleado_al_corte(e, fecha_corte) for e in empleados_periodo]
    activos = sum(1 for estado, _ in estados if estado == "ACTIVO")
    inactivos = len(empleados_periodo) - activos
    perfiles_registrados = sum(
        1 for empleado in empleados_periodo if empleado.id in perfiles_por_empleado
    )
    perfiles_completados = sum(
        1
        for empleado in empleados_periodo
        if getattr(perfiles_por_empleado.get(empleado.id), "completado", False)
    )

    limite_tendencia = mes or 12
    tendencia = []
    for numero_mes, nombre_corto, _ in _MESES[:limite_tendencia]:
        corte_mes = _fecha_corte(anio, numero_mes)
        empleados_mes = _empleados_al_corte(empleados, corte_mes)
        activos_mes = sum(
            1
            for empleado in empleados_mes
            if _estado_empleado_al_corte(empleado, corte_mes)[0] == "ACTIVO"
        )
        tendencia.append(
            {
                "mes": numero_mes,
                "nombre": nombre_corto,
                "activos": activos_mes,
                "inactivos": len(empleados_mes) - activos_mes,
            }
        )

    sedes: dict[int | None, dict] = {}
    for empleado in empleados_periodo:
        sede_id = empleado.sede_id
        grupo = sedes.setdefault(
            sede_id,
            {
                "sede_id": sede_id,
                "nombre": empleado.sede.nombre if empleado.sede else "Sin sede",
                "activos": 0,
                "inactivos": 0,
                "total": 0,
            },
        )
        estado, _ = _estado_empleado_al_corte(empleado, fecha_corte)
        grupo["activos" if estado == "ACTIVO" else "inactivos"] += 1
        grupo["total"] += 1

    nombre_mes = _MESES[(mes or 12) - 1][2]
    etiqueta = f"{nombre_mes} {anio}" if mes else f"Año {anio}"
    total_periodo = len(empleados_periodo)
    return {
        "periodo": {
            "anio": anio,
            "mes": mes,
            "fecha_corte": fecha_corte.isoformat(),
            "etiqueta": etiqueta,
        },
        "kpis": {
            "total_periodo": total_periodo,
            "activos": activos,
            "inactivos": inactivos,
            "perfiles_registrados": perfiles_registrados,
            "perfiles_completados": perfiles_completados,
            "cobertura_perfil": round(
                perfiles_registrados * 100 / total_periodo, 1
            )
            if total_periodo
            else 0.0,
            "sin_fecha_ingreso": sum(1 for e in empleados if e.fecha_ingreso is None),
            "datos_historicos_incompletos": sum(1 for _, incompleto in estados if incompleto),
        },
        "tendencia_mensual": tendencia,
        "por_sede": sorted(
            sedes.values(), key=lambda item: (item["nombre"].lower(), item["sede_id"] or 0)
        ),
    }


def _cargar_dashboard(
    db: Session,
    empresa_id: int | None,
    sede_id: int | None,
    anio: int,
    mes: int | None,
) -> tuple[dict, list[Empleado], dict[int, EmpleadoPerfilSociodemografico]]:
    query = db.query(Empleado).options(
        joinedload(Empleado.empresa), joinedload(Empleado.sede)
    )
    if empresa_id is not None:
        query = query.filter(Empleado.empresa_id == empresa_id)
    if sede_id is not None:
        query = query.filter(Empleado.sede_id == sede_id)
    empleados = query.order_by(Empleado.id).all()

    fecha_corte = _fecha_corte(anio, mes)
    empleados_periodo = _empleados_al_corte(empleados, fecha_corte)
    ids_periodo = [empleado.id for empleado in empleados_periodo]
    perfiles = []
    if ids_periodo:
        perfiles = (
            db.query(EmpleadoPerfilSociodemografico)
            .filter(EmpleadoPerfilSociodemografico.empleado_id.in_(ids_periodo))
            .all()
        )
    perfiles_por_empleado = {perfil.empleado_id: perfil for perfil in perfiles}
    return (
        _construir_dashboard(empleados, perfiles, anio, mes),
        empleados_periodo,
        perfiles_por_empleado,
    )


def _detalle_empleado(
    empleado: Empleado,
    perfil: EmpleadoPerfilSociodemografico | None,
    fecha_corte: date,
) -> list:
    estado, _ = _estado_empleado_al_corte(empleado, fecha_corte)
    return [
        f"{empleado.nombres} {empleado.apellidos}".strip(),
        empleado.documento,
        empleado.empresa.nombre if empleado.empresa else "Sin empresa",
        empleado.sede.nombre if empleado.sede else "Sin sede",
        empleado.fecha_ingreso,
        empleado.fecha_retiro,
        estado,
        "Sí" if perfil else "No",
        "Sí" if perfil and perfil.completado else "No",
    ]


def _valor_excel(valor):
    if isinstance(valor, str) and valor.startswith(("=", "+", "-", "@")):
        return f"'{valor}"
    return valor


# Las rutas estáticas deben declararse antes de /empleado/{empleado_id}.
@router.get("/dashboard")
def dashboard_perfil_sociodemografico(
    empresa_id: int | None = Query(default=None),
    sede_id: int | None = Query(default=None),
    anio: int = Query(default=datetime.now().year, ge=1900, le=2100),
    mes: int | None = Query(default=None, ge=1, le=12),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    empresa_autorizada = _empresa_id_autorizada(usuario, empresa_id)
    dashboard, _, _ = _cargar_dashboard(
        db, empresa_autorizada, sede_id, anio, mes
    )
    return dashboard


@router.get("/dashboard/exportar-excel")
def exportar_dashboard_excel(
    empresa_id: int | None = Query(default=None),
    sede_id: int | None = Query(default=None),
    anio: int = Query(default=datetime.now().year, ge=1900, le=2100),
    mes: int | None = Query(default=None, ge=1, le=12),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    empresa_autorizada = _empresa_id_autorizada(usuario, empresa_id)
    dashboard, empleados, perfiles = _cargar_dashboard(
        db, empresa_autorizada, sede_id, anio, mes
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Resumen"
    ws.append(["Perfil Sociodemográfico - Dashboard Activos/Inactivos"])
    ws.append(["Periodo", dashboard["periodo"]["etiqueta"]])
    ws.append(["Fecha de corte", dashboard["periodo"]["fecha_corte"]])
    ws.append([])
    ws.append(["Indicador", "Valor"])
    etiquetas_kpi = {
        "total_periodo": "Total periodo",
        "activos": "Activos",
        "inactivos": "Inactivos",
        "perfiles_registrados": "Perfiles registrados",
        "perfiles_completados": "Perfiles completados",
        "cobertura_perfil": "Cobertura perfil (%)",
        "sin_fecha_ingreso": "Sin fecha de ingreso",
        "datos_historicos_incompletos": "Datos históricos incompletos",
    }
    for clave, etiqueta in etiquetas_kpi.items():
        ws.append([etiqueta, dashboard["kpis"][clave]])
    ws.append([])
    ws.append(["Mes", "Activos", "Inactivos"])
    for item in dashboard["tendencia_mensual"]:
        ws.append([item["nombre"], item["activos"], item["inactivos"]])

    encabezado = PatternFill("solid", fgColor="173A8A")
    for fila in (1, 5, 15):
        for celda in ws[fila]:
            celda.font = Font(bold=True, color="FFFFFF")
            celda.fill = encabezado
    ws.column_dimensions["A"].width = 32
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 15

    detalle = wb.create_sheet("Detalle empleados")
    headers = [
        "Empleado",
        "Documento",
        "Empresa",
        "Sede",
        "Fecha ingreso",
        "Fecha retiro",
        "Estado al corte",
        "Perfil registrado",
        "Perfil completado",
    ]
    detalle.append(headers)
    fecha_corte = date.fromisoformat(dashboard["periodo"]["fecha_corte"])
    for empleado in empleados:
        detalle.append(
            [
                _valor_excel(valor)
                for valor in _detalle_empleado(
                    empleado, perfiles.get(empleado.id), fecha_corte
                )
            ]
        )
    for celda in detalle[1]:
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = encabezado
        celda.alignment = Alignment(horizontal="center", wrap_text=True)
    detalle.freeze_panes = "A2"
    detalle.auto_filter.ref = detalle.dimensions
    for indice, ancho in enumerate((30, 18, 28, 24, 15, 15, 18, 18, 18), 1):
        detalle.column_dimensions[get_column_letter(indice)].width = ancho

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    filename = f"dashboard_perfil_{anio}_{mes or 'anual'}.xlsx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/dashboard/exportar-pdf")
def exportar_dashboard_pdf(
    empresa_id: int | None = Query(default=None),
    sede_id: int | None = Query(default=None),
    anio: int = Query(default=datetime.now().year, ge=1900, le=2100),
    mes: int | None = Query(default=None, ge=1, le=12),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    empresa_autorizada = _empresa_id_autorizada(usuario, empresa_id)
    dashboard, empleados, perfiles = _cargar_dashboard(
        db, empresa_autorizada, sede_id, anio, mes
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=0.8 * cm,
        rightMargin=0.8 * cm,
        topMargin=0.8 * cm,
        bottomMargin=0.8 * cm,
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Perfil Sociodemográfico - Activos e Inactivos", styles["Title"]),
        Paragraph(
            f"Periodo: {escape(dashboard['periodo']['etiqueta'])} | "
            f"Corte: {dashboard['periodo']['fecha_corte']}",
            styles["Normal"],
        ),
        Spacer(1, 0.2 * cm),
    ]
    kpis = dashboard["kpis"]
    resumen = Table(
        [
            ["Total", "Activos", "Inactivos", "Perfiles", "Completados", "Cobertura", "Sin ingreso", "Histórico incompleto"],
            [
                kpis["total_periodo"],
                kpis["activos"],
                kpis["inactivos"],
                kpis["perfiles_registrados"],
                kpis["perfiles_completados"],
                f"{kpis['cobertura_perfil']}%",
                kpis["sin_fecha_ingreso"],
                kpis["datos_historicos_incompletos"],
            ],
        ],
        repeatRows=1,
    )
    estilo_tabla = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#173A8A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
    ]
    resumen.setStyle(TableStyle(estilo_tabla))
    story.extend([resumen, Spacer(1, 0.25 * cm), Paragraph("Detalle de empleados", styles["Heading2"])])

    headers = ["Empleado", "Documento", "Empresa", "Sede", "Ingreso", "Retiro", "Estado", "Perfil", "Completo"]
    datos = [headers]
    fecha_corte = date.fromisoformat(dashboard["periodo"]["fecha_corte"])
    for empleado in empleados:
        fila = _detalle_empleado(empleado, perfiles.get(empleado.id), fecha_corte)
        datos.append(
            [
                Paragraph(escape(str(valor or "")), styles["BodyText"])
                for valor in fila
            ]
        )
    tabla = Table(
        datos,
        colWidths=[4.0 * cm, 2.5 * cm, 3.5 * cm, 3.0 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 1.8 * cm, 1.8 * cm],
        repeatRows=1,
    )
    tabla.setStyle(TableStyle(estilo_tabla + [("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")])]))
    story.append(tabla)
    doc.build(story)
    buffer.seek(0)
    filename = f"dashboard_perfil_{anio}_{mes or 'anual'}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ── CRUD ────────────────────────────────────────────────────
@router.get(
    "/empleado/{empleado_id}",
    response_model=EmpleadoPerfilResponse,
    dependencies=[Depends(require_roles(ROLES_SST))],
)
def obtener_perfil(
    empleado_id: int,
    empresa_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    emp = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    _ensure_empleado(emp, empleado_id, db)
    perfil = _get_perfil_or_404(empleado_id, db, empresa_id)
    if not perfil:
        raise HTTPException(
            status_code=404,
            detail="Perfil sociodemográfico no encontrado para este empleado",
        )
    return perfil


@router.post(
    "",
    response_model=EmpleadoPerfilResponse,
    status_code=201,
    dependencies=[Depends(require_roles(ROLES_SST))],
)
def crear_perfil(data: EmpleadoPerfilCreate, db: Session = Depends(get_db)):
    emp = db.query(Empleado).filter(Empleado.id == data.empleado_id).first()
    _ensure_empleado(emp, data.empleado_id, db)

    existente = _get_perfil_or_404(data.empleado_id, db, data.empresa_id)
    if existente:
        raise HTTPException(
            status_code=409,
            detail="El empleado ya tiene un perfil sociodemográfico. Use PUT para actualizar.",
        )

    payload = data.model_dump(exclude_unset=True)
    perfil = EmpleadoPerfilSociodemografico(**payload)
    db.add(perfil)
    db.commit()
    db.refresh(perfil)
    logger.info("Perfil sociodemográfico creado para empleado %s", data.empleado_id)
    return perfil


@router.put(
    "/empleado/{empleado_id}",
    response_model=EmpleadoPerfilResponse,
    dependencies=[Depends(require_roles(ROLES_SST))],
)
def actualizar_perfil(
    empleado_id: int,
    data: EmpleadoPerfilUpdate,
    empresa_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    emp = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    _ensure_empleado(emp, empleado_id, db)

    perfil = _get_perfil_or_404(empleado_id, db, empresa_id)
    if not perfil:
        raise HTTPException(
            status_code=404,
            detail="Perfil sociodemográfico no encontrado. Use POST para crear.",
        )

    payload = data.model_dump(exclude_unset=True)
    for key, value in payload.items():
        setattr(perfil, key, value)
    db.commit()
    db.refresh(perfil)
    logger.info("Perfil sociodemográfico actualizado para empleado %s", empleado_id)
    return perfil


@router.delete(
    "/empleado/{empleado_id}",
    status_code=204,
    dependencies=[Depends(require_roles(ROLES_SST))],
)
def eliminar_perfil(
    empleado_id: int,
    empresa_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    perfil = _get_perfil_or_404(empleado_id, db, empresa_id)
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    db.delete(perfil)
    db.commit()
    logger.info("Perfil sociodemográfico eliminado para empleado %s", empleado_id)


# ── LISTA MASIVA ────────────────────────────────────────────
@router.get(
    "",
    response_model=list[EmpleadoPerfilResponse],
    dependencies=[Depends(require_roles(ROLES_SST))],
)
def listar_perfiles(
    empresa_id: int = Query(...),
    completado: bool | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(EmpleadoPerfilSociodemografico).filter(
        EmpleadoPerfilSociodemografico.empresa_id == empresa_id
    )
    if completado is not None:
        q = q.filter(EmpleadoPerfilSociodemografico.completado == completado)
    return q.order_by(EmpleadoPerfilSociodemografico.id.desc()).all()


# ── EXPORTACIÓN EXCEL ───────────────────────────────────────
@router.get(
    "/exportar-excel",
    dependencies=[Depends(require_roles(ROLES_SST))],
)
def exportar_perfiles_excel(
    empresa_id: int = Query(...),
    db: Session = Depends(get_db),
):
    perfiles = (
        db.query(EmpleadoPerfilSociodemografico)
        .filter(EmpleadoPerfilSociodemografico.empresa_id == empresa_id)
        .order_by(EmpleadoPerfilSociodemografico.id.desc())
        .all()
    )
    if not perfiles:
        raise HTTPException(
            status_code=404, detail="No hay perfiles sociodemográficos para exportar"
        )

    wb = Workbook()
    ws = wb.active
    ws.title = "Perfiles Sociodemográficos"

    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(
        start_color="2563EB", end_color="2563EB", fill_type="solid"
    )
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    headers = [
        "ID",
        "Empleado ID",
        "Nombres Completos",
        "Tipo Doc",
        "No. Documento",
        "Fecha Nac",
        "Lugar Nac",
        "Edad",
        "Étnia",
        "Teléfono",
        "Estado Civil",
        "Cónyuge",
        "Ocupación Cónyuge",
        "Dependientes",
        "Dirección",
        "Barrio",
        "Ciudad/Municipio",
        "Estrato",
        "Tipo Vivienda",
        "Transporte",
        "Tiempo Desplaz.",
        "Cargo Actual",
        "Área/Depto",
        "Tipo Contrato",
        "Tiempo Laborado",
        "Escolaridad",
        "EPS",
        "Fondo Pensiones",
        "RH",
        "Diagnóstico",
        "Actividad Física",
        "Cigarrillo",
        "Alcohol",
        "Talla Camisa",
        "Talla Pantalón",
        "Talla Calzado",
        "Ref. 1 Nombre",
        "Ref. 1 Teléfono",
        "Ref. 2 Nombre",
        "Ref. 2 Teléfono",
        "Consentimiento",
        "Completado",
        "Fuente",
    ]

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border

    for row_idx, p in enumerate(perfiles, 2):
        values = [
            p.id,
            p.empleado_id,
            p.nombres_completos,
            p.tipo_documento,
            p.numero_documento,
            p.fecha_nacimiento,
            p.lugar_nacimiento,
            p.edad,
            p.raza_pertenencia_etnica,
            p.telefono_celular,
            p.estado_civil,
            p.conyuge_nombre,
            p.conyuge_ocupacion,
            p.numero_dependientes,
            p.direccion_residencia,
            p.barrio,
            p.ciudad_municipio,
            p.estrato_socioeconomico,
            p.tipo_vivienda,
            p.medio_transporte,
            p.tiempo_desplazamiento,
            p.cargo_actual,
            p.area_departamento,
            p.tipo_contrato,
            p.tiempo_laborado,
            p.nivel_escolaridad,
            p.eps_actual,
            p.fondo_pensiones,
            p.tipo_rh,
            p.diagnostico_detalle if p.diagnostico_previo else "No",
            p.actividad_fisica,
            p.consumo_cigarrillo,
            p.consumo_alcohol,
            p.talla_camisa,
            p.talla_pantalon,
            p.talla_calzado,
            p.referencia_1_nombre,
            p.referencia_1_telefono,
            p.referencia_2_nombre,
            p.referencia_2_telefono,
            "Sí" if p.consentimiento_informado else "No",
            "Sí" if p.completado else "No",
            p.fuente,
        ]
        for col, val in enumerate(values, 1):
            cell = ws.cell(row=row_idx, column=col, value=val)
            cell.border = thin_border
            cell.alignment = Alignment(vertical="center")

    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    fecha = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"perfiles_sociodemograficos_{fecha}.xlsx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ── PLANTILLA EXCEL VACÍA ──────────────────────────────────
_PLANTILLA_HEADERS = [
    "Empleado ID",
    "Nombres Completos",
    "Tipo Doc",
    "No. Documento",
    "Libreta Militar",
    "Fecha Nacimiento (AAAA-MM-DD)",
    "Lugar Nacimiento",
    "Edad",
    "Raza / Pertenencia Étnica",
    "Teléfono / Celular",
    "Estado Civil",
    "Nombre Cónyuge",
    "Ocupación Cónyuge",
    "Edad Cónyuge",
    "Celular Cónyuge",
    "N° Dependientes",
    "Hijos (JSON: [{nombre,fecha_nacimiento,edad,escolaridad}])",
    "Dirección Residencia",
    "Barrio",
    "Ciudad / Municipio",
    "Estrato (1-6)",
    "Tipo Vivienda",
    "Medio Transporte",
    "Otro Transporte",
    "Tiempo Desplazamiento",
    "Cargo Actual",
    "Área / Depto",
    "Sede / Centro Trabajo",
    "Tipo Contrato",
    "Tiempo Laborado",
    "Antigüedad Cargo",
    "Última Empresa",
    "Nivel Escolaridad",
    "Detalle Títulos",
    "EPS Actual",
    "Fondo Pensiones",
    "Tipo RH",
    "Diagnóstico Previo (Sí/No)",
    "Detalle Diagnóstico",
    "Actividad Física (Sí/No)",
    "Consumo Cigarrillo (Nunca/Ocasional/Frecuente)",
    "Consumo Alcohol (Nunca/Ocasional/Frecuente)",
    "Talla Camisa",
    "Talla Pantalón",
    "Talla Chaqueta",
    "Talla Overol",
    "Talla Calzado",
    "Ref 1 Nombre",
    "Ref 1 Ocupación",
    "Ref 1 Teléfono",
    "Ref 2 Nombre",
    "Ref 2 Ocupación",
    "Ref 2 Teléfono",
    "Consentimiento (Sí/No)",
    "Fecha Firma (AAAA-MM-DD)",
    "Completado (Sí/No)",
]


@router.get(
    "/plantilla-excel",
    dependencies=[Depends(require_roles(ROLES_SST))],
)
def descargar_plantilla_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Plantilla Perfil Sociodemográfico"

    header_font = Font(bold=True, color="FFFFFF", size=10)
    header_fill = PatternFill(
        start_color="7C3AED", end_color="7C3AED", fill_type="solid"
    )
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    for col, header in enumerate(_PLANTILLA_HEADERS, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border
        ws.column_dimensions[get_column_letter(col)].width = 22

    ws.row_dimensions[1].height = 40

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=plantilla_perfil_sociodemografico.xlsx"
        },
    )


# ── IMPORTACIÓN EXCEL ───────────────────────────────────────
_PERFIL_FIELD_MAP = {
    1: "nombres_completos",
    2: "tipo_documento",
    3: "numero_documento",
    4: "libreta_militar",
    5: "fecha_nacimiento",
    6: "lugar_nacimiento",
    7: "edad",
    8: "raza_pertenencia_etnica",
    9: "telefono_celular",
    10: "estado_civil",
    11: "conyuge_nombre",
    12: "conyuge_ocupacion",
    13: "conyuge_edad",
    14: "conyuge_celular",
    15: "numero_dependientes",
    17: "direccion_residencia",
    18: "barrio",
    19: "ciudad_municipio",
    20: "estrato_socioeconomico",
    21: "tipo_vivienda",
    22: "medio_transporte",
    23: "medio_transporte_otro",
    24: "tiempo_desplazamiento",
    25: "cargo_actual",
    26: "area_departamento",
    27: "sede_centro_trabajo",
    28: "tipo_contrato",
    29: "tiempo_laborado",
    30: "antiguedad_cargo",
    31: "ultima_empresa",
    32: "nivel_escolaridad",
    33: "detalle_titulos",
    34: "eps_actual",
    35: "fondo_pensiones",
    36: "tipo_rh",
    37: "diagnostico_previo",
    38: "diagnostico_detalle",
    39: "actividad_fisica",
    40: "consumo_cigarrillo",
    41: "consumo_alcohol",
    42: "talla_camisa",
    43: "talla_pantalon",
    44: "talla_chaqueta",
    45: "talla_overol",
    46: "talla_calzado",
    47: "referencia_1_nombre",
    48: "referencia_1_ocupacion",
    49: "referencia_1_telefono",
    50: "referencia_2_nombre",
    51: "referencia_2_ocupacion",
    52: "referencia_2_telefono",
    53: "consentimiento_informado",
    54: "fecha_firma",
    55: "completado",
}

_INT_FIELDS = {"edad", "conyuge_edad", "numero_dependientes", "estrato_socioeconomico"}
_BOOL_FIELDS = {"diagnostico_previo", "consentimiento_informado", "completado"}


def _parse_bool(value):
    if value is None:
        return False
    s = str(value).strip().lower()
    return s in ("sí", "si", "true", "1", "yes")


def _parse_int(value):
    if value is None:
        return None
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return None


def _parse_fecha(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if hasattr(value, "date"):
        return value.date()
    s = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


@router.post(
    "/importar-excel",
    dependencies=[Depends(require_roles(ROLES_SST))],
)
async def importar_perfil_excel(
    archivo: UploadFile = File(...),
    empresa_id: int = Query(...),
    db: Session = Depends(get_db),
):
    if not archivo.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="El archivo debe ser un Excel (.xlsx)")

    contents = await archivo.read()
    try:
        wb = load_workbook(io.BytesIO(contents), read_only=True)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="No se pudo leer el archivo Excel. Verifique que no esté corrupto.",
        )

    ws = wb.active
    rows = list(ws.iter_rows(min_row=2, values_only=True))
    if not rows:
        raise HTTPException(
            status_code=400,
            detail="El archivo Excel está vacío o no tiene datos después del encabezado",
        )

    resultados = {"importados": 0, "actualizados": 0, "errores": []}

    for row_idx, row in enumerate(rows, 2):
        if not row or not any(cell is not None for cell in row):
            continue

        empleado_id = _parse_int(row[0]) if len(row) > 0 else None
        if not empleado_id:
            resultados["errores"].append(f"Fila {row_idx}: Falta Empleado ID")
            continue

        emp = db.query(Empleado).filter(Empleado.id == empleado_id).first()
        if not emp:
            resultados["errores"].append(
                f"Fila {row_idx}: Empleado ID {empleado_id} no encontrado"
            )
            continue

        data = {}
        for col_idx, field_name in _PERFIL_FIELD_MAP.items():
            if col_idx < len(row):
                value = row[col_idx]
                if value is not None:
                    if field_name in _INT_FIELDS:
                        data[field_name] = _parse_int(value)
                    elif field_name in _BOOL_FIELDS:
                        data[field_name] = _parse_bool(value)
                    elif field_name in ("fecha_nacimiento", "fecha_firma"):
                        data[field_name] = _parse_fecha(value)
                    else:
                        data[field_name] = (
                            str(value).strip() if str(value).strip() else None
                        )

        data["empresa_id"] = empresa_id
        data["empleado_id"] = empleado_id
        data["fuente"] = "IMPORTADO"

        perfil_existente = _get_perfil_or_404(empleado_id, db, empresa_id)
        if perfil_existente:
            for key, value in data.items():
                if key not in ("empresa_id", "empleado_id") and value is not None:
                    setattr(perfil_existente, key, value)
            resultados["actualizados"] += 1
        else:
            perfil = EmpleadoPerfilSociodemografico(**data)
            db.add(perfil)
            resultados["importados"] += 1

    db.commit()
    wb.close()
    logger.info(
        "Importación Excel: %d importados, %d actualizados, %d errores",
        resultados["importados"],
        resultados["actualizados"],
        len(resultados["errores"]),
    )
    return resultados

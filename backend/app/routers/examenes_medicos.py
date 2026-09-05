# ============================================================
# ROUTER EXÁMENES MÉDICOS SST - ERP SST PRO
# FASE 1.1.6.2.1 — EVIDENCIAS MÉDICAS ENTERPRISE
# Archivo: backend/app/routers/examenes_medicos.py
# ============================================================

from datetime import date, datetime, timedelta
from io import BytesIO
import json
import os
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.auth.dependencies import require_roles, require_permission, user_has_permission
from app.core.default_permissions import PERM_EXAMENES_DESCARGAR, PERM_REGISTROS_ELIMINAR, PERM_HISTORIA_CLINICA, PERM_CONCEPTO_MEDICO
from app.core.roles import MEDICO_OCUPACIONAL
from app.database import get_db
from app.models.area import Area
from app.models.cargo import Cargo
from app.models.empleado import Empleado
from app.models.empresa import Empresa
from app.models.examen_medico import ExamenMedico
from app.models.archivo_sst import ArchivoSST
from app.models.sede import Sede
from app.schemas.examen_medico_schema import (
    ExamenMedicoCreate,
    ExamenMedicoResponse,
    ExamenMedicoUpdate,
)
from app.schemas.archivo_sst_schema import ArchivoSSTResponse


router = APIRouter(prefix="/examenes-medicos", tags=["Exámenes Médicos SST"])
ROLES_SST = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]
ROLES_MEDICOS = ["MEDICO_OCUPACIONAL"]
DESCARGAR_EXAMENES = require_permission(PERM_EXAMENES_DESCARGAR)
ELIMINAR_REGISTROS = require_permission(PERM_REGISTROS_ELIMINAR)
MODULO_EVIDENCIAS_EXAMENES = "EXAMENES_MEDICOS"
BASE_UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads" / "examenes-medicos"
EXTENSIONES_EVIDENCIA = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
MIME_EVIDENCIA = {"application/pdf", "image/png", "image/jpeg", "image/webp"}


def _empresa_id_autorizada(usuario, empresa_id: int | None) -> int | None:
    if str(getattr(usuario, "rol", "") or "").upper() == "SUPER_ADMIN":
        return empresa_id
    usuario_empresa_id = getattr(usuario, "empresa_id", None)
    if usuario_empresa_id is None:
        raise HTTPException(status_code=403, detail="Usuario sin empresa asignada")
    if empresa_id is not None and int(usuario_empresa_id) != int(empresa_id):
        raise HTTPException(status_code=403, detail="No tiene permisos sobre esta empresa")
    return int(usuario_empresa_id)


def _puede_ver_historia_clinica(usuario, db: Session) -> bool:
    """Verifica si el usuario puede acceder a información clínica detallada."""
    from app.core.roles import normalizar_rol
    rol = normalizar_rol(usuario.rol)
    if rol == MEDICO_OCUPACIONAL:
        return True
    if user_has_permission(db, usuario, PERM_HISTORIA_CLINICA):
        return True
    return False


def _puede_ver_concepto_medico(usuario, db: Session) -> bool:
    """Verifica si el usuario puede acceder al concepto médico de aptitud."""
    from app.core.roles import normalizar_rol
    rol = normalizar_rol(usuario.rol)
    if rol == MEDICO_OCUPACIONAL:
        return True
    if _puede_ver_historia_clinica(usuario, db):
        return True
    if user_has_permission(db, usuario, PERM_CONCEPTO_MEDICO):
        return True
    return False


def _exigir_historia_clinica(usuario, db: Session) -> None:
    """Exige permiso de historia clínica para adjuntos y reportes clínicos."""
    if not _puede_ver_historia_clinica(usuario, db):
        raise HTTPException(
            status_code=403,
            detail="Se requiere permiso de historia clínica para esta operación",
        )


def _sanitizar_respuesta_medica(examen: ExamenMedicoResponse, usuario, db: Session) -> ExamenMedicoResponse:
    """Filtra campos sensibles de información médica según los permisos del usuario."""
    if not _puede_ver_historia_clinica(usuario, db):
        examen.restricciones = "[ACCESO RESTRINGIDO - Información clínica reservada]"
        examen.observaciones = "[ACCESO RESTRINGIDO - Información clínica reservada]"
        examen.examenes_aplicados = None
    if not _puede_ver_concepto_medico(usuario, db):
        examen.concepto = "[ACCESO RESTRINGIDO - Concepto médico reservado]"
    return examen


# ============================================================
# Helpers
# ============================================================
def _limpiar_texto(valor):
    if valor is None:
        return None
    valor = str(valor).strip()
    return valor if valor else None


def _normalizar_upper(valor, default=None):
    valor = _limpiar_texto(valor)
    return valor.upper() if valor else default


def _calcular_estado(fecha_vencimiento):
    if not fecha_vencimiento:
        return "VIGENTE"

    hoy = date.today()
    if fecha_vencimiento < hoy:
        return "VENCIDO"
    if fecha_vencimiento <= hoy + timedelta(days=30):
        return "PROXIMO_VENCER"
    return "VIGENTE"


def _dias_vencimiento(fecha_vencimiento):
    if not fecha_vencimiento:
        return None
    return (fecha_vencimiento - date.today()).days

def _texto(valor, defecto="Sin dato"):
    if valor is None:
        return defecto
    valor = str(valor).strip()
    return valor if valor else defecto


def _fecha(valor):
    if not valor:
        return ""
    if isinstance(valor, (datetime, date)):
        return valor.strftime("%Y-%m-%d")
    return str(valor)


def _nombre_archivo(prefijo: str, extension: str):
    fecha = datetime.now().strftime("%Y%m%d_%H%M")
    return f"{prefijo}_{fecha}.{extension}"


def _label_tipo(value):
    return {
        "INGRESO": "Ingreso",
        "PERIODICO": "Periódico",
        "RETIRO": "Retiro",
        "POST_INCAPACIDAD": "Post incapacidad",
        "RETORNO_LABORAL": "Retorno laboral",
    }.get((value or "").upper(), _texto(value, "Sin tipo"))


def _label_concepto(value):
    return {
        "APTO": "Apto",
        "APTO_CON_RESTRICCIONES": "Apto con restricciones",
        "NO_APTO": "No apto",
    }.get((value or "").upper(), _texto(value, "Sin concepto"))


def _label_estado(value):
    return {
        "VIGENTE": "Vigente",
        "PROXIMO_VENCER": "Próximo a vencer",
        "VENCIDO": "Vencido",
    }.get((value or "").upper(), _texto(value, "Sin estado"))


def _nombre_empleado(examen):
    empleado = getattr(examen, "empleado", None)
    if not empleado:
        return "Sin empleado"
    return _texto(f"{empleado.nombres or ''} {empleado.apellidos or ''}".strip(), "Sin empleado")


def _documento_empleado(examen):
    empleado = getattr(examen, "empleado", None)
    return _texto(getattr(empleado, "documento", None), "")


def _empresa_examen(examen):
    empleado = getattr(examen, "empleado", None)
    return _texto(empleado.empresa.nombre if empleado and empleado.empresa else None)


def _sede_examen(examen):
    empleado = getattr(examen, "empleado", None)
    return _texto(empleado.sede.nombre if empleado and empleado.sede else None)


def _area_examen(examen):
    empleado = getattr(examen, "empleado", None)
    return _texto(empleado.area.nombre if empleado and empleado.area else None)


def _cargo_examen(examen):
    empleado = getattr(examen, "empleado", None)
    return _texto(empleado.cargo.nombre if empleado and empleado.cargo else None)


def _stream_excel(wb: Workbook, filename: str):
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _stream_pdf(buffer: BytesIO, filename: str):
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _validar_empleado(db: Session, empleado_id: int, empresa_id: int | None = None):
    query = (
        db.query(Empleado)
        .options(
            joinedload(Empleado.empresa),
            joinedload(Empleado.sede),
            joinedload(Empleado.area),
            joinedload(Empleado.cargo),
        )
        .filter(Empleado.id == empleado_id)
    )
    if empresa_id:
        query = query.filter(Empleado.empresa_id == empresa_id)
    empleado = query.first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado


def _payload_limpio(data):
    payload = data.model_dump(exclude_unset=True)

    for key in ["tipo_examen", "concepto", "estado"]:
        if key in payload and payload[key] is not None:
            payload[key] = _normalizar_upper(payload[key])

    for key in ["medico_ocupacional", "entidad_salud", "restricciones", "observaciones"]:
        if key in payload:
            payload[key] = _limpiar_texto(payload[key])

    if "examenes_aplicados" in payload:
        valor = payload["examenes_aplicados"]
        if isinstance(valor, list):
            payload["examenes_aplicados"] = json.dumps(valor, ensure_ascii=False)
        elif valor is None:
            payload["examenes_aplicados"] = None

    if payload.get("fecha_vencimiento"):
        payload["estado"] = _calcular_estado(payload.get("fecha_vencimiento"))
    elif payload.get("estado") is None:
        payload["estado"] = "VIGENTE"

    return payload


def _examen_to_response(examen: ExamenMedico) -> ExamenMedicoResponse:
    data = ExamenMedicoResponse.model_validate(examen)
    empleado = examen.empleado

    if empleado:
        nombre = f"{empleado.nombres or ''} {empleado.apellidos or ''}".strip()
        data.empleado_documento = empleado.documento
        data.empleado_nombre = nombre or None
        data.empleado_correo = empleado.correo
        data.empresa_id = empleado.empresa_id
        data.sede_id = empleado.sede_id
        data.area_id = empleado.area_id
        data.cargo_id = empleado.cargo_id
        data.empresa_nombre = empleado.empresa.nombre if empleado.empresa else None
        data.sede_nombre = empleado.sede.nombre if empleado.sede else None
        data.area_nombre = empleado.area.nombre if empleado.area else None
        data.cargo_nombre = empleado.cargo.nombre if empleado.cargo else None

    data.estado = _calcular_estado(examen.fecha_vencimiento)
    data.dias_vencimiento = _dias_vencimiento(examen.fecha_vencimiento)
    return data


def _query_examenes_filtrada(
    db: Session,
    empresa_id: int | None = None,
    sede_id: int | None = None,
    area_id: int | None = None,
    cargo_id: int | None = None,
    empleado_id: int | None = None,
    tipo_examen: str | None = None,
    concepto: str | None = None,
    estado: str | None = None,
    activo: bool | None = None,
    q: str | None = None,
):
    query = (
        db.query(ExamenMedico)
        .join(Empleado, ExamenMedico.empleado_id == Empleado.id)
        .options(
            joinedload(ExamenMedico.empleado).joinedload(Empleado.empresa),
            joinedload(ExamenMedico.empleado).joinedload(Empleado.sede),
            joinedload(ExamenMedico.empleado).joinedload(Empleado.area),
            joinedload(ExamenMedico.empleado).joinedload(Empleado.cargo),
        )
    )

    if empresa_id:
        query = query.filter(Empleado.empresa_id == empresa_id)
    if sede_id:
        query = query.filter(Empleado.sede_id == sede_id)
    if area_id:
        query = query.filter(Empleado.area_id == area_id)
    if cargo_id:
        query = query.filter(Empleado.cargo_id == cargo_id)
    if empleado_id:
        query = query.filter(ExamenMedico.empleado_id == empleado_id)
    if tipo_examen:
        query = query.filter(func.upper(ExamenMedico.tipo_examen) == tipo_examen.upper().strip())
    if concepto:
        query = query.filter(func.upper(ExamenMedico.concepto) == concepto.upper().strip())
    if activo is not None:
        query = query.filter(ExamenMedico.activo == activo)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Empleado.nombres.ilike(like),
                Empleado.apellidos.ilike(like),
                Empleado.documento.ilike(like),
                ExamenMedico.medico_ocupacional.ilike(like),
                ExamenMedico.entidad_salud.ilike(like),
            )
        )

    examenes = query.order_by(ExamenMedico.id.desc())

    if estado:
        estado_up = estado.upper().strip()
        ids = []
        for examen in examenes.all():
            if _calcular_estado(examen.fecha_vencimiento) == estado_up:
                ids.append(examen.id)
        if not ids:
            return db.query(ExamenMedico).filter(False)
        return (
            db.query(ExamenMedico)
            .options(
                joinedload(ExamenMedico.empleado).joinedload(Empleado.empresa),
                joinedload(ExamenMedico.empleado).joinedload(Empleado.sede),
                joinedload(ExamenMedico.empleado).joinedload(Empleado.area),
                joinedload(ExamenMedico.empleado).joinedload(Empleado.cargo),
            )
            .filter(ExamenMedico.id.in_(ids))
            .order_by(ExamenMedico.id.desc())
        )

    return examenes


def _agrupar_examenes(examenes, key_func, default="Sin dato"):
    tmp = {}
    for examen in examenes:
        nombre = key_func(examen) or default
        nombre = str(nombre).strip() or default
        tmp[nombre] = tmp.get(nombre, 0) + 1
    return [{"name": k, "value": v} for k, v in sorted(tmp.items(), key=lambda x: x[1], reverse=True)]


# ============================================================
# Dashboard / Analytics
# ============================================================
@router.get("/dashboard")
def dashboard_examenes_medicos(
    empresa_id: int | None = None,
    sede_id: int | None = None,
    area_id: int | None = None,
    cargo_id: int | None = None,
    empleado_id: int | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    tenant_id = _empresa_id_autorizada(usuario, empresa_id)
    if empleado_id is not None and not _puede_ver_concepto_medico(usuario, db):
        raise HTTPException(
            status_code=403,
            detail="Se requiere permiso de concepto médico para analítica por empleado",
        )
    examenes = _query_examenes_filtrada(
        db=db,
        empresa_id=tenant_id,
        sede_id=sede_id,
        area_id=area_id,
        cargo_id=cargo_id,
        empleado_id=empleado_id,
        activo=True,
    ).all()

    total = len(examenes)
    estados = [_calcular_estado(e.fecha_vencimiento) for e in examenes]
    conceptos = [(e.concepto or "").upper() for e in examenes]

    vigentes = estados.count("VIGENTE")
    proximos = estados.count("PROXIMO_VENCER")
    vencidos = estados.count("VENCIDO")
    aptos = conceptos.count("APTO")
    con_restricciones = conceptos.count("APTO_CON_RESTRICCIONES")
    no_aptos = conceptos.count("NO_APTO")

    indice_cumplimiento = round((vigentes / total) * 100, 1) if total else 100
    pendientes_criticos = proximos + vencidos + con_restricciones + no_aptos

    recomendaciones = []
    if vencidos:
        recomendaciones.append("Prioriza la renovación de exámenes médicos vencidos.")
    if proximos:
        recomendaciones.append("Programa exámenes próximos a vencer dentro de los próximos 30 días.")
    if con_restricciones:
        recomendaciones.append("Revisa restricciones médicas y valida ajustes al puesto de trabajo.")
    if no_aptos:
        recomendaciones.append("Gestiona casos NO APTOS con acompañamiento médico ocupacional.")
    if not recomendaciones:
        recomendaciones.append("Gestión médica ocupacional estable. Mantén seguimiento periódico.")

    return {
        "kpis": {
            "total": total,
            "vigentes": vigentes,
            "proximos_vencer": proximos,
            "vencidos": vencidos,
            "aptos": aptos,
            "con_restricciones": con_restricciones,
            "no_aptos": no_aptos,
            "indice_cumplimiento": indice_cumplimiento,
            "pendientes_criticos": pendientes_criticos,
        },
        "charts": {
            "por_tipo": _agrupar_examenes(examenes, lambda e: e.tipo_examen),
            "por_concepto": _agrupar_examenes(examenes, lambda e: e.concepto),
            "por_estado": _agrupar_examenes(examenes, lambda e: _calcular_estado(e.fecha_vencimiento)),
            "por_empresa": _agrupar_examenes(examenes, lambda e: e.empleado.empresa.nombre if e.empleado and e.empleado.empresa else "Sin empresa"),
            "por_sede": _agrupar_examenes(examenes, lambda e: e.empleado.sede.nombre if e.empleado and e.empleado.sede else "Sin sede"),
            "por_cargo": _agrupar_examenes(examenes, lambda e: e.empleado.cargo.nombre if e.empleado and e.empleado.cargo else "Sin cargo"),
        },
        "alertas": {
            "proximos_vencer": proximos,
            "vencidos": vencidos,
            "con_restricciones": con_restricciones,
            "no_aptos": no_aptos,
        },
        "recomendaciones": recomendaciones,
    }






# ============================================================
# FASE 1.1.6.4 — Exportación PDF / Excel Exámenes Médicos SST
# ============================================================
def _examenes_exportables(
    db: Session,
    empresa_id: int | None = None,
    sede_id: int | None = None,
    area_id: int | None = None,
    cargo_id: int | None = None,
    empleado_id: int | None = None,
    tipo_examen: str | None = None,
    concepto: str | None = None,
    estado: str | None = None,
    activo: bool | None = True,
    q: str | None = None,
):
    return _query_examenes_filtrada(
        db=db,
        empresa_id=empresa_id,
        sede_id=sede_id,
        area_id=area_id,
        cargo_id=cargo_id,
        empleado_id=empleado_id,
        tipo_examen=tipo_examen,
        concepto=concepto,
        estado=estado,
        activo=activo,
        q=q,
    ).all()


def _crear_excel_examenes(
    examenes,
    titulo="Exámenes Médicos SST",
    mostrar_concepto: bool = True,
    mostrar_historia: bool = True,
):
    wb = Workbook()
    ws = wb.active
    ws.title = "Exámenes Médicos"

    header_fill = PatternFill("solid", fgColor="075985")
    sub_fill = PatternFill("solid", fgColor="E0F2FE")
    white_font = Font(color="FFFFFF", bold=True)
    title_font = Font(color="075985", bold=True, size=16)
    bold_font = Font(bold=True, color="0F172A")
    border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1"),
    )

    headers = [
        "ID", "Documento", "Empleado", "Empresa", "Sede", "Área", "Cargo",
        "Tipo examen", "Concepto", "Médico ocupacional", "Entidad / IPS",
        "Fecha examen", "Fecha vencimiento", "Días vencimiento", "Estado",
        "Restricciones", "Observaciones",
    ]

    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    ws.cell(1, 1, titulo)
    ws.cell(1, 1).font = title_font
    ws.cell(1, 1).alignment = Alignment(horizontal="center")

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(headers))
    ws.cell(2, 1, f"ERP SST PRO · Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} · Total: {len(examenes)}")
    ws.cell(2, 1).alignment = Alignment(horizontal="center")

    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=4, column=col, value=header)
        cell.fill = header_fill
        cell.font = white_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border

    for row_idx, examen in enumerate(examenes, start=5):
        estado_real = _calcular_estado(examen.fecha_vencimiento)
        values = [
            examen.id,
            _documento_empleado(examen),
            _nombre_empleado(examen),
            _empresa_examen(examen),
            _sede_examen(examen),
            _area_examen(examen),
            _cargo_examen(examen),
            _label_tipo(examen.tipo_examen),
            _label_concepto(examen.concepto) if mostrar_concepto else "[RESTRINGIDO]",
            _texto(examen.medico_ocupacional),
            _texto(examen.entidad_salud),
            _fecha(examen.fecha_examen),
            _fecha(examen.fecha_vencimiento),
            _dias_vencimiento(examen.fecha_vencimiento),
            _label_estado(estado_real),
            _texto(examen.restricciones, "") if mostrar_historia else "",
            _texto(examen.observaciones, "") if mostrar_historia else "",
        ]
        for col_idx, value in enumerate(values, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.border = border
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if col_idx in [8, 9, 15]:
                cell.fill = sub_fill
                cell.font = bold_font

    for idx, column_cells in enumerate(ws.columns, start=1):
        max_len = 12
        for cell in column_cells:
            try:
                max_len = max(max_len, len(str(cell.value or "")))
            except Exception:
                pass
        ws.column_dimensions[get_column_letter(idx)].width = min(max_len + 2, 38)

    ws.freeze_panes = "A5"
    return wb


def _crear_pdf_tabla(
    examenes,
    titulo="Reporte General de Exámenes Médicos SST",
    subtitulo=None,
    mostrar_concepto: bool = True,
):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=0.9 * cm,
        leftMargin=0.9 * cm,
        topMargin=0.9 * cm,
        bottomMargin=0.9 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TituloExamenes",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=16,
        textColor=colors.HexColor("#075985"),
        spaceAfter=8,
    )
    normal = ParagraphStyle("NormalExamSmall", parent=styles["BodyText"], fontSize=7, leading=9)

    story = [
        Paragraph(titulo, title_style),
        Paragraph(subtitulo or f"ERP SST PRO · Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} · Total registros: {len(examenes)}", styles["Normal"]),
        Spacer(1, 0.22 * cm),
    ]

    headers = ["Empleado", "Documento", "Empresa", "Cargo", "Tipo", "Concepto", "Examen", "Vence", "Estado"]
    data = [headers]
    for examen in examenes:
        estado_real = _calcular_estado(examen.fecha_vencimiento)
        data.append([
            Paragraph(_nombre_empleado(examen), normal),
            Paragraph(_documento_empleado(examen), normal),
            Paragraph(_empresa_examen(examen), normal),
            Paragraph(_cargo_examen(examen), normal),
            Paragraph(_label_tipo(examen.tipo_examen), normal),
            Paragraph(_label_concepto(examen.concepto) if mostrar_concepto else "[RESTRINGIDO]", normal),
            Paragraph(_fecha(examen.fecha_examen), normal),
            Paragraph(_fecha(examen.fecha_vencimiento) or "Sin venc.", normal),
            Paragraph(_label_estado(estado_real), normal),
        ])

    table = Table(data, colWidths=[4.0 * cm, 2.3 * cm, 3.5 * cm, 3.2 * cm, 2.7 * cm, 3.2 * cm, 2.1 * cm, 2.1 * cm, 2.5 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#075985")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(table)
    doc.build(story)
    return buffer


@router.get("/export/excel")
def exportar_examenes_medicos_excel(
    empresa_id: int | None = None,
    sede_id: int | None = None,
    area_id: int | None = None,
    cargo_id: int | None = None,
    empleado_id: int | None = None,
    tipo_examen: str | None = None,
    concepto: str | None = None,
    estado: str | None = None,
    activo: bool | None = True,
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(DESCARGAR_EXAMENES),
):
    tenant_id = _empresa_id_autorizada(usuario, empresa_id)
    examenes = _examenes_exportables(db, tenant_id, sede_id, area_id, cargo_id, empleado_id, tipo_examen, concepto, estado, activo, q)
    wb = _crear_excel_examenes(
        examenes,
        "Exámenes Médicos SST - Reporte General",
        mostrar_concepto=_puede_ver_concepto_medico(usuario, db),
        mostrar_historia=_puede_ver_historia_clinica(usuario, db),
    )
    return _stream_excel(wb, _nombre_archivo("examenes_medicos_sst", "xlsx"))


@router.get("/export/pdf")
def exportar_examenes_medicos_pdf(
    empresa_id: int | None = None,
    sede_id: int | None = None,
    area_id: int | None = None,
    cargo_id: int | None = None,
    empleado_id: int | None = None,
    tipo_examen: str | None = None,
    concepto: str | None = None,
    estado: str | None = None,
    activo: bool | None = True,
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(DESCARGAR_EXAMENES),
):
    tenant_id = _empresa_id_autorizada(usuario, empresa_id)
    examenes = _examenes_exportables(db, tenant_id, sede_id, area_id, cargo_id, empleado_id, tipo_examen, concepto, estado, activo, q)
    buffer = _crear_pdf_tabla(
        examenes,
        mostrar_concepto=_puede_ver_concepto_medico(usuario, db),
    )
    return _stream_pdf(buffer, _nombre_archivo("reporte_examenes_medicos_sst", "pdf"))


@router.get("/export/vencimientos/pdf")
def exportar_reporte_vencimientos_pdf(
    empresa_id: int | None = None,
    sede_id: int | None = None,
    area_id: int | None = None,
    cargo_id: int | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(DESCARGAR_EXAMENES),
):
    tenant_id = _empresa_id_autorizada(usuario, empresa_id)
    examenes = _examenes_exportables(db, tenant_id=tenant_id, sede_id=sede_id, area_id=area_id, cargo_id=cargo_id, activo=True)
    examenes = [e for e in examenes if _calcular_estado(e.fecha_vencimiento) in {"PROXIMO_VENCER", "VENCIDO"}]
    buffer = _crear_pdf_tabla(
        examenes,
        titulo="Reporte de Vencimientos Médicos SST",
        subtitulo=f"Incluye exámenes vencidos y próximos a vencer · Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} · Total: {len(examenes)}",
        mostrar_concepto=_puede_ver_concepto_medico(usuario, db),
    )
    return _stream_pdf(buffer, _nombre_archivo("vencimientos_examenes_medicos", "pdf"))


@router.get("/export/restricciones/pdf")
def exportar_reporte_restricciones_pdf(
    empresa_id: int | None = None,
    sede_id: int | None = None,
    area_id: int | None = None,
    cargo_id: int | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(DESCARGAR_EXAMENES),
):
    tenant_id = _empresa_id_autorizada(usuario, empresa_id)
    _exigir_historia_clinica(usuario, db)
    examenes = _examenes_exportables(db, tenant_id=tenant_id, sede_id=sede_id, area_id=area_id, cargo_id=cargo_id, activo=True)
    examenes = [e for e in examenes if (e.concepto or "").upper() == "APTO_CON_RESTRICCIONES" or _limpiar_texto(e.restricciones)]
    buffer = _crear_pdf_tabla(
        examenes,
        titulo="Reporte de Restricciones Médicas SST",
        subtitulo=f"Incluye conceptos con restricciones y observaciones médicas · Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} · Total: {len(examenes)}",
    )
    return _stream_pdf(buffer, _nombre_archivo("restricciones_medicas_sst", "pdf"))


@router.get("/{examen_id}/export/pdf")
def exportar_ficha_examen_medico_pdf(
    examen_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(DESCARGAR_EXAMENES),
):
    tenant_id = _empresa_id_autorizada(usuario, None)
    _exigir_historia_clinica(usuario, db)
    filtros = [ExamenMedico.id == examen_id]
    if tenant_id is not None:
        filtros.append(ExamenMedico.empleado.has(Empleado.empresa_id == tenant_id))
    examen = (
        db.query(ExamenMedico)
        .options(
            joinedload(ExamenMedico.empleado).joinedload(Empleado.empresa),
            joinedload(ExamenMedico.empleado).joinedload(Empleado.sede),
            joinedload(ExamenMedico.empleado).joinedload(Empleado.area),
            joinedload(ExamenMedico.empleado).joinedload(Empleado.cargo),
        )
        .filter(*filtros)
        .first()
    )
    if not examen:
        raise HTTPException(status_code=404, detail="Examen médico no encontrado")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.4 * cm, leftMargin=1.4 * cm, topMargin=1.2 * cm, bottomMargin=1.2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TituloFichaExamen", parent=styles["Title"], alignment=TA_CENTER, fontSize=17, textColor=colors.HexColor("#075985"))
    section_style = ParagraphStyle("SeccionExamen", parent=styles["Heading2"], fontSize=11, textColor=colors.HexColor("#075985"), spaceBefore=10, spaceAfter=6)

    def tabla_pares(rows):
        tabla = Table(rows, colWidths=[5.2 * cm, 10.8 * cm])
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E0F2FE")),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#0F172A")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]))
        return tabla

    estado_real = _calcular_estado(examen.fecha_vencimiento)
    story = [
        Paragraph("Ficha Individual de Examen Médico SST", title_style),
        Paragraph(f"ERP SST PRO · Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]),
        Spacer(1, 0.25 * cm),
        Paragraph("Información del empleado", section_style),
        tabla_pares([
            ["Empleado", _nombre_empleado(examen)],
            ["Documento", _documento_empleado(examen)],
            ["Empresa", _empresa_examen(examen)],
            ["Sede", _sede_examen(examen)],
            ["Área", _area_examen(examen)],
            ["Cargo", _cargo_examen(examen)],
        ]),
        Paragraph("Información del examen", section_style),
        tabla_pares([
            ["Tipo de examen", _label_tipo(examen.tipo_examen)],
            ["Concepto médico", _label_concepto(examen.concepto)],
            ["Estado", _label_estado(estado_real)],
            ["Fecha examen", _fecha(examen.fecha_examen)],
            ["Fecha vencimiento", _fecha(examen.fecha_vencimiento) or "Sin vencimiento"],
            ["Días para vencimiento", _texto(_dias_vencimiento(examen.fecha_vencimiento), "Sin dato")],
            ["Médico ocupacional", _texto(examen.medico_ocupacional)],
            ["Entidad / IPS", _texto(examen.entidad_salud)],
        ]),
        Paragraph("Restricciones y observaciones", section_style),
        tabla_pares([
            ["Restricciones", _texto(examen.restricciones, "Sin restricciones")],
            ["Observaciones", _texto(examen.observaciones, "Sin observaciones")],
        ]),
    ]

    doc.build(story)
    documento = _documento_empleado(examen) or examen.id
    return _stream_pdf(buffer, f"ficha_examen_medico_{documento}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf")

# ============================================================
# Evidencias Médicas SST
# ============================================================
def _validar_archivo_evidencia(file: UploadFile):
    extension = os.path.splitext(file.filename or "")[1].lower()
    if extension not in EXTENSIONES_EVIDENCIA:
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten evidencias PDF o imágenes PNG/JPG/WEBP.",
        )
    if file.content_type and file.content_type not in MIME_EVIDENCIA:
        raise HTTPException(
            status_code=400,
            detail="Tipo MIME no permitido para evidencia médica.",
        )
    return extension


def _obtener_examen_base(db: Session, examen_id: int, empresa_id: int | None = None) -> ExamenMedico:
    query = (
        db.query(ExamenMedico)
        .options(joinedload(ExamenMedico.empleado))
        .filter(ExamenMedico.id == examen_id)
    )
    if empresa_id:
        query = query.filter(ExamenMedico.empleado.has(Empleado.empresa_id == empresa_id))
    examen = query.first()
    if not examen:
        raise HTTPException(status_code=404, detail="Examen médico no encontrado")
    if not examen.empleado:
        raise HTTPException(status_code=400, detail="El examen no tiene empleado asociado")
    if not examen.empleado.empresa_id:
        raise HTTPException(status_code=400, detail="El empleado no tiene empresa asociada")
    return examen


@router.get("/{examen_id}/evidencias", response_model=list[ArchivoSSTResponse])
def listar_evidencias_examen_medico(
    examen_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(DESCARGAR_EXAMENES),
):
    tenant_id = _empresa_id_autorizada(usuario, None)
    _exigir_historia_clinica(usuario, db)
    _obtener_examen_base(db, examen_id, tenant_id)
    return (
        db.query(ArchivoSST)
        .filter(
            ArchivoSST.modulo == MODULO_EVIDENCIAS_EXAMENES,
            ArchivoSST.referencia_id == examen_id,
            ArchivoSST.empresa_id == tenant_id,
            ArchivoSST.activo == True,
        )
        .order_by(ArchivoSST.id.desc())
        .all()
    )


@router.post("/{examen_id}/evidencias", response_model=ArchivoSSTResponse)
def subir_evidencia_examen_medico(
    examen_id: int,
    descripcion: str | None = Form(None),
    tipo_evidencia: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    tenant_id = _empresa_id_autorizada(usuario, None)
    _exigir_historia_clinica(usuario, db)
    examen = _obtener_examen_base(db, examen_id, tenant_id)
    extension = _validar_archivo_evidencia(file)

    BASE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    nombre_archivo = f"{uuid4().hex}{extension}"
    ruta_fisica = BASE_UPLOAD_DIR / nombre_archivo

    try:
        with ruta_fisica.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    registro = ArchivoSST(
        empresa_id=tenant_id,
        usuario_id=getattr(usuario, "id", None),
        tipo="EVIDENCIA",
        nombre_original=file.filename or nombre_archivo,
        nombre_archivo=nombre_archivo,
        ruta=str(ruta_fisica),
        url=f"/uploads/examenes-medicos/{nombre_archivo}",
        extension=extension.replace(".", ""),
        mime_type=file.content_type,
        tamano_bytes=ruta_fisica.stat().st_size,
        modulo=MODULO_EVIDENCIAS_EXAMENES,
        referencia_id=examen_id,
        descripcion=f"[{_normalizar_upper(tipo_evidencia, 'OTRO')}] {_limpiar_texto(descripcion) or 'Evidencia médica ocupacional'}",
        activo=True,
    )
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


@router.delete("/{examen_id}/evidencias/{archivo_id}")
def eliminar_evidencia_examen_medico(
    examen_id: int,
    archivo_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(ELIMINAR_REGISTROS),
):
    tenant_id = _empresa_id_autorizada(usuario, None)
    _exigir_historia_clinica(usuario, db)
    _obtener_examen_base(db, examen_id, tenant_id)
    archivo = (
        db.query(ArchivoSST)
        .filter(
            ArchivoSST.id == archivo_id,
            ArchivoSST.modulo == MODULO_EVIDENCIAS_EXAMENES,
            ArchivoSST.referencia_id == examen_id,
            ArchivoSST.empresa_id == tenant_id,
            ArchivoSST.activo == True,
        )
        .first()
    )
    if not archivo:
        raise HTTPException(status_code=404, detail="Evidencia médica no encontrada")
    archivo.activo = False
    db.commit()
    return {"ok": True, "mensaje": "Evidencia médica eliminada correctamente"}


# ============================================================
# CRUD
# ============================================================
@router.get("/", response_model=list[ExamenMedicoResponse])
def listar_examenes_medicos(
    empresa_id: int | None = None,
    sede_id: int | None = None,
    area_id: int | None = None,
    cargo_id: int | None = None,
    empleado_id: int | None = None,
    tipo_examen: str | None = None,
    concepto: str | None = None,
    estado: str | None = None,
    activo: bool | None = None,
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    tenant_id = _empresa_id_autorizada(usuario, empresa_id)
    examenes = _query_examenes_filtrada(
        db=db,
        empresa_id=tenant_id,
        sede_id=sede_id,
        area_id=area_id,
        cargo_id=cargo_id,
        empleado_id=empleado_id,
        tipo_examen=tipo_examen,
        concepto=concepto,
        estado=estado,
        activo=activo,
        q=q,
    ).all()
    return [_sanitizar_respuesta_medica(_examen_to_response(e), usuario, db) for e in examenes]


@router.post("/", response_model=ExamenMedicoResponse)
def crear_examen_medico(
    data: ExamenMedicoCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    tenant_id = _empresa_id_autorizada(usuario, None)
    _validar_empleado(db, data.empleado_id, tenant_id)
    payload = _payload_limpio(data)
    examen = ExamenMedico(**payload, empleado_id=data.empleado_id)
    db.add(examen)
    db.commit()
    db.refresh(examen)
    return _examen_to_response(examen)


@router.get("/{examen_id}", response_model=ExamenMedicoResponse)
def obtener_examen_medico(
    examen_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    tenant_id = _empresa_id_autorizada(usuario, None)
    examen = (
        db.query(ExamenMedico)
        .options(
            joinedload(ExamenMedico.empleado).joinedload(Empleado.empresa),
            joinedload(ExamenMedico.empleado).joinedload(Empleado.sede),
            joinedload(ExamenMedico.empleado).joinedload(Empleado.area),
            joinedload(ExamenMedico.empleado).joinedload(Empleado.cargo),
        )
        .filter(ExamenMedico.id == examen_id, ExamenMedico.empleado.has(Empleado.empresa_id == tenant_id))
        .first()
    )
    if not examen:
        raise HTTPException(status_code=404, detail="Examen médico no encontrado")
    return _sanitizar_respuesta_medica(_examen_to_response(examen), usuario, db)


@router.put("/{examen_id}", response_model=ExamenMedicoResponse)
def actualizar_examen_medico(
    examen_id: int,
    data: ExamenMedicoUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    tenant_id = _empresa_id_autorizada(usuario, None)
    examen = db.query(ExamenMedico).filter(ExamenMedico.id == examen_id, ExamenMedico.empleado.has(Empleado.empresa_id == tenant_id)).first()
    if not examen:
        raise HTTPException(status_code=404, detail="Examen médico no encontrado")

    payload = _payload_limpio(data)
    if payload.get("empleado_id"):
        _validar_empleado(db, payload["empleado_id"], tenant_id)

    for key, value in payload.items():
        setattr(examen, key, value)

    examen.fecha_actualizacion = datetime.now()
    if examen.fecha_vencimiento:
        examen.estado = _calcular_estado(examen.fecha_vencimiento)

    db.commit()
    db.refresh(examen)
    return _sanitizar_respuesta_medica(_examen_to_response(examen), usuario, db)


@router.patch("/{examen_id}/estado", response_model=ExamenMedicoResponse)
def cambiar_estado_examen_medico(
    examen_id: int,
    activo: bool,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    tenant_id = _empresa_id_autorizada(usuario, None)
    examen = db.query(ExamenMedico).filter(ExamenMedico.id == examen_id, ExamenMedico.empleado.has(Empleado.empresa_id == tenant_id)).first()
    if not examen:
        raise HTTPException(status_code=404, detail="Examen médico no encontrado")
    examen.activo = activo
    examen.fecha_actualizacion = datetime.now()
    db.commit()
    db.refresh(examen)
    return _sanitizar_respuesta_medica(_examen_to_response(examen), usuario, db)


@router.delete("/{examen_id}")
def eliminar_examen_medico(
    examen_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(ELIMINAR_REGISTROS),
):
    tenant_id = _empresa_id_autorizada(usuario, None)
    examen = db.query(ExamenMedico).filter(ExamenMedico.id == examen_id, ExamenMedico.empleado.has(Empleado.empresa_id == tenant_id)).first()
    if not examen:
        raise HTTPException(status_code=404, detail="Examen médico no encontrado")

    db.delete(examen)
    db.commit()
    return {"ok": True, "mensaje": "Examen médico eliminado correctamente"}


# ============================================================
# GENERAR EXÁMENES REQUERIDOS DESDE PROFESIOGRAMA
# ============================================================
@router.post("/empleado/{empleado_id}/generar-desde-profesiograma", response_model=list[ExamenMedicoResponse])
def generar_examenes_desde_profesiograma(
    empleado_id: int,
    data: dict = Body(default={}),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_SST)),
):
    """
    Genera exámenes médicos requeridos para un empleado basándose en el profesiograma de su cargo.
    Usa los tipos de evaluación y exámenes configurados en el profesiograma del cargo del empleado.
    """
    tenant_id = _empresa_id_autorizada(usuario, None)
    from app.models.empleado import Empleado
    from app.models.profesiograma import Profesiograma, ProfesiogramaEvaluacion
    from app.models.examen_medico import ExamenMedico

    empleado = db.query(Empleado).filter(Empleado.id == empleado_id, Empleado.empresa_id == tenant_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    if not empleado.cargo_id:
        raise HTTPException(status_code=400, detail="El empleado no tiene cargo asignado")

    # Buscar profesiograma del cargo
    prof = db.query(Profesiograma).filter(
        Profesiograma.cargo_id == empleado.cargo_id,
        Profesiograma.empresa_id == tenant_id,
        Profesiograma.activo.is_(True)
    ).first()
    if not prof:
        raise HTTPException(status_code=404, detail="No hay profesiograma configurado para este cargo")

    # Obtener evaluaciones del profesiograma
    evaluaciones = db.query(ProfesiogramaEvaluacion).filter(
        ProfesiogramaEvaluacion.profesiograma_id == prof.id,
        ProfesiogramaEvaluacion.activo.is_(True)
    ).all()

    if not evaluaciones:
        raise HTTPException(status_code=400, detail="El profesiograma no tiene evaluaciones configuradas")

    examenes_creados = []
    for ev in evaluaciones:
        import json
        try:
            examenes_requeridos_ids = json.loads(ev.examenes_requeridos or "[]")
        except:
            examenes_requeridos_ids = []

        if not examenes_requeridos_ids:
            continue

        # Obtener información del tipo de evaluación
        from app.models.profesiograma import TipoEvaluacionMedica
        tipo_eval = db.query(TipoEvaluacionMedica).filter(
            TipoEvaluacionMedica.id == ev.tipo_evaluacion_id
        ).first()

        for ex_id in examenes_requeridos_ids:
            from app.models.profesiograma import ExamenEvaluacionCatalogo
            examen_catalogo = db.query(ExamenEvaluacionCatalogo).filter(
                ExamenEvaluacionCatalogo.id == ex_id
            ).first()

            # Verificar si ya existe un examen similar reciente
            from datetime import date, timedelta
            fecha_hoy = date.today()
            existe_reciente = db.query(ExamenMedico).filter(
                ExamenMedico.empleado_id == empleado_id,
                ExamenMedico.tipo_examen == (tipo_eval.codigo if tipo_eval else "INGRESO"),
                ExamenMedico.activo.is_(True),
                ExamenMedico.fecha_examen >= fecha_hoy - timedelta(days=30)
            ).first()

            if existe_reciente:
                continue

            examenes_aplicados_lista = []
            if examen_catalogo:
                examenes_aplicados_lista.append({
                    "id": examen_catalogo.id,
                    "codigo": examen_catalogo.codigo,
                    "nombre": examen_catalogo.nombre,
                })

            nuevo_examen = ExamenMedico(
                empleado_id=empleado_id,
                tipo_examen=tipo_eval.codigo if tipo_eval else "INGRESO",
                fecha_examen=fecha_hoy,
                fecha_vencimiento=fecha_hoy + timedelta(days=365),
                concepto="APTO",
                estado="VIGENTE",
                medico_ocupacional=data.get("medico_ocupacional"),
                entidad_salud=data.get("entidad_salud"),
                observaciones=f"Generado automáticamente desde profesiograma. Evaluación: {tipo_eval.nombre if tipo_eval else 'N/A'}. Examen: {examen_catalogo.nombre if examen_catalogo else 'N/A'}",
                examenes_aplicados=json.dumps(examenes_aplicados_lista, ensure_ascii=False) if examenes_aplicados_lista else None,
                activo=True,
            )
            db.add(nuevo_examen)
            db.flush()
            examenes_creados.append(nuevo_examen)

    db.commit()

    for ex in examenes_creados:
        db.refresh(ex)

    return [_examen_to_response(e) for e in examenes_creados]

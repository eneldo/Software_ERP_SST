# ============================================================
# ROUTER MATRIZ IPER - GTC 45
# Identificación de Peligros, Evaluación y Valoración de Riesgos
# ============================================================

from collections import Counter

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func

from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles

from app.models.empresa import Empresa
from app.models.matriz_iper import MatrizIPER

from app.schemas.matriz_iper_schema import (
    MatrizIPERCreate,
    MatrizIPERUpdate,
    MatrizIPERResponse,
    MatrizIPERDashboardResponse,
)


router = APIRouter(
    prefix="/planear/matriz-iper",
    tags=["PLANEAR - Matriz IPER GTC45"],
)

ROLES_LECTURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"]
ROLES_ESCRITURA = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"]


def _calcular_np_ne(nd: int, ne: int) -> int:
    return nd * ne


def _calcular_nr(np_val: int, nc: int) -> int:
    return np_val * nc


def _interpretar_np(np_val: int) -> str:
    if np_val >= 24:
        return "Muy Alto"
    if np_val >= 10:
        return "Alto"
    if np_val >= 6:
        return "Medio"
    return "Bajo"


def _interpretar_nr(nr: int) -> str:
    if nr >= 600:
        return "No Aceptable"
    if nr >= 150:
        return "No Aceptable / Control Específico"
    if nr >= 40:
        return "Aceptable Mejorable"
    return "Aceptable"


def _aceptabilidad(nr: int) -> str:
    if nr >= 600:
        return "NO ACEPTABLE"
    if nr >= 150:
        return "CON CONTROL ESPECÍFICO"
    if nr >= 40:
        return "MEJORABLE"
    return "ACEPTABLE"


def _nivel_riesgo_romano(nr: int) -> str:
    if nr >= 600:
        return "I"
    if nr >= 150:
        return "II"
    if nr >= 40:
        return "III"
    return "IV"


def _calcular_campos_riesgo(data: dict) -> dict:
    nd = data.get("nd", 0)
    ne = data.get("ne", 1)
    nc = data.get("nc", 10)

    np_val = _calcular_np_ne(nd, ne)
    nr_val = _calcular_nr(np_val, nc)

    data["np"] = np_val
    data["nr"] = nr_val
    data["interpretacion_np"] = _interpretar_np(np_val)
    data["interpretacion_nr"] = _interpretar_nr(nr_val)
    data["nivel_riesgo"] = _nivel_riesgo_romano(nr_val)
    data["aceptabilidad"] = _aceptabilidad(nr_val)

    return data


def serializar(item: MatrizIPER) -> dict:
    return {
        "id": item.id,
        "empresa_id": item.empresa_id,
        "usuario_id": item.usuario_id,
        "proceso": item.proceso,
        "zona_lugar": item.zona_lugar,
        "actividades": item.actividades,
        "tareas": item.tareas,
        "rutinaria": item.rutinaria,
        "clasificacion_peligro": item.clasificacion_peligro,
        "descripcion_peligro": item.descripcion_peligro,
        "riesgo": item.riesgo,
        "efectos_posibles": item.efectos_posibles,
        "fuente": item.fuente,
        "medio": item.medio,
        "individuo": item.individuo,
        "nd": item.nd,
        "ne": item.ne,
        "np": item.np,
        "interpretacion_np": item.interpretacion_np,
        "nc": item.nc,
        "nr": item.nr,
        "interpretacion_nr": item.interpretacion_nr,
        "nivel_riesgo": item.nivel_riesgo,
        "aceptabilidad": item.aceptabilidad,
        "expuestos_hombres": item.expuestos_hombres,
        "expuestos_mujeres": item.expuestos_mujeres,
        "expuestos_gestantes": item.expuestos_gestantes,
        "peor_consecuencia": item.peor_consecuencia,
        "eliminacion": item.eliminacion,
        "control_ingenieria": item.control_ingenieria,
        "sustitucion": item.sustitucion,
        "senalizacion_admin": item.senalizacion_admin,
        "epp": item.epp,
        "responsable": item.responsable,
        "fecha_proyectada": item.fecha_proyectada,
        "fecha_ejecucion": item.fecha_ejecucion,
        "evidencias": item.evidencias,
        "realizado": item.realizado,
        "activo": item.activo,
        "fecha_creacion": item.fecha_creacion,
        "fecha_actualizacion": item.fecha_actualizacion,
    }


# ── CRUD ──────────────────────────────────────────────────

@router.post("/", response_model=MatrizIPERResponse)
def crear_fila_iper(
    data: MatrizIPERCreate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    payload = data.model_dump()
    payload = _calcular_campos_riesgo(payload)

    item = MatrizIPER(**payload, usuario_id=usuario.id)
    db.add(item)
    db.commit()
    db.refresh(item)

    return serializar(item)


@router.post("/lote")
def crear_lote_iper(
    filas: list[MatrizIPERCreate],
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    """Crea múltiples filas de la matriz IPER en una sola petición."""
    if not filas:
        raise HTTPException(status_code=400, detail="No se enviaron filas")

    empresa_id = filas[0].empresa_id
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    creados = []
    for fila in filas:
        payload = fila.model_dump()
        payload = _calcular_campos_riesgo(payload)
        item = MatrizIPER(**payload, usuario_id=usuario.id)
        db.add(item)
        db.flush()
        creados.append(serializar(item))

    db.commit()

    return {"mensaje": f"{len(creados)} filas creadas correctamente", "items": creados}


@router.get("/", response_model=list[MatrizIPERResponse])
def listar_iper(
    empresa_id: int | None = None,
    clasificacion_peligro: str | None = None,
    aceptabilidad: str | None = None,
    buscar: str | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    query = db.query(MatrizIPER).filter(MatrizIPER.activo == True)

    if empresa_id:
        query = query.filter(MatrizIPER.empresa_id == empresa_id)

    if clasificacion_peligro:
        query = query.filter(MatrizIPER.clasificacion_peligro == clasificacion_peligro)

    if aceptabilidad:
        query = query.filter(MatrizIPER.aceptabilidad == aceptabilidad)

    if buscar:
        patron = f"%{buscar}%"
        query = query.filter(
            MatrizIPER.proceso.ilike(patron)
            | MatrizIPER.descripcion_peligro.ilike(patron)
            | MatrizIPER.efectos_posibles.ilike(patron)
        )

    items = query.order_by(MatrizIPER.id.desc()).all()
    return [serializar(item) for item in items]


@router.get("/dashboard/{empresa_id}", response_model=MatrizIPERDashboardResponse)
def dashboard_iper(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    items = (
        db.query(MatrizIPER)
        .filter(MatrizIPER.empresa_id == empresa_id, MatrizIPER.activo == True)
        .all()
    )

    total = len(items)

    clasif_counter = Counter([i.clasificacion_peligro for i in items])
    acept_counter = Counter([i.aceptabilidad or "SIN_VALORAR" for i in items])
    nr_counter = Counter([i.interpretacion_nr or "SIN_VALORAR" for i in items])

    expuestos_total = sum(
        (i.expuestos_hombres or 0) + (i.expuestos_mujeres or 0) + (i.expuestos_gestantes or 0)
        for i in items
    )

    return {
        "total": total,
        "por_clasificacion": [{"nombre": k, "total": v} for k, v in clasif_counter.most_common()],
        "por_aceptabilidad": [{"nombre": k, "total": v} for k, v in acept_counter.most_common()],
        "por_nr": [{"nombre": k, "total": v} for k, v in nr_counter.most_common()],
        "expuestos_total": expuestos_total,
    }


# ── RECALCULAR VALORES ─────────────────────────────────────

@router.put("/recalcular/{empresa_id}")
def recalcular_valores_iper(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    """Recalcula np, nr, interpretacion_np, interpretacion_nr, nivel_riesgo y aceptabilidad
    para todas las filas IPER de una empresa usando nd, ne, nc almacenados."""
    items = (
        db.query(MatrizIPER)
        .filter(MatrizIPER.empresa_id == empresa_id, MatrizIPER.activo == True)
        .all()
    )

    if not items:
        raise HTTPException(status_code=404, detail="No hay registros IPER para recalcular")

    recalculados = 0
    for item in items:
        payload = {
            "nd": item.nd,
            "ne": item.ne,
            "nc": item.nc,
        }
        payload = _calcular_campos_riesgo(payload)

        item.np = payload["np"]
        item.nr = payload["nr"]
        item.interpretacion_np = payload["interpretacion_np"]
        item.interpretacion_nr = payload["interpretacion_nr"]
        item.nivel_riesgo = payload["nivel_riesgo"]
        item.aceptabilidad = payload["aceptabilidad"]
        recalculados += 1

    db.commit()

    return {
        "mensaje": f"{recalculados} registros recalculados correctamente",
        "recalculados": recalculados,
    }


# ── CRUD ──────────────────────────────────────────────────

@router.get("/{item_id}", response_model=MatrizIPERResponse)
def obtener_fila_iper(
    item_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    item = db.query(MatrizIPER).filter(MatrizIPER.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Fila IPER no encontrada")
    return serializar(item)


@router.put("/{item_id}", response_model=MatrizIPERResponse)
def actualizar_fila_iper(
    item_id: int,
    data: MatrizIPERUpdate,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    item = db.query(MatrizIPER).filter(MatrizIPER.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Fila IPER no encontrada")

    payload = data.model_dump(exclude_unset=True)
    payload = _calcular_campos_riesgo(payload)

    for key, value in payload.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)

    return serializar(item)


@router.delete("/{item_id}")
def eliminar_fila_iper(
    item_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA"])),
):
    item = db.query(MatrizIPER).filter(MatrizIPER.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Fila IPER no encontrada")

    item.activo = False
    db.commit()

    return {"mensaje": "Fila IPER eliminada correctamente"}


# ── ACTUALIZACIÓN MASIVA ──────────────────────────────────

class ItemLoteUpdate(BaseModel):
    id: int
    data: dict


@router.put("/lote")
def actualizar_lote_iper(
    filas: list[ItemLoteUpdate],
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_ESCRITURA)),
):
    """Actualiza múltiples filas de la matriz IPER en una sola petición."""
    if not filas:
        raise HTTPException(status_code=400, detail="No se enviaron filas")

    actualizados = []
    for item_data in filas:
        item = db.query(MatrizIPER).filter(MatrizIPER.id == item_data.id).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Fila IPER {item_data.id} no encontrada")

        payload = item_data.data
        payload = _calcular_campos_riesgo(payload)

        for key, value in payload.items():
            if key != "id":
                setattr(item, key, value)

        db.flush()
        actualizados.append(serializar(item))

    db.commit()

    return {"mensaje": f"{len(actualizados)} filas actualizadas correctamente", "items": actualizados}


# ── EXPORTAR EXCEL ────────────────────────────────────────

@router.get("/exportar/excel/{empresa_id}")
def exportar_excel_iper(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    """Exporta la matriz IPER completa a Excel con estructura GTC 45."""
    from io import BytesIO
    from datetime import datetime
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from fastapi.responses import StreamingResponse

    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    items = (
        db.query(MatrizIPER)
        .filter(MatrizIPER.empresa_id == empresa_id, MatrizIPER.activo == True)
        .order_by(MatrizIPER.id)
        .all()
    )

    if not items:
        raise HTTPException(status_code=404, detail="No hay registros IPER para exportar")

    # ── Estilos base ──
    verde = PatternFill("solid", fgColor="A8D08D")
    font_header = Font(name="Times New Roman", bold=True, size=10)
    font_data = Font(name="Times New Roman", size=10)
    border_medium = Side(border_style="medium", color="000000")
    border_thin = Side(border_style="thin", color="000000")
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="top", wrap_text=True)

    # ── Definición de columnas (ADMINISTRATIVA = 31 cols, OPERATIVO = 36 cols) ──
    # Cada tupla: (header_row9, width)
    columnas_base = [
        ("PROCESO", 9.0),           # A
        ("ZONA/LUGAR", 8.4),        # B
        ("ACTIVIDADES", 8.9),       # C
        ("TAREAS", 8.4),            # D
        ("RUTINARIA", 7.9),         # E
        ("CLASIFICACION", 15.6),    # F
        ("DESCRIPCION", 30.6),      # G
        ("RIESGO", 17.6),           # H
        ("EFECTOS POSIBLES", 14.1), # I
        ("FUENTE", 12.4),           # J
        ("MEDIO", 12.9),            # K
        ("INDIVIDUO", 12.0),        # L
        ("NIVEL DE DEFICIENCIA", 14.1),   # M
        ("NIVEL DE EXPOSICION", 10.4),    # N
        ("NIVEL DE PROBABILIDAD", 12.6),  # O
        ("INTERPRETACION DEL NIVEL DE PROBABILIDAD", 12.9),  # P
        ("NIVEL DE CONSECUENCIA", 7.0),   # Q
        ("NIVEL DEL RIESGO", 11.1),       # R
        ("INTERPRETACION DEL NIVEL DEL RIESGO", 17.4),  # S
        ("ACEPTABILIDAD DEL RIESGO", 10.6),  # T
        ("Nro. EXPUESTOS HOMBRES", 15.1),    # U
        ("Nro. EXPUESTOS MUJERES", 15.1),    # V
        ("Nro. EXPUESTOS GESTANTES", 15.1),  # W
        ("PEOR CONSECUENCIA", 22.0),         # X
        ("ELIMINACION", 18.4),               # Y
        ("CONTROL INGENIERIA", 21.9),        # Z
        ("SUSTITUCION", 20.0),               # AA
        ("SEÑALIZACION / CONTROLES ADMIN", 37.0),  # AB
        ("EPP", 21.4),                        # AC
    ]

    columnas_seguimiento = [
        ("RESPONSABLE", 11.4),       # AD
        ("FECHA PROYECTADA", 23.0),  # AE
        ("FECHA EJECUCION", 23.0),   # AF
        ("EVIDENCIAS", 30.0),        # AG
        ("REALIZADO", 12.0),         # AH
    ]

    # Encabezados de grupo (row 8) - tuplas: (texto, start_col, end_col)
    grupos_base = [
        ("PROCESO", 1, 1),
        ("ZONA/LUGAR", 2, 2),
        ("ACTIVIDADES", 3, 3),
        ("TAREAS", 4, 4),
        ("RUTINARIA", 5, 5),
        ("PELIGRO", 6, 7),
        ("RIESGO", 8, 8),
        ("EFECTOS POSIBLES", 9, 9),
        ("CONTROLES EXISTENTES", 10, 12),
        ("EVALUACION DE RIESGOS", 13, 20),
        ("CRITERIOS PARA ESTABLECER CONTROLES", 21, 24),
        ("MEDIDAS DE INTERVENCION", 25, 29),
    ]

    grupos_seguimiento = [
        ("SEGUIMIENTO", 30, 34),
        ("INDICADOR", 35, 36),
    ]

    def _crear_hoja(wb, nombre, columnas, grupos, font_size, items_lista):
        ws = wb.create_sheet(title=nombre)

        total_cols = len(columnas)
        font_h = Font(name="Times New Roman", bold=True, size=font_size)
        font_d = Font(name="Times New Roman", size=font_size)

        # ── Metadatos (rows 1-6) ──
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=min(5, total_cols))
        ws["A1"] = "Matriz Peligros 10 Actualizada"
        ws["A1"].font = Font(name="Times New Roman", bold=True, size=14)
        ws["A1"].alignment = Alignment(horizontal="left")

        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=min(15, total_cols))
        ws["A2"] = "MATRIZ DE IDENTIFICACION DE PELIGROS, VALORACION DE RIESGOS Y DETERMINACION DE CONTROLES"
        ws["A2"].font = Font(name="Times New Roman", bold=True, size=12)
        ws["A2"].alignment = Alignment(horizontal="left")

        ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=min(5, total_cols))
        ws["A3"] = f"Código: SGSST-IPER-GTC45"
        ws["A3"].font = Font(name="Times New Roman", size=10)

        ws.merge_cells(start_row=4, start_column=1, end_row=4, end_column=min(5, total_cols))
        ws["A4"] = f"Fecha: {datetime.now().strftime('%Y-%m-%d')}"
        ws["A4"].font = Font(name="Times New Roman", size=10)

        ws.merge_cells(start_row=6, start_column=1, end_row=6, end_column=min(10, total_cols))
        ws["A6"] = f"Empresa: {empresa.nombre} | NIT: {empresa.nit or 'N/A'} | Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        ws["A6"].font = Font(name="Times New Roman", size=10)

        # ── Row 8: Encabezados de grupo ──
        # Track which columns in row 9 are covered by vertical merges
        merged_row9_cols = set()
        for texto, start, end in grupos:
            if start == end:
                # Single column: merge vertically row 8-9
                ws.merge_cells(start_row=8, start_column=start, end_row=9, end_column=end)
                cell = ws.cell(row=8, column=start, value=texto)
                merged_row9_cols.add(start)
            else:
                # Multi column: merge horizontally in row 8
                ws.merge_cells(start_row=8, start_column=start, end_row=8, end_column=end)
                cell = ws.cell(row=8, column=start, value=texto)
            cell.fill = verde
            cell.font = font_h
            cell.alignment = align_center
            cell.border = Border(top=border_medium, bottom=border_thin, left=border_thin, right=border_thin)

        # ── Row 9: Sub-encabezados ──
        for col_idx, (header, width) in enumerate(columnas, start=1):
            if col_idx in merged_row9_cols:
                # This column is vertically merged from row 8, skip writing value
                # but still apply formatting
                cell = ws.cell(row=9, column=col_idx)
                cell.fill = verde
                cell.font = font_h
                cell.alignment = align_center
                cell.border = Border(top=border_thin, bottom=border_thin, left=border_thin, right=border_thin)
            else:
                cell = ws.cell(row=9, column=col_idx, value=header)
                cell.fill = verde
                cell.font = font_h
                cell.alignment = align_center
                cell.border = Border(top=border_thin, bottom=border_thin, left=border_thin, right=border_thin)
            ws.column_dimensions[get_column_letter(col_idx)].width = width

        # ── Datos (rows 10+) ──
        for row_idx, item in enumerate(items_lista, start=10):
            fila = [
                item.proceso,
                item.zona_lugar or "",
                item.actividades or "",
                item.tareas or "",
                item.rutinaria or "SI",
                CLASIFICACION_LABELS.get(item.clasificacion_peligro, item.clasificacion_peligro),
                item.descripcion_peligro,
                item.riesgo or "",
                item.efectos_posibles or "",
                item.fuente or "",
                item.medio or "",
                item.individuo or "",
                item.nd or 0,
                item.ne or 1,
                item.np or 0,
                item.interpretacion_np or "",
                item.nc or 10,
                item.nr or 0,
                item.interpretacion_nr or "",
                item.nivel_riesgo or "",
                item.aceptabilidad or "",
                item.expuestos_hombres or 0,
                item.expuestos_mujeres or 0,
                item.expuestos_gestantes or 0,
                item.peor_consecuencia or "",
                item.eliminacion or "",
                item.control_ingenieria or "",
                item.sustitucion or "",
                item.senalizacion_admin or "",
                item.epp or "",
            ]

            # Columnas de seguimiento (solo OPERATIVO)
            if len(columnas) > 29:
                fila.extend([
                    item.responsable or "",
                    item.fecha_proyectada.strftime("%Y-%m-%d") if item.fecha_proyectada else "",
                    item.fecha_ejecucion.strftime("%Y-%m-%d") if item.fecha_ejecucion else "",
                    item.evidencias or "",
                    item.realizado or "NO",
                ])

            for col_idx, valor in enumerate(fila, start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=valor)
                cell.font = font_d
                cell.alignment = align_left
                cell.border = Border(top=border_thin, bottom=border_thin, left=border_thin, right=border_thin)

        return ws

    # ── Crear libro ──
    wb = Workbook()
    wb.remove(wb.active)  # Eliminar hoja por defecto

    # Hoja ADMINISTRATIVA (solo registros clasificación administrativa o todos)
    admin_items = [i for i in items if i.clasificacion_peligro in ("CONDICIONES_SEGURIDAD", "PSICOSOCIAL", "FENOMENOS_NATURALES")]
    if not admin_items:
        admin_items = items  # Si no hay clasificados, exportar todos

    _crear_hoja(wb, "ADMINISTRATIVA", columnas_base, grupos_base, 10, admin_items)

    # Hoja OPERATIVA (todos los registros o los operativos)
    oper_items = [i for i in items if i.clasificacion_peligro in ("FISICO", "QUIMICO", "BIOLOGICO", "BIOMECANICO")]
    if not oper_items:
        oper_items = items

    columnas_operativo = columnas_base + columnas_seguimiento
    grupos_operativo = grupos_base + grupos_seguimiento
    _crear_hoja(wb, "OPERATIVO", columnas_operativo, grupos_operativo, 12, oper_items)

    # ── Guardar ──
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    nombre_archivo = f"Matriz_IPER_{empresa.nombre.replace(' ', '_')}.xlsx"

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={nombre_archivo}"},
    )


# ── EXPORTAR PDF ──────────────────────────────────────────

@router.get("/exportar/pdf/{empresa_id}")
def exportar_pdf_iper(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_LECTURA)),
):
    """Exporta la matriz IPER completa a PDF."""
    from fastapi.responses import StreamingResponse
    from app.services.export_pdf_service import generar_pdf_corporativo

    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    items = (
        db.query(MatrizIPER)
        .filter(MatrizIPER.empresa_id == empresa_id, MatrizIPER.activo == True)
        .order_by(MatrizIPER.id)
        .all()
    )

    if not items:
        raise HTTPException(status_code=404, detail="No hay registros IPER para exportar")

    columnas = [
        "N°", "Proceso", "Peligro", "Descripción", "ND", "NE", "NP", "NC", "NR",
        "Aceptabilidad", "Responsable", "Realizado",
    ]

    filas = []
    for idx, item in enumerate(items, start=1):
        filas.append([
            idx, item.proceso, CLASIFICACION_LABELS.get(item.clasificacion_peligro, item.clasificacion_peligro),
            item.descripcion_peligro, item.nd, item.ne, item.np, item.nc, item.nr,
            item.aceptabilidad or "", item.responsable or "", item.realizado or "NO",
        ])

    pdf_bytes = generar_pdf_corporativo(
        titulo="Matriz IPER - GTC 45",
        codigo="IPER",
        empresa=empresa,
        configuracion=None,
        columnas=columnas,
        filas=filas,
        orientacion="horizontal",
    )

    nombre_archivo = f"Matriz_IPER_{empresa.nombre.replace(' ', '_')}.pdf"

    return StreamingResponse(
        iter([pdf_bytes.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={nombre_archivo}"},
    )


CLASIFICACION_LABELS = {
    "FISICO": "Físico",
    "QUIMICO": "Químico",
    "BIOLOGICO": "Biológico",
    "BIOMECANICO": "Biomecánico",
    "PSICOSOCIAL": "Psicosocial",
    "CONDICIONES_SEGURIDAD": "Condiciones de Seguridad",
    "FENOMENOS_NATURALES": "Fenómenos Naturales",
}

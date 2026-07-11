# ============================================================
# ROUTER EXPORTACIONES SST
# ERP SST PRO
# FASE 2.5.2 - Exportación Real Matriz de Peligros
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.auth.dependencies import require_permission
from app.core.default_permissions import PERM_REPORTES_EXPORTAR

from app.models.empresa import Empresa
from app.models.configuracion_documental import ConfiguracionDocumental
from app.models.objetivo_sst import ObjetivoSST
from app.models.politica_sst import PoliticaSST
from app.models.evaluacion_inicial import EvaluacionInicialSST
from app.models.matriz_legal import MatrizLegalSST
from app.models.matriz_peligros import MatrizPeligrosSST
from app.models.plan_anual import PlanAnualSST
from app.models.capacitacion import CapacitacionSST, CapacitacionAsistenteSST

from app.services.export_pdf_service import generar_pdf_corporativo
from app.services.export_excel_service import generar_excel_corporativo


router = APIRouter(
    prefix="/exportaciones-sst",
    tags=["Exportaciones Corporativas SST"],
)

ROLES_EXPORTACION = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"]
EXPORTAR_REPORTES = require_permission(PERM_REPORTES_EXPORTAR)


def obtener_empresa_y_configuracion(db: Session, empresa_id: int):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    configuracion = (
        db.query(ConfiguracionDocumental)
        .filter(ConfiguracionDocumental.empresa_id == empresa_id)
        .first()
    )

    return empresa, configuracion


# ============================================================
# OBJETIVOS SST
# ============================================================

@router.get("/objetivos/pdf/{empresa_id}")
def exportar_objetivos_pdf(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(EXPORTAR_REPORTES),
):
    empresa, configuracion = obtener_empresa_y_configuracion(db, empresa_id)

    objetivos = (
        db.query(ObjetivoSST)
        .filter(ObjetivoSST.empresa_id == empresa_id)
        .order_by(ObjetivoSST.id.asc())
        .all()
    )

    columnas = ["Objetivo", "Meta", "Indicador", "Responsable", "Estado", "Cumplimiento"]

    filas = [
        [
            o.objetivo,
            o.meta,
            o.indicador,
            o.responsable or "",
            o.estado,
            f"{o.cumplimiento}%",
        ]
        for o in objetivos
    ]

    pdf = generar_pdf_corporativo(
        titulo="Objetivos SST",
        codigo="OBJ-001",
        empresa=empresa,
        configuracion=configuracion,
        columnas=columnas,
        filas=filas,
        orientacion="horizontal",
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=objetivos_sst.pdf"},
    )


@router.get("/objetivos/excel/{empresa_id}")
def exportar_objetivos_excel(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(EXPORTAR_REPORTES),
):
    empresa, configuracion = obtener_empresa_y_configuracion(db, empresa_id)

    objetivos = (
        db.query(ObjetivoSST)
        .filter(ObjetivoSST.empresa_id == empresa_id)
        .order_by(ObjetivoSST.id.asc())
        .all()
    )

    columnas = [
        "ID", "Objetivo", "Meta", "Indicador", "Responsable",
        "Fecha inicio", "Fecha fin", "Estado", "Cumplimiento", "Observaciones",
    ]

    filas = [
        [
            o.id,
            o.objetivo,
            o.meta,
            o.indicador,
            o.responsable or "",
            str(o.fecha_inicio or ""),
            str(o.fecha_fin or ""),
            o.estado,
            f"{o.cumplimiento}%",
            o.observaciones or "",
        ]
        for o in objetivos
    ]

    excel = generar_excel_corporativo(
        titulo="Objetivos SST",
        codigo="OBJ-001",
        empresa=empresa,
        configuracion=configuracion,
        columnas=columnas,
        filas=filas,
    )

    return StreamingResponse(
        excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=objetivos_sst.xlsx"},
    )


# ============================================================
# POLÍTICA SST
# ============================================================

@router.get("/politica/pdf/{politica_id}")
def exportar_politica_pdf(
    politica_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(EXPORTAR_REPORTES),
):
    politica = db.query(PoliticaSST).filter(PoliticaSST.id == politica_id).first()

    if not politica:
        raise HTTPException(status_code=404, detail="Política SST no encontrada")

    empresa, configuracion = obtener_empresa_y_configuracion(db, politica.empresa_id)

    columnas = ["Campo", "Información"]

    filas = [
        ["Título", politica.titulo],
        ["Versión", politica.version],
        ["Estado", politica.estado],
        ["Fecha aprobación", str(politica.fecha_aprobacion or "")],
        ["Fecha vigencia", str(politica.fecha_vigencia or "")],
        ["Responsable SST", politica.responsable_sst or ""],
        ["Representante Legal", politica.representante_legal or ""],
        ["Contenido", politica.contenido],
        ["Observaciones", politica.observaciones or ""],
    ]

    pdf = generar_pdf_corporativo(
        titulo="Política SST",
        codigo="POL-001",
        empresa=empresa,
        configuracion=configuracion,
        columnas=columnas,
        filas=filas,
        orientacion="vertical",
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=politica_sst.pdf"},
    )


# ============================================================
# EVALUACIÓN INICIAL SST
# ============================================================

@router.get("/evaluacion-inicial/pdf/{evaluacion_id}")
def exportar_evaluacion_inicial_pdf(
    evaluacion_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(EXPORTAR_REPORTES),
):
    evaluacion = (
        db.query(EvaluacionInicialSST)
        .options(joinedload(EvaluacionInicialSST.items))
        .filter(EvaluacionInicialSST.id == evaluacion_id)
        .first()
    )

    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación inicial no encontrada")

    empresa, configuracion = obtener_empresa_y_configuracion(db, evaluacion.empresa_id)

    columnas = ["Campo", "Información"]

    filas = [
        ["Código", evaluacion.codigo],
        ["Nombre", evaluacion.nombre],
        ["Fecha evaluación", str(evaluacion.fecha_evaluacion or "")],
        ["Responsable", evaluacion.responsable or ""],
        ["Estado", evaluacion.estado],
        ["Total criterios", evaluacion.total_items],
        ["Cumplen", evaluacion.items_cumplen],
        ["No cumplen", evaluacion.items_no_cumplen],
        ["No aplican", evaluacion.items_no_aplican],
        ["Cumplimiento", f"{evaluacion.porcentaje_cumplimiento}%"],
        ["Nivel", evaluacion.nivel],
        ["Observaciones generales", evaluacion.observaciones_generales or ""],
    ]

    pdf = generar_pdf_corporativo(
        titulo="Evaluación Inicial SG-SST",
        codigo="EVAL-001",
        empresa=empresa,
        configuracion=configuracion,
        columnas=columnas,
        filas=filas,
        orientacion="vertical",
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=evaluacion_inicial_{evaluacion.id}.pdf"
        },
    )


@router.get("/evaluacion-inicial/excel/{evaluacion_id}")
def exportar_evaluacion_inicial_excel(
    evaluacion_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(EXPORTAR_REPORTES),
):
    evaluacion = (
        db.query(EvaluacionInicialSST)
        .options(joinedload(EvaluacionInicialSST.items))
        .filter(EvaluacionInicialSST.id == evaluacion_id)
        .first()
    )

    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación inicial no encontrada")

    empresa, configuracion = obtener_empresa_y_configuracion(db, evaluacion.empresa_id)

    columnas = [
        "ID", "Numeral", "Estándar", "Criterio", "Respuesta",
        "Puntaje", "Evidencia", "Observaciones", "Responsable",
    ]

    filas = [
        [
            item.id,
            item.numeral or "",
            item.estandar,
            item.criterio,
            item.respuesta,
            item.puntaje,
            item.evidencia or "",
            item.observaciones or "",
            item.responsable or "",
        ]
        for item in evaluacion.items
        if item.activo
    ]

    excel = generar_excel_corporativo(
        titulo=f"Evaluación Inicial SG-SST - {evaluacion.codigo}",
        codigo="EVAL-001",
        empresa=empresa,
        configuracion=configuracion,
        columnas=columnas,
        filas=filas,
    )

    return StreamingResponse(
        excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=evaluacion_inicial_{evaluacion.id}.xlsx"
        },
    )


# ============================================================
# MATRIZ LEGAL SST
# ============================================================

@router.get("/matriz-legal/pdf/{empresa_id}")
def exportar_matriz_legal_pdf(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(EXPORTAR_REPORTES),
):
    empresa, configuracion = obtener_empresa_y_configuracion(db, empresa_id)

    items = (
        db.query(MatrizLegalSST)
        .filter(MatrizLegalSST.empresa_id == empresa_id, MatrizLegalSST.activo == True)
        .order_by(MatrizLegalSST.id.asc())
        .all()
    )

    columnas = ["Código", "Norma", "Artículo", "Requisito", "Tema", "Cumplimiento"]

    filas = [
        [
            i.codigo,
            i.norma,
            i.articulo or "",
            i.requisito_legal,
            i.tema or "",
            i.estado_cumplimiento,
        ]
        for i in items
    ]

    pdf = generar_pdf_corporativo(
        titulo="Matriz Legal SST",
        codigo="ML-001",
        empresa=empresa,
        configuracion=configuracion,
        columnas=columnas,
        filas=filas,
        orientacion="horizontal",
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=matriz_legal_sst.pdf"},
    )


@router.get("/matriz-legal/excel/{empresa_id}")
def exportar_matriz_legal_excel(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(EXPORTAR_REPORTES),
):
    empresa, configuracion = obtener_empresa_y_configuracion(db, empresa_id)

    items = (
        db.query(MatrizLegalSST)
        .filter(MatrizLegalSST.empresa_id == empresa_id, MatrizLegalSST.activo == True)
        .order_by(MatrizLegalSST.id.asc())
        .all()
    )

    columnas = [
        "ID", "Código", "Norma", "Tipo", "Número", "Año", "Artículo",
        "Requisito legal", "Tema", "Entidad emisora", "Aplicabilidad",
        "Estado cumplimiento", "Estado norma", "Responsable",
        "Fecha revisión", "Fecha vencimiento", "Evidencia", "Observaciones",
    ]

    filas = [
        [
            i.id,
            i.codigo,
            i.norma,
            i.tipo_norma or "",
            i.numero_norma or "",
            i.anio or "",
            i.articulo or "",
            i.requisito_legal,
            i.tema or "",
            i.entidad_emisora or "",
            i.aplicabilidad,
            i.estado_cumplimiento,
            i.estado_norma,
            i.responsable or "",
            str(i.fecha_revision or ""),
            str(i.fecha_vencimiento or ""),
            i.evidencia or "",
            i.observaciones or "",
        ]
        for i in items
    ]

    excel = generar_excel_corporativo(
        titulo="Matriz Legal SST",
        codigo="ML-001",
        empresa=empresa,
        configuracion=configuracion,
        columnas=columnas,
        filas=filas,
    )

    return StreamingResponse(
        excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=matriz_legal_sst.xlsx"},
    )


# ============================================================
# MATRIZ DE PELIGROS SST - REAL
# ============================================================

@router.get("/matriz-peligros/pdf/{empresa_id}")
def exportar_matriz_peligros_pdf(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(EXPORTAR_REPORTES),
):
    empresa, configuracion = obtener_empresa_y_configuracion(db, empresa_id)

    items = (
        db.query(MatrizPeligrosSST)
        .filter(MatrizPeligrosSST.empresa_id == empresa_id, MatrizPeligrosSST.activo == True)
        .order_by(MatrizPeligrosSST.id.asc())
        .all()
    )

    columnas = [
        "Código",
        "Proceso",
        "Actividad",
        "Peligro",
        "Clasificación",
        "NP",
        "NC",
        "Nivel",
        "Riesgo",
        "Aceptabilidad",
        "Medidas",
    ]

    filas = [
        [
            i.codigo,
            i.proceso,
            i.actividad,
            i.peligro,
            i.clasificacion_peligro,
            i.probabilidad,
            i.consecuencia,
            i.nivel_riesgo,
            i.interpretacion_riesgo,
            i.aceptabilidad,
            i.medidas_intervencion or "",
        ]
        for i in items
    ]

    pdf = generar_pdf_corporativo(
        titulo="Matriz de Peligros SST",
        codigo="MP-001",
        empresa=empresa,
        configuracion=configuracion,
        columnas=columnas,
        filas=filas,
        orientacion="horizontal",
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=matriz_peligros_sst.pdf"},
    )


@router.get("/matriz-peligros/excel/{empresa_id}")
def exportar_matriz_peligros_excel(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(EXPORTAR_REPORTES),
):
    empresa, configuracion = obtener_empresa_y_configuracion(db, empresa_id)

    items = (
        db.query(MatrizPeligrosSST)
        .filter(MatrizPeligrosSST.empresa_id == empresa_id, MatrizPeligrosSST.activo == True)
        .order_by(MatrizPeligrosSST.id.asc())
        .all()
    )

    columnas = [
        "ID",
        "Código",
        "Proceso",
        "Actividad",
        "Tarea",
        "Peligro",
        "Clasificación del peligro",
        "Efectos posibles",
        "Controles fuente",
        "Controles medio",
        "Controles individuo",
        "Probabilidad",
        "Consecuencia",
        "Nivel riesgo",
        "Interpretación riesgo",
        "Aceptabilidad",
        "Medidas intervención",
        "Responsable",
        "Fecha revisión",
        "Fecha vencimiento",
        "Estado",
        "Evidencia",
        "Observaciones",
    ]

    filas = [
        [
            i.id,
            i.codigo,
            i.proceso,
            i.actividad,
            i.tarea or "",
            i.peligro,
            i.clasificacion_peligro,
            i.efectos_posibles or "",
            i.controles_fuente or "",
            i.controles_medio or "",
            i.controles_individuo or "",
            i.probabilidad,
            i.consecuencia,
            i.nivel_riesgo,
            i.interpretacion_riesgo,
            i.aceptabilidad,
            i.medidas_intervencion or "",
            i.responsable or "",
            str(i.fecha_revision or ""),
            str(i.fecha_vencimiento or ""),
            i.estado,
            i.evidencia or "",
            i.observaciones or "",
        ]
        for i in items
    ]

    excel = generar_excel_corporativo(
        titulo="Matriz de Peligros SST",
        codigo="MP-001",
        empresa=empresa,
        configuracion=configuracion,
        columnas=columnas,
        filas=filas,
    )

    return StreamingResponse(
        excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=matriz_peligros_sst.xlsx"},
    )


# ============================================================
# PLAN ANUAL SST - PLACEHOLDER
# ============================================================

# ============================================================
# PLAN ANUAL SST - REAL
# FASE 2.6.2
# ============================================================

@router.get("/plan-anual/pdf/{empresa_id}")
def exportar_plan_anual_pdf(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(EXPORTAR_REPORTES),
):
    empresa, configuracion = obtener_empresa_y_configuracion(db, empresa_id)

    items = (
        db.query(PlanAnualSST)
        .filter(
            PlanAnualSST.empresa_id == empresa_id,
            PlanAnualSST.activo == True,
        )
        .order_by(PlanAnualSST.id.asc())
        .all()
    )

    columnas = [
        "Código",
        "Actividad",
        "Objetivo",
        "Responsable",
        "Indicador",
        "Meta",
        "Estado",
        "Avance",
        "Inicio",
        "Fin",
        "Presupuesto",
    ]

    filas = [
        [
            i.codigo,
            i.actividad,
            i.objetivo or "",
            i.responsable or "",
            i.indicador or "",
            i.meta or "",
            i.estado,
            f"{i.porcentaje_avance}%",
            str(i.fecha_inicio or ""),
            str(i.fecha_fin or ""),
            f"${float(i.presupuesto or 0):,.0f}",
        ]
        for i in items
    ]

    pdf = generar_pdf_corporativo(
        titulo="Plan Anual SST",
        codigo="PA-001",
        empresa=empresa,
        configuracion=configuracion,
        columnas=columnas,
        filas=filas,
        orientacion="horizontal",
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=plan_anual_sst.pdf"
        },
    )


@router.get("/plan-anual/excel/{empresa_id}")
def exportar_plan_anual_excel(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(EXPORTAR_REPORTES),
):
    empresa, configuracion = obtener_empresa_y_configuracion(db, empresa_id)

    items = (
        db.query(PlanAnualSST)
        .filter(
            PlanAnualSST.empresa_id == empresa_id,
            PlanAnualSST.activo == True,
        )
        .order_by(PlanAnualSST.id.asc())
        .all()
    )

    columnas = [
        "ID",
        "Código",
        "Actividad",
        "Objetivo",
        "Responsable",
        "Recurso humano",
        "Recurso físico",
        "Recurso financiero",
        "Presupuesto",
        "Indicador",
        "Meta",
        "Fecha inicio",
        "Fecha fin",
        "Estado",
        "Porcentaje avance",
        "Evidencia",
        "Observaciones",
    ]

    filas = [
        [
            i.id,
            i.codigo,
            i.actividad,
            i.objetivo or "",
            i.responsable or "",
            i.recurso_humano or "",
            i.recurso_fisico or "",
            i.recurso_financiero or "",
            float(i.presupuesto or 0),
            i.indicador or "",
            i.meta or "",
            str(i.fecha_inicio or ""),
            str(i.fecha_fin or ""),
            i.estado,
            f"{i.porcentaje_avance}%",
            i.evidencia or "",
            i.observaciones or "",
        ]
        for i in items
    ]

    excel = generar_excel_corporativo(
        titulo="Plan Anual SST",
        codigo="PA-001",
        empresa=empresa,
        configuracion=configuracion,
        columnas=columnas,
        filas=filas,
    )

    return StreamingResponse(
        excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=plan_anual_sst.xlsx"
        },
    )

# ============================================================
# CAPACITACIONES SST - REAL
# FASE 2.7.3
# ============================================================

@router.get("/capacitaciones/pdf/{empresa_id}")
def exportar_capacitaciones_pdf(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(EXPORTAR_REPORTES),
):
    empresa, configuracion = obtener_empresa_y_configuracion(db, empresa_id)

    items = (
        db.query(CapacitacionSST)
        .filter(
            CapacitacionSST.empresa_id == empresa_id,
            CapacitacionSST.activo == True,
        )
        .order_by(CapacitacionSST.id.asc())
        .all()
    )

    columnas = [
        "Código",
        "Nombre",
        "Tema",
        "Tipo",
        "Modalidad",
        "Capacitador",
        "Responsable",
        "Fecha programada",
        "Fecha ejecución",
        "Asistentes",
        "Estado",
        "Cumplimiento",
    ]

    filas = [
        [
            i.codigo,
            i.nombre,
            i.tema,
            i.tipo,
            i.modalidad,
            i.capacitador or "",
            i.responsable or "",
            str(i.fecha_programada or ""),
            str(i.fecha_ejecucion or ""),
            i.total_asistentes or 0,
            i.estado,
            f"{i.cumplimiento}%",
        ]
        for i in items
    ]

    pdf = generar_pdf_corporativo(
        titulo="Capacitaciones SST",
        codigo="CAP-001",
        empresa=empresa,
        configuracion=configuracion,
        columnas=columnas,
        filas=filas,
        orientacion="horizontal",
    )

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=capacitaciones_sst.pdf"
        },
    )


@router.get("/capacitaciones/excel/{empresa_id}")
def exportar_capacitaciones_excel(
    empresa_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(EXPORTAR_REPORTES),
):
    empresa, configuracion = obtener_empresa_y_configuracion(db, empresa_id)

    items = (
        db.query(CapacitacionSST)
        .filter(
            CapacitacionSST.empresa_id == empresa_id,
            CapacitacionSST.activo == True,
        )
        .order_by(CapacitacionSST.id.asc())
        .all()
    )

    columnas = [
        "ID",
        "Código",
        "Nombre",
        "Tema",
        "Objetivo",
        "Tipo",
        "Modalidad",
        "Capacitador",
        "Responsable",
        "Fecha programada",
        "Fecha ejecución",
        "Duración horas",
        "Lugar",
        "Población objetivo",
        "Total asistentes",
        "Estado",
        "Cumplimiento",
        "Evidencia",
        "Observaciones",
    ]

    filas = [
        [
            i.id,
            i.codigo,
            i.nombre,
            i.tema,
            i.objetivo or "",
            i.tipo,
            i.modalidad,
            i.capacitador or "",
            i.responsable or "",
            str(i.fecha_programada or ""),
            str(i.fecha_ejecucion or ""),
            float(i.duracion_horas or 0),
            i.lugar or "",
            i.poblacion_objetivo or "",
            i.total_asistentes or 0,
            i.estado,
            f"{i.cumplimiento}%",
            i.evidencia or "",
            i.observaciones or "",
        ]
        for i in items
    ]

    excel = generar_excel_corporativo(
        titulo="Capacitaciones SST",
        codigo="CAP-001",
        empresa=empresa,
        configuracion=configuracion,
        columnas=columnas,
        filas=filas,
    )

    return StreamingResponse(
        excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=capacitaciones_sst.xlsx"
        },
    )

# ============================================================
# ROUTER DASHBOARD SST INTELIGENTE
# FASE 1.5.4 - DASHBOARD + PLAN MEJORAMIENTO SST
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.auth.dependencies import require_roles

from app.models.empresa import Empresa
from app.models.evaluacion_inicial import EvaluacionInicialSST
from app.models.plan_mejoramiento import PlanMejoramientoSST

from app.schemas.dashboard_sst import (
    DashboardEmpresaSST,
    DashboardSSTResponse,
)


router = APIRouter(
    prefix="/dashboard-sst",
    tags=["Dashboard SST Inteligente"],
)


ROLES_DASHBOARD = [
    "SUPER_ADMIN",
    "ADMIN_EMPRESA",
    "RESPONSABLE_SST",
    "AUDITOR",
]


def calcular_nivel_sst(porcentaje: float) -> str:
    if porcentaje >= 86:
        return "ACEPTABLE"

    if porcentaje >= 61:
        return "MODERADO"

    return "CRITICO"


def obtener_ultima_evaluacion_empresa(db: Session, empresa_id: int):
    return (
        db.query(EvaluacionInicialSST)
        .options(joinedload(EvaluacionInicialSST.items))
        .filter(
            EvaluacionInicialSST.empresa_id == empresa_id,
            EvaluacionInicialSST.activo == True,
        )
        .order_by(EvaluacionInicialSST.id.desc())
        .first()
    )


def construir_resumen_empresa(db: Session, empresa: Empresa) -> DashboardEmpresaSST:
    evaluacion = obtener_ultima_evaluacion_empresa(db, empresa.id)
    total_estandares = int(empresa.total_estandares_sst or 0)

    if not evaluacion:
        return DashboardEmpresaSST(
            empresa_id=empresa.id,
            empresa=empresa.nombre,
            total_estandares=total_estandares,
            cumplen=0,
            no_cumplen=0,
            no_aplican=0,
            porcentaje=0,
            nivel="SIN_EVALUACION",
        )

    items_activos = [item for item in evaluacion.items if item.activo]

    cumplen = len([item for item in items_activos if item.respuesta == "CUMPLE"])
    no_cumplen = len([item for item in items_activos if item.respuesta == "NO_CUMPLE"])
    no_aplican = len([item for item in items_activos if item.respuesta == "NO_APLICA"])

    evaluables = len([item for item in items_activos if item.respuesta != "NO_APLICA"])
    porcentaje = round((cumplen / evaluables) * 100, 2) if evaluables > 0 else 0

    return DashboardEmpresaSST(
        empresa_id=empresa.id,
        empresa=empresa.nombre,
        total_estandares=total_estandares or len(items_activos),
        cumplen=cumplen,
        no_cumplen=no_cumplen,
        no_aplican=no_aplican,
        porcentaje=porcentaje,
        nivel=calcular_nivel_sst(porcentaje),
    )


def obtener_kpi_plan_mejoramiento(db: Session) -> dict:
    acciones = (
        db.query(PlanMejoramientoSST)
        .filter(PlanMejoramientoSST.activo == True)
        .all()
    )

    total_acciones = len(acciones)
    pendientes = len([x for x in acciones if x.estado == "PENDIENTE"])
    en_proceso = len([x for x in acciones if x.estado == "EN_PROCESO"])
    vencidas = len([x for x in acciones if x.estado == "VENCIDO"])
    finalizadas = len([x for x in acciones if x.estado == "FINALIZADO"])

    cumplimiento = (
        round((finalizadas / total_acciones) * 100, 2)
        if total_acciones > 0
        else 0
    )

    return {
        "total_acciones": total_acciones,
        "acciones_pendientes": pendientes,
        "acciones_en_proceso": en_proceso,
        "acciones_vencidas": vencidas,
        "acciones_finalizadas": finalizadas,
        "cumplimiento_plan_mejoramiento": cumplimiento,
    }


@router.get("/resumen", response_model=DashboardSSTResponse)
def resumen_dashboard_sst(
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(ROLES_DASHBOARD)),
):
    empresas = (
        db.query(Empresa)
        .filter(Empresa.estado == True)
        .order_by(Empresa.id.desc())
        .all()
    )

    ranking = []
    alertas = []

    for empresa in empresas:
        resumen = construir_resumen_empresa(db=db, empresa=empresa)
        ranking.append(resumen)

        if resumen.nivel == "SIN_EVALUACION":
            alertas.append(
                f"La empresa {empresa.nombre} no tiene evaluación inicial registrada."
            )
        elif resumen.nivel == "CRITICO":
            alertas.append(
                f"La empresa {empresa.nombre} está en nivel crítico con {resumen.porcentaje}% de cumplimiento."
            )
        elif resumen.porcentaje < 86:
            alertas.append(
                f"La empresa {empresa.nombre} requiere plan de mejora. Cumplimiento actual: {resumen.porcentaje}%."
            )

    total_empresas = len(ranking)
    empresas_aceptables = len([x for x in ranking if x.nivel == "ACEPTABLE"])
    empresas_moderadas = len([x for x in ranking if x.nivel == "MODERADO"])
    empresas_criticas = len(
        [x for x in ranking if x.nivel in ["CRITICO", "SIN_EVALUACION"]]
    )

    promedio_general = (
        round(sum([x.porcentaje for x in ranking]) / total_empresas, 2)
        if total_empresas > 0
        else 0
    )

    ranking = sorted(ranking, key=lambda item: item.porcentaje, reverse=True)
    kpi_plan = obtener_kpi_plan_mejoramiento(db)

    return DashboardSSTResponse(
        total_empresas=total_empresas,
        empresas_aceptables=empresas_aceptables,
        empresas_moderadas=empresas_moderadas,
        empresas_criticas=empresas_criticas,
        promedio_general=promedio_general,
        total_acciones=kpi_plan["total_acciones"],
        acciones_pendientes=kpi_plan["acciones_pendientes"],
        acciones_en_proceso=kpi_plan["acciones_en_proceso"],
        acciones_vencidas=kpi_plan["acciones_vencidas"],
        acciones_finalizadas=kpi_plan["acciones_finalizadas"],
        cumplimiento_plan_mejoramiento=kpi_plan["cumplimiento_plan_mejoramiento"],
        ranking=ranking,
        alertas=alertas,
    )
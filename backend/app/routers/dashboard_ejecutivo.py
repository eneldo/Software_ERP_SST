# ============================================================
# ROUTER DASHBOARD EJECUTIVO SST PRO ENTERPRISE
# FASE 1.6 - ERP SST PRO
# H-012: KPIs reales + 8 indicadores §21
# ============================================================

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.database import get_db
from app.auth.dependencies import require_roles

from app.models.capacitacion import CapacitacionSST
from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.area import Area
from app.models.cargo import Cargo
from app.models.empleado import Empleado
from app.models.incidente import IncidenteAccidenteSST
from app.models.inspeccion import InspeccionSST
from app.models.plan_mejoramiento import PlanMejoramientoSST
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.permiso import Permiso
from app.models.auditoria import Auditoria
from app.models.login_intento import LoginIntento
from app.models.politica_sst import PoliticaSST
from app.models.examen_medico import ExamenMedico
from app.models.epp import EPPEntrega
from app.models.matriz_iper import MatrizIPER
from app.models.capa import CapaSST

try:
    from app.models.evaluacion_inicial import EvaluacionInicialSST
except ImportError:
    EvaluacionInicialSST = None

try:
    from app.models.examen_medico import ExamenMedicoSST
except ImportError:
    ExamenMedicoSST = None

from app.schemas.dashboard_ejecutivo_schema import DashboardEjecutivoSSTResponse


router = APIRouter(
    prefix="/dashboard-ejecutivo",
    tags=["Dashboard Ejecutivo SST PRO"]
)


def _empresa_id_autorizada(usuario, empresa_id: int | None) -> int | None:
    if str(getattr(usuario, "rol", "") or "").upper() == "SUPER_ADMIN":
        return empresa_id
    usuario_empresa_id = getattr(usuario, "empresa_id", None)
    if usuario_empresa_id is None:
        raise HTTPException(status_code=403, detail="Usuario sin empresa asignada")
    if empresa_id is not None and int(usuario_empresa_id) != int(empresa_id):
        raise HTTPException(status_code=403, detail="No tiene permisos sobre esta empresa")
    return int(usuario_empresa_id)


def _calcular_cumplimiento_evaluacion(db: Session, empresa_id: int) -> float:
    if EvaluacionInicialSST is None:
        return 0.0

    ultima = (
        db.query(EvaluacionInicialSST)
        .filter(
            EvaluacionInicialSST.empresa_id == empresa_id,
            EvaluacionInicialSST.activo == True,
        )
        .order_by(EvaluacionInicialSST.id.desc())
        .first()
    )

    if ultima:
        val = getattr(ultima, "porcentaje_cumplimiento", None)
        if val is not None:
            return float(val)
    return 0.0


def _calcular_cumplimiento_politicas(db: Session, empresa_id: int) -> float:
    tipos_requeridos = {"POLITICA_SST", "CONVIVENCIA", "ALCOHOL_TABACO"}
    total = len(tipos_requeridos)

    try:
        aprobadas = db.query(func.count(PoliticaSST.id)).filter(
            PoliticaSST.empresa_id == empresa_id,
            PoliticaSST.tipo_politica.in_(tipos_requeridos),
            PoliticaSST.estado == "APROBADA",
            PoliticaSST.activo == True,
        ).scalar()
        if not isinstance(aprobadas, int):
            return 0.0
        return round((aprobadas / total) * 100, 2) if total > 0 else 0.0
    except Exception:
        return 0.0


def _calcular_cumplimiento_plan_anual(db: Session, empresa_id: int) -> float:
    try:
        from app.models.plan_anual import PlanAnualSST

        total = db.query(PlanAnualSST).filter(
            PlanAnualSST.empresa_id == empresa_id,
            PlanAnualSST.activo == True,
        ).count()

        if not isinstance(total, int) or total == 0:
            return 0.0

        ejecutadas = db.query(PlanAnualSST).filter(
            PlanAnualSST.empresa_id == empresa_id,
            PlanAnualSST.activo == True,
            PlanAnualSST.estado == "EJECUTADO",
        ).count()

        if not isinstance(ejecutadas, int):
            return 0.0

        return round((ejecutadas / total) * 100, 2)
    except Exception:
        return 0.0


def _contar_acciones(db: Session, empresa_id: int) -> dict:
    hoy = datetime.now(timezone.utc).date()
    defaults = {
        "pendientes": 0, "en_proceso": 0, "vencidas": 0,
        "proximas_vencer": 0, "finalizadas": 0,
    }

    try:
        pendientes = db.query(PlanMejoramientoSST).filter(
            PlanMejoramientoSST.empresa_id == empresa_id,
            PlanMejoramientoSST.activo == True,
            PlanMejoramientoSST.estado == "PENDIENTE",
        ).count()
        if not isinstance(pendientes, int):
            return defaults
    except Exception:
        return defaults

    try:
        en_proceso = db.query(PlanMejoramientoSST).filter(
            PlanMejoramientoSST.empresa_id == empresa_id,
            PlanMejoramientoSST.activo == True,
            PlanMejoramientoSST.estado == "EN_PROCESO",
        ).count()
        if not isinstance(en_proceso, int):
            en_proceso = 0
    except Exception:
        en_proceso = 0

    try:
        vencidas = db.query(PlanMejoramientoSST).filter(
            PlanMejoramientoSST.empresa_id == empresa_id,
            PlanMejoramientoSST.activo == True,
            PlanMejoramientoSST.estado.in_(["PENDIENTE", "EN_PROCESO"]),
            PlanMejoramientoSST.fecha_compromiso < hoy,
        ).count()
        if not isinstance(vencidas, int):
            vencidas = 0
    except Exception:
        vencidas = 0

    try:
        proximas_vencer = db.query(PlanMejoramientoSST).filter(
            PlanMejoramientoSST.empresa_id == empresa_id,
            PlanMejoramientoSST.activo == True,
            PlanMejoramientoSST.estado.in_(["PENDIENTE", "EN_PROCESO"]),
            PlanMejoramientoSST.fecha_compromiso >= hoy,
            PlanMejoramientoSST.fecha_compromiso <= hoy + timedelta(days=15),
        ).count()
        if not isinstance(proximas_vencer, int):
            proximas_vencer = 0
    except Exception:
        proximas_vencer = 0

    try:
        finalizadas = db.query(PlanMejoramientoSST).filter(
            PlanMejoramientoSST.empresa_id == empresa_id,
            PlanMejoramientoSST.activo == True,
            PlanMejoramientoSST.estado == "FINALIZADO",
        ).count()
        if not isinstance(finalizadas, int):
            finalizadas = 0
    except Exception:
        finalizadas = 0

    return {
        "pendientes": pendientes,
        "en_proceso": en_proceso,
        "vencidas": vencidas,
        "proximas_vencer": proximas_vencer,
        "finalizadas": finalizadas,
    }


@router.get("/sst", response_model=DashboardEjecutivoSSTResponse)
def dashboard_ejecutivo_sst(
    empresa_id: int | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"]))
):
    tenant_id = _empresa_id_autorizada(usuario, empresa_id)
    empresa_id = tenant_id

    query_sedes = db.query(Sede)
    query_areas = db.query(Area)
    query_cargos = db.query(Cargo)
    query_empleados = db.query(Empleado)
    query_usuarios = db.query(Usuario)

    empresa_nombre = "Todas las empresas"

    if empresa_id:
        query_sedes = query_sedes.filter(Sede.empresa_id == empresa_id)
        query_areas = query_areas.filter(Area.empresa_id == empresa_id)
        query_cargos = query_cargos.filter(Cargo.empresa_id == empresa_id)
        query_empleados = query_empleados.filter(Empleado.empresa_id == empresa_id)
        query_usuarios = query_usuarios.filter(Usuario.empresa_id == empresa_id)

        empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
        if empresa:
            empresa_nombre = empresa.nombre

    total_sedes = query_sedes.count()
    total_areas = query_areas.count()
    total_cargos = query_cargos.count()
    total_empleados = query_empleados.count()
    empleados_activos = query_empleados.filter(Empleado.activo == True).count()
    empleados_inactivos = query_empleados.filter(Empleado.activo == False).count()
    total_usuarios = query_usuarios.count()

    total_roles = db.query(Rol).count()
    total_permisos = db.query(Permiso).count()
    query_auditoria = db.query(Auditoria)
    if empresa_id is not None:
        query_auditoria = query_auditoria.filter(Auditoria.empresa_id == empresa_id)
    total_auditorias = query_auditoria.count()
    total_logins = db.query(LoginIntento).count()

    total_capacitaciones = db.query(CapacitacionSST).filter(
        CapacitacionSST.empresa_id == empresa_id
    ).count() if empresa_id else db.query(CapacitacionSST).count()

    total_inspecciones = db.query(InspeccionSST).filter(
        InspeccionSST.empresa_id == empresa_id
    ).count() if empresa_id else db.query(InspeccionSST).count()

    total_accidentes = db.query(IncidenteAccidenteSST).filter(
        IncidenteAccidenteSST.tipo_evento == "ACCIDENTE",
        IncidenteAccidenteSST.empresa_id == empresa_id,
    ).count() if empresa_id else db.query(IncidenteAccidenteSST).filter(
        IncidenteAccidenteSST.tipo_evento == "ACCIDENTE"
    ).count()

    total_incidentes = db.query(IncidenteAccidenteSST).filter(
        IncidenteAccidenteSST.tipo_evento == "INCIDENTE",
        IncidenteAccidenteSST.empresa_id == empresa_id,
    ).count() if empresa_id else db.query(IncidenteAccidenteSST).filter(
        IncidenteAccidenteSST.tipo_evento == "INCIDENTE"
    ).count()

    total_planes = db.query(PlanMejoramientoSST).filter(
        PlanMejoramientoSST.empresa_id == empresa_id
    ).count() if empresa_id else db.query(PlanMejoramientoSST).count()

    eval_p = _calcular_cumplimiento_evaluacion(db, empresa_id) if empresa_id else 0
    polit_p = _calcular_cumplimiento_politicas(db, empresa_id) if empresa_id else 0
    plan_p = _calcular_cumplimiento_plan_anual(db, empresa_id) if empresa_id else 0
    acciones = _contar_acciones(db, empresa_id) if empresa_id else {
        "pendientes": 0, "en_proceso": 0, "vencidas": 0, "proximas_vencer": 0, "finalizadas": 0
    }

    hoy = datetime.now(timezone.utc).date()

    examenes_query = db.query(ExamenMedico).filter(ExamenMedico.activo == True)
    if empresa_id:
        examenes_query = examenes_query.join(Empleado, Empleado.id == ExamenMedico.empleado_id).filter(Empleado.empresa_id == empresa_id)
    examenes_pendientes = examenes_query.filter(ExamenMedico.estado.notin_(["FINALIZADO", "CERRADO", "NORMAL"])).count()
    examenes_vencidos = examenes_query.filter(ExamenMedico.fecha_vencimiento < hoy).count()

    inspecciones_pendientes_q = db.query(InspeccionSST).filter(InspeccionSST.activo == True, InspeccionSST.estado.notin_(["CERRADA", "EJECUTADA", "FINALIZADA"]))
    if empresa_id:
        inspecciones_pendientes_q = inspecciones_pendientes_q.filter(InspeccionSST.empresa_id == empresa_id)
    inspecciones_pendientes = inspecciones_pendientes_q.count()

    epp_query = db.query(EPPEntrega).filter(EPPEntrega.activo == True)
    if empresa_id:
        epp_query = epp_query.filter(EPPEntrega.empresa_id == empresa_id)
    epp_reposicion_pendiente = epp_query.filter(EPPEntrega.fecha_reposicion <= hoy).count()

    iper_query = db.query(MatrizIPER).filter(MatrizIPER.activo == True)
    if empresa_id:
        iper_query = iper_query.filter(MatrizIPER.empresa_id == empresa_id)
    iper_total = iper_query.count()
    iper_alto_riesgo = iper_query.filter(MatrizIPER.nivel_riesgo.in_(["I", "II"])).count() if iper_total > 0 else 0

    capas_query = db.query(CapaSST).filter(CapaSST.activo == True, CapaSST.estado.notin_(["CERRADA", "CERRADO", "FINALIZADA"]))
    if empresa_id:
        capas_query = capas_query.filter(CapaSST.empresa_id == empresa_id)
    capas_vencidas = capas_query.filter(CapaSST.fecha_compromiso < hoy).count()

    componentes = []
    if total_sedes > 0:
        componentes.append(1)
    if total_areas > 0:
        componentes.append(1)
    if total_cargos > 0:
        componentes.append(1)
    if total_empleados > 0:
        componentes.append(1)
    if total_capacitaciones > 0:
        componentes.append(1)
    if total_inspecciones > 0:
        componentes.append(1)
    if eval_p > 0:
        componentes.append(1)
    if polit_p > 0:
        componentes.append(1)
    if plan_p > 0:
        componentes.append(1)
    if total_planes > 0:
        componentes.append(1)

    base_componentes = 10
    cumplimiento_sg_sst = round((len(componentes) / base_componentes) * 100, 2)
    cumplimiento_resolucion_0312 = eval_p if eval_p > 0 else round(cumplimiento_sg_sst * 0.65, 2)

    if cumplimiento_sg_sst >= 85:
        nivel_alerta = "BAJO"
    elif cumplimiento_sg_sst >= 60:
        nivel_alerta = "MEDIO"
    else:
        nivel_alerta = "ALTO"

    return {
        "empresa_id": empresa_id,
        "empresa_nombre": empresa_nombre,
        "cumplimiento_sg_sst": cumplimiento_sg_sst,
        "cumplimiento_resolucion_0312": cumplimiento_resolucion_0312,
        "nivel_alerta": nivel_alerta,
        "kpis": [
            {
                "codigo": "EMP",
                "titulo": "Empleados",
                "valor": total_empleados,
                "subtitulo": f"{empleados_activos} activos",
                "estado": "OK" if total_empleados > 0 else "ALERTA",
            },
            {
                "codigo": "SED",
                "titulo": "Sedes",
                "valor": total_sedes,
                "subtitulo": "Sedes operativas",
                "estado": "OK" if total_sedes > 0 else "ALERTA",
            },
            {
                "codigo": "CAP",
                "titulo": "Capacitaciones",
                "valor": total_capacitaciones,
                "subtitulo": "Realizadas",
                "estado": "OK" if total_capacitaciones > 0 else "PENDIENTE",
                "url_detalle": "/hacer/capacitaciones",
            },
            {
                "codigo": "INS",
                "titulo": "Inspecciones",
                "valor": total_inspecciones,
                "subtitulo": "Realizadas",
                "estado": "OK" if total_inspecciones > 0 else "PENDIENTE",
                "url_detalle": "/hacer/inspecciones",
            },
            {
                "codigo": "ACC",
                "titulo": "Accidentes",
                "valor": total_accidentes,
                "subtitulo": "Este período",
                "estado": "OK" if total_accidentes == 0 else "ALERTA",
                "url_detalle": "/hacer/incidentes",
            },
            {
                "codigo": "INC",
                "titulo": "Incidentes",
                "valor": total_incidentes,
                "subtitulo": "Este período",
                "estado": "OK" if total_incidentes == 0 else "ALERTA",
                "url_detalle": "/hacer/incidentes",
            },
            {
                "codigo": "ACP",
                "titulo": "Acciones",
                "valor": acciones["pendientes"] + acciones["en_proceso"],
                "subtitulo": f"{acciones['vencidas']} vencidas",
                "estado": "OK" if acciones["vencidas"] == 0 else "ALERTA",
                "url_detalle": "/planear/plan-mejoramiento",
            },
            {
                "codigo": "POL",
                "titulo": "Políticas",
                "valor": polit_p,
                "subtitulo": f"% aprobadas ({polit_p}%)",
                "estado": "OK" if polit_p >= 80 else "PENDIENTE",
                "url_detalle": "/planear/politica-sst",
            },
            {
                "codigo": "EVA",
                "titulo": "Evaluación Inicial",
                "valor": eval_p,
                "subtitulo": f"% cumplimiento ({eval_p}%)",
                "estado": "OK" if eval_p >= 60 else "ALERTA",
                "url_detalle": "/planear/evaluacion-inicial",
            },
            {
                "codigo": "PAN",
                "titulo": "Plan Anual",
                "valor": plan_p,
                "subtitulo": f"% ejecutado ({plan_p}%)",
                "estado": "OK" if plan_p >= 50 else "PENDIENTE",
                "url_detalle": "/planear/plan-anual",
            },
            {
                "codigo": "EXA",
                "titulo": "Exámenes Médicos",
                "valor": examenes_pendientes,
                "subtitulo": f"{examenes_vencidos} vencidos",
                "estado": "OK" if examenes_pendientes == 0 else "ALERTA",
                "url_detalle": "/hacer/examenes-medicos",
            },
            {
                "codigo": "INS_P",
                "titulo": "Inspecciones Pendientes",
                "valor": inspecciones_pendientes,
                "subtitulo": "Por ejecutar",
                "estado": "OK" if inspecciones_pendientes == 0 else "ALERTA",
                "url_detalle": "/hacer/inspecciones",
            },
            {
                "codigo": "EPP_R",
                "titulo": "EPP por Reposición",
                "valor": epp_reposicion_pendiente,
                "subtitulo": "Reposiciones vencidas",
                "estado": "OK" if epp_reposicion_pendiente == 0 else "ALERTA",
                "url_detalle": "/hacer/epp",
            },
            {
                "codigo": "IPER",
                "titulo": "Riesgos Altos",
                "valor": iper_alto_riesgo,
                "subtitulo": f"{iper_total} evaluados",
                "estado": "OK" if iper_alto_riesgo == 0 else "ALERTA",
                "url_detalle": "/planear/matriz-iper",
            },
            {
                "codigo": "CAP_V",
                "titulo": "CAPA Vencidas",
                "valor": capas_vencidas,
                "subtitulo": "Acciones correctivas vencidas",
                "estado": "OK" if capas_vencidas == 0 else "ALERTA",
                "url_detalle": "/hacer/capa",
            },
        ],
        "empleados_estado": [
            {"nombre": "Activos", "valor": empleados_activos},
            {"nombre": "Inactivos", "valor": empleados_inactivos},
        ],
        "estructura_organizacional": [
            {"nombre": "Sedes", "valor": total_sedes},
            {"nombre": "Áreas", "valor": total_areas},
            {"nombre": "Cargos", "valor": total_cargos},
            {"nombre": "Empleados", "valor": total_empleados},
        ],
        "seguridad_auditoria": [
            {"nombre": "Usuarios", "valor": total_usuarios},
            {"nombre": "Roles", "valor": total_roles},
            {"nombre": "Permisos", "valor": total_permisos},
            {"nombre": "Auditorías", "valor": total_auditorias},
            {"nombre": "Logins", "valor": total_logins},
        ],
        "avance_phva": [
            {"nombre": "Planear", "valor": round((polit_p + eval_p + plan_p) / 3, 1) if empresa_id else 0},
            {"nombre": "Hacer", "valor": round((total_capacitaciones + total_inspecciones) / max(total_empleados, 1) * 100, 1) if empresa_id else 0},
            {"nombre": "Verificar", "valor": round(total_auditorias / max(total_empleados, 1) * 100, 1) if empresa_id else 0},
            {"nombre": "Actuar", "valor": round(acciones["finalizadas"] / max(acciones["pendientes"] + acciones["en_proceso"] + acciones["finalizadas"], 1) * 100, 1) if empresa_id else 0},
        ],
        "actividades_recientes": [
            {
                "id": a.id,
                "modulo": "Auditoría",
                "accion": a.accion or f"{a.metodo} {a.ruta}",
                "ruta": a.ruta,
                "metodo": a.metodo,
                "status_code": a.status_code,
                "fecha": a.fecha_creacion.isoformat() if a.fecha_creacion else "",
            }
            for a in query_auditoria.order_by(Auditoria.id.desc()).limit(8).all()
        ],
    }

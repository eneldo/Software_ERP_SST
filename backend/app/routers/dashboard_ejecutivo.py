# ============================================================
# ROUTER DASHBOARD EJECUTIVO SST PRO ENTERPRISE
# FASE 1.6 - ERP SST PRO
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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


@router.get("/sst", response_model=DashboardEjecutivoSSTResponse)
def dashboard_ejecutivo_sst(
    empresa_id: int | None = None,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles(["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST", "AUDITOR"]))
):
    """
    Dashboard ejecutivo SST Enterprise.
    Usa datos reales administrativos y operativos del tenant autorizado.
    """

    tenant_id = _empresa_id_autorizada(usuario, empresa_id)
    empresa_id = tenant_id

    query_empresas = db.query(Empresa)
    query_sedes = db.query(Sede)
    query_areas = db.query(Area)
    query_cargos = db.query(Cargo)
    query_empleados = db.query(Empleado)
    query_usuarios = db.query(Usuario)

    empresa_nombre = "Todas las empresas"

    if empresa_id:
        query_empresas = query_empresas.filter(Empresa.id == empresa_id)
        query_sedes = query_sedes.filter(Sede.empresa_id == empresa_id)
        query_areas = query_areas.filter(Area.empresa_id == empresa_id)
        query_cargos = query_cargos.filter(Cargo.empresa_id == empresa_id)
        query_empleados = query_empleados.filter(Empleado.empresa_id == empresa_id)
        query_usuarios = query_usuarios.filter(Usuario.empresa_id == empresa_id)

        empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
        if empresa:
            empresa_nombre = empresa.nombre

    total_empresas = query_empresas.count()
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

    filtro_empresa = {"empresa_id": empresa_id} if empresa_id is not None else {}
    total_capacitaciones = db.query(CapacitacionSST).filter_by(**filtro_empresa).count() if filtro_empresa else db.query(CapacitacionSST).count()
    total_inspecciones = db.query(InspeccionSST).filter_by(**filtro_empresa).count() if filtro_empresa else db.query(InspeccionSST).count()
    total_accidentes = db.query(IncidenteAccidenteSST).filter(
        IncidenteAccidenteSST.tipo_evento == "ACCIDENTE",
        *([IncidenteAccidenteSST.empresa_id == empresa_id] if empresa_id is not None else []),
    ).count()
    total_planes = db.query(PlanMejoramientoSST).filter_by(**filtro_empresa).count() if filtro_empresa else db.query(PlanMejoramientoSST).count()

    # KPIs provisionales inteligentes mientras se construyen módulos normativos.
    # Se calculan con madurez organizacional base.
    base_componentes = 5
    componentes_ok = 0
    if total_empresas > 0:
        componentes_ok += 1
    if total_sedes > 0:
        componentes_ok += 1
    if total_areas > 0:
        componentes_ok += 1
    if total_cargos > 0:
        componentes_ok += 1
    if total_empleados > 0:
        componentes_ok += 1

    cumplimiento_sg_sst = round((componentes_ok / base_componentes) * 100, 2)
    cumplimiento_resolucion_0312 = round(cumplimiento_sg_sst * 0.65, 2)

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
                "subtitulo": "Sedes operativas registradas",
                "estado": "OK" if total_sedes > 0 else "ALERTA",
            },
            {
                "codigo": "ARE",
                "titulo": "Áreas",
                "valor": total_areas,
                "subtitulo": "Estructura organizacional",
                "estado": "OK" if total_areas > 0 else "ALERTA",
            },
            {
                "codigo": "CAR",
                "titulo": "Cargos",
                "valor": total_cargos,
                "subtitulo": "Cargos asociados al riesgo",
                "estado": "OK" if total_cargos > 0 else "ALERTA",
            },
            {
                "codigo": "CAP",
                "titulo": "Capacitaciones",
                "valor": total_capacitaciones,
                "subtitulo": "Módulo SST",
                "estado": "OK" if total_capacitaciones > 0 else "PENDIENTE",
                "url_detalle": "/hacer/capacitaciones",
            },
            {
                "codigo": "INS",
                "titulo": "Inspecciones",
                "valor": total_inspecciones,
                "subtitulo": "Módulo SST",
                "estado": "OK" if total_inspecciones > 0 else "PENDIENTE",
                "url_detalle": "/hacer/inspecciones",
            },
            {
                "codigo": "ACC",
                "titulo": "Accidentes",
                "valor": total_accidentes,
                "subtitulo": "Módulo SST",
                "estado": "OK",
                "url_detalle": "/hacer/accidentes",
            },
            {
                "codigo": "ACP",
                "titulo": "Planes de acción",
                "valor": total_planes,
                "subtitulo": "Módulo SST",
                "estado": "OK" if total_planes > 0 else "PENDIENTE",
                "url_detalle": "/planear/plan-mejoramiento",
            },
        ],
        "empleados_estado": [
            {"nombre": "Activos", "valor": empleados_activos},
            {"nombre": "Inactivos", "valor": empleados_inactivos},
        ],
        "estructura_organizacional": [
            {"nombre": "Empresas", "valor": total_empresas},
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
            {"nombre": "Planear", "valor": 10},
            {"nombre": "Hacer", "valor": 5},
            {"nombre": "Verificar", "valor": 5},
            {"nombre": "Actuar", "valor": 5},
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

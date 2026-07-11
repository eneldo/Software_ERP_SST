# ============================================================
# MAIN APP - ERP SST PRO
# FASE 36.8 — Logging Enterprise y Manejo de Errores
# ============================================================

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.config import settings
from app.core.default_permissions import ensure_default_permissions_on_startup
from app.core.exception_handlers import register_exception_handlers
from app.core.logging_config import setup_logging
from app.database import Base, engine
from app.middlewares.audit_middleware import AuditMiddleware
from app.middlewares.rate_limit import (
    MemoryRateLimitStore,
    RateLimitMiddleware,
    RateLimitPolicy,
    RedisRateLimitStore,
)
from app.middlewares.request_context import RequestContextMiddleware
from app.middlewares.security_headers import SecurityHeadersMiddleware

# Importación explícita de modelos para mantener disponible la metadata SQLAlchemy.
# No eliminar: varios proyectos sin Alembic aún dependen de estos imports al inicializar.
from app.models.alerta_medida_correctiva import AlertaMedidaCorrectivaSST  # noqa: F401
from app.models.archivo_sst import ArchivoSST  # noqa: F401
from app.models.area import Area  # noqa: F401
from app.models.area_historial import AreaHistorialSST  # noqa: F401
from app.models.auditoria import Auditoria  # noqa: F401
from app.models.auditoria_hallazgo_evidencia import AuditoriaHallazgoEvidenciaSST  # noqa: F401
from app.models.auditoria_sst import AuditoriaHallazgoSST, AuditoriaSST  # noqa: F401
from app.models.biblioteca_documental import BibliotecaDocumental  # noqa: F401
from app.models.capa import CapaSST, CapaSeguimientoSST  # noqa: F401
from app.models.capacitacion import CapacitacionAsistenteSST, CapacitacionSST  # noqa: F401
from app.models.capacitacion_certificado import CapacitacionCertificado  # noqa: F401
from app.models.cargo import Cargo  # noqa: F401
from app.models.configuracion_documental import ConfiguracionDocumental  # noqa: F401
from app.models.configuracion_sistema import ConfiguracionSistema  # noqa: F401
from app.models.documento_validacion import DocumentoValidacionSST  # noqa: F401
from app.models.documento_version import DocumentoVersion  # noqa: F401
from app.models.empleado import Empleado  # noqa: F401
from app.models.empresa import Empresa  # noqa: F401
from app.models.epp import EPPCatalogo, EPPEntrega  # noqa: F401
from app.models.evaluacion_inicial import EvaluacionInicialItemSST, EvaluacionInicialSST  # noqa: F401
from app.models.examen_medico import ExamenMedico  # noqa: F401
from app.models.firma_digital import FirmaDigitalSST  # noqa: F401
from app.models.firma_documental_sst import FirmaDocumentalSST  # noqa: F401
from app.models.incidente import IncidenteAccidenteSST, IncidenteLesionadoSST, IncidenteTestigoSST  # noqa: F401
from app.models.indicador_sst import IndicadorSST  # noqa: F401
from app.models.inspeccion import InspeccionHallazgoSST, InspeccionSST  # noqa: F401
from app.models.inspeccion_seguimiento import InspeccionHallazgoSeguimientoSST  # noqa: F401
from app.models.login_intento import LoginIntento  # noqa: F401
from app.models.matriz_legal import MatrizLegalSST  # noqa: F401
from app.models.matriz_peligros import MatrizPeligrosSST  # noqa: F401
from app.models.notificacion_sst import ConfiguracionNotificacionSST, NotificacionSST  # noqa: F401
from app.models.objetivo_sst import ObjetivoSST  # noqa: F401
from app.models.permiso import Permiso  # noqa: F401
from app.models.plan_anual import PlanAnualSST  # noqa: F401
from app.models.plan_mejoramiento import PlanMejoramientoSST  # noqa: F401
from app.models.plan_mejoramiento_evidencia import PlanMejoramientoEvidenciaSST  # noqa: F401
from app.models.plan_mejoramiento_seguimiento import PlanMejoramientoSeguimientoSST  # noqa: F401
from app.models.politica_sst import PoliticaSST  # noqa: F401
from app.models.reporte_evidencia_sst import ReporteEvidenciaSST  # noqa: F401
from app.models.reporte_inseguridad import ReporteInseguridadSST  # noqa: F401
from app.models.revision_direccion import RevisionDireccionCompromisoSST, RevisionDireccionSST  # noqa: F401
from app.models.revision_version import RevisionDireccionVersionSST  # noqa: F401
from app.models.rol import Rol  # noqa: F401
from app.models.sede import Sede  # noqa: F401
from app.models.usuario import Usuario  # noqa: F401
from app.models.usuario_permiso import UsuarioPermiso  # noqa: F401

setup_logging()

from app.routers import (
    alertas_medidas_correctivas,
    archivos_protegidos,
    archivos_sst,
    areas,
    auditoria,
    auditoria_evidencias,
    auditoria_hallazgo_evidencias,
    auditoria_pdf,
    auditoria_sst,
    auth,
    biblioteca_documental,
    capa,
    capacitacion_asistentes,
    capacitacion_certificados,
    capacitaciones,
    cargos,
    configuracion_documental,
    configuracion_sistema,
    dashboard,
    dashboard_documental,
    dashboard_ejecutivo,
    dashboard_saas,
    dashboard_sst,
    documental_enterprise,
    documento_validacion,
    documentos_versiones,
    empleados,
    empresas,
    epp,
    evaluacion_inicial,
    examenes_medicos,
    exportaciones_sst,
    firma_documental,
    firmas_digitales,
    incidentes,
    indicadores_bi,
    indicadores_sst,
    inspeccion_seguimientos,
    inspecciones,
    inspecciones_exportaciones,
    inspecciones_exportaciones_platinum,
    matriz_legal,
    matriz_peligros,
    medidas_correctivas,
    medidas_correctivas_bi,
    medidas_correctivas_exportaciones,
    medidas_evidencias_inteligentes,
    notificaciones_sst,
    objetivos_sst,
    observabilidad,
    permisos,
    plan_anual,
    plan_mejoramiento,
    plan_mejoramiento_evidencias,
    plan_mejoramiento_seguimientos,
    politica_sst,
    portal_empleado,
    reporte_anonimo_sst,
    reporte_evidencias,
    reportes_anonimos_admin,
    revision_direccion,
    revision_direccion_pdf,
    revision_version,
    roles,
    sedes,
    usuarios_sistema,
    relation_guard,
)


def create_app() -> FastAPI:
    if settings.AUTO_CREATE_TABLES:
        Base.metadata.create_all(bind=engine)
        ensure_default_permissions_on_startup()

    app = FastAPI(
        title=settings.APP_NAME,
        description="Sistema de Gestión de Seguridad y Salud en el Trabajo - Colombia",
        version=settings.APP_VERSION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
        openapi_url=settings.OPENAPI_URL,
    )

    register_exception_handlers(app)

    app.add_middleware(RequestContextMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.TRUSTED_HOSTS:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.TRUSTED_HOSTS)

    if settings.HTTPS_REDIRECT_ENABLED:
        app.add_middleware(HTTPSRedirectMiddleware)

    if settings.SECURITY_HEADERS_ENABLED:
        app.add_middleware(SecurityHeadersMiddleware)

    if settings.RATE_LIMIT_ENABLED:
        rate_limit_store = (
            RedisRateLimitStore(settings.RATE_LIMIT_REDIS_URL, settings.RATE_LIMIT_REDIS_PREFIX)
            if settings.RATE_LIMIT_BACKEND == "redis"
            else MemoryRateLimitStore()
        )
        app.add_middleware(
            RateLimitMiddleware,
            store=rate_limit_store,
            default_policy=RateLimitPolicy(
                "default",
                settings.RATE_LIMIT_REQUESTS,
                settings.RATE_LIMIT_WINDOW_SECONDS,
            ),
            login_policy=RateLimitPolicy(
                "login",
                settings.RATE_LIMIT_LOGIN_REQUESTS,
                settings.RATE_LIMIT_LOGIN_WINDOW_SECONDS,
            ),
            public_report_policy=RateLimitPolicy(
                "public_report",
                settings.RATE_LIMIT_PUBLIC_REPORT_REQUESTS,
                settings.RATE_LIMIT_PUBLIC_REPORT_WINDOW_SECONDS,
            ),
            upload_policy=RateLimitPolicy(
                "upload",
                settings.RATE_LIMIT_UPLOAD_REQUESTS,
                settings.RATE_LIMIT_UPLOAD_WINDOW_SECONDS,
            ),
        )

    upload_dir = Path(settings.UPLOAD_DIR).resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)

    for carpeta in settings.UPLOAD_SUBDIRS:
        (upload_dir / carpeta).mkdir(parents=True, exist_ok=True)

    app.add_middleware(AuditMiddleware)

    # Seguridad
    app.include_router(auth.router)
    app.include_router(archivos_protegidos.router)
    app.include_router(usuarios_sistema.router)
    app.include_router(roles.router)
    app.include_router(permisos.router)
    app.include_router(auditoria.router)
    app.include_router(configuracion_sistema.router)
    app.include_router(observabilidad.router)

    # Administración empresarial
    app.include_router(empresas.router)
    app.include_router(sedes.router)
    app.include_router(areas.router)
    app.include_router(cargos.router)
    app.include_router(empleados.router)
    app.include_router(relation_guard.router)

    # PLANEAR / HACER / VERIFICAR / ACTUAR
    app.include_router(politica_sst.router)
    app.include_router(objetivos_sst.router)
    app.include_router(evaluacion_inicial.router)
    app.include_router(matriz_legal.router)
    app.include_router(matriz_peligros.router)
    app.include_router(plan_anual.router)
    app.include_router(capacitaciones.router)
    app.include_router(capacitacion_asistentes.router)
    app.include_router(capacitacion_certificados.router)
    app.include_router(examenes_medicos.router)
    app.include_router(epp.router)
    app.include_router(inspecciones.router)
    app.include_router(inspeccion_seguimientos.router)
    app.include_router(inspecciones_exportaciones.router)
    app.include_router(inspecciones_exportaciones_platinum.router)
    app.include_router(capa.router)
    app.include_router(incidentes.router)
    app.include_router(indicadores_sst.router)
    app.include_router(notificaciones_sst.router)
    app.include_router(plan_mejoramiento.router)
    app.include_router(plan_mejoramiento_evidencias.router)
    app.include_router(plan_mejoramiento_seguimientos.router)
    app.include_router(medidas_correctivas.router)
    app.include_router(medidas_correctivas_bi.router)
    app.include_router(medidas_correctivas_exportaciones.router)
    app.include_router(alertas_medidas_correctivas.router)
    app.include_router(medidas_evidencias_inteligentes.router)

    # Auditoría y revisión
    app.include_router(auditoria_sst.router)
    app.include_router(auditoria_pdf.router)
    app.include_router(auditoria_hallazgo_evidencias.router)
    app.include_router(auditoria_evidencias.router)
    app.include_router(revision_direccion.router)
    app.include_router(revision_direccion_pdf.router)
    app.include_router(revision_version.router)

    # Gestión documental
    app.include_router(archivos_sst.router)
    app.include_router(configuracion_documental.router)
    app.include_router(biblioteca_documental.router)
    app.include_router(firmas_digitales.router)
    app.include_router(documento_validacion.router)
    app.include_router(documentos_versiones.router)
    app.include_router(dashboard_documental.router)
    app.include_router(documental_enterprise.router)
    app.include_router(firma_documental.router)

    # Portal público y reportes
    app.include_router(portal_empleado.router)
    app.include_router(reporte_anonimo_sst.router)
    app.include_router(reportes_anonimos_admin.router)
    app.include_router(reporte_evidencias.router)

    # Exportaciones y dashboards
    app.include_router(exportaciones_sst.router)
    app.include_router(indicadores_bi.router)
    app.include_router(dashboard.router)
    app.include_router(dashboard_saas.router)
    app.include_router(dashboard_ejecutivo.router)
    app.include_router(dashboard_sst.router)

    @app.get("/", tags=["Sistema"])
    def inicio():
        return {
            "mensaje": "ERP SST PRO funcionando correctamente",
            "entorno": "Logging Enterprise y Manejo de Errores",
            "version": settings.APP_VERSION,
            "uploads_url": "/uploads",
            "auto_create_tables": settings.AUTO_CREATE_TABLES,
        }

    @app.get("/health", tags=["Sistema"])
    def healthcheck():
        return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION, "logging": "enabled"}

    return app


app = create_app()

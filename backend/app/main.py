from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base

# Modelos base
from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.usuario import Usuario
from app.models.empleado import Empleado

# Administración empresarial
from app.models.area import Area
from app.models.cargo import Cargo

# Seguridad
from app.models.rol import Rol
from app.models.permiso import Permiso
from app.models.usuario_permiso import UsuarioPermiso
from app.models.auditoria import Auditoria
from app.models.login_intento import LoginIntento

# PLANEAR SG-SST
from app.models.politica_sst import PoliticaSST
from app.models.objetivo_sst import ObjetivoSST
from app.models.evaluacion_inicial import EvaluacionInicialSST, EvaluacionInicialItemSST
from app.models.matriz_legal import MatrizLegalSST
from app.models.matriz_peligros import MatrizPeligrosSST
from app.models.plan_anual import PlanAnualSST
from app.models.plan_mejoramiento import PlanMejoramientoSST



# HACER| Capacitaciones SST PRO Enterprise
from app.models.capacitacion import CapacitacionSST, CapacitacionAsistenteSST
from app.models.capacitacion_certificado import CapacitacionCertificado 
from app.models.examen_medico import ExamenMedico
from app.models.epp import EPPCatalogo, EPPEntrega

# HACER| Inspecciones SST PRO Enterprise
from app.models.inspeccion import InspeccionSST, InspeccionHallazgoSST
from app.models.inspeccion_seguimiento import InspeccionHallazgoSeguimientoSST 
from app.models.capa import CapaSST, CapaSeguimientoSST

from app.models.plan_mejoramiento_evidencia import PlanMejoramientoEvidenciaSST
from app.models.plan_mejoramiento_seguimiento import PlanMejoramientoSeguimientoSST

from app.models.auditoria_sst import AuditoriaSST, AuditoriaHallazgoSST

from app.models.auditoria_hallazgo_evidencia import AuditoriaHallazgoEvidenciaSST
from app.models.firma_digital import FirmaDigitalSST

from app.models.revision_direccion import RevisionDireccionSST, RevisionDireccionCompromisoSST
from app.models.indicador_sst import IndicadorSST
from app.models.notificacion_sst import NotificacionSST, ConfiguracionNotificacionSST
from app.models.reporte_inseguridad import ReporteInseguridadSST




# Gestión documental
from app.models.archivo_sst import ArchivoSST
from app.models.configuracion_documental import ConfiguracionDocumental
from app.models.biblioteca_documental import BibliotecaDocumental
from app.models.documento_validacion import DocumentoValidacionSST
from app.models.revision_version import RevisionDireccionVersionSST
from app.models.documento_version import DocumentoVersion
from app.models.firma_documental_sst import FirmaDocumentalSST
from app.models.configuracion_sistema import ConfiguracionSistema
from app.models.alerta_medida_correctiva import AlertaMedidaCorrectivaSST




# Routers
from app.routers import (
    auth,
    usuarios_sistema,
    roles,
    permisos,
    auditoria,
    revision_direccion_pdf,
    empresas,
    sedes,
    areas,
    cargos,
    empleados,
    dashboard,
    dashboard_saas,
    dashboard_ejecutivo,
    dashboard_sst,
    politica_sst,
    objetivos_sst,
    archivos_sst,
    configuracion_documental,
    exportaciones_sst,
    biblioteca_documental,
    evaluacion_inicial,
    matriz_legal,
    matriz_peligros,
    plan_anual,
    capacitaciones,
    examenes_medicos,
    epp,
    inspecciones,
    capacitacion_asistentes,
    capacitacion_certificados,
    plan_mejoramiento,
    plan_mejoramiento_evidencias,
    plan_mejoramiento_seguimientos,
    auditoria_sst,
    auditoria_pdf,
    auditoria_hallazgo_evidencias,
    firmas_digitales,
    documento_validacion,
    revision_direccion,
    revision_version,
    documentos_versiones,
    dashboard_documental,
    documental_enterprise,
    firma_documental,
    inspeccion_seguimientos,
    capa,
    incidentes,
    indicadores_sst,
    notificaciones_sst,
    indicadores_bi,
    portal_empleado,
    reporte_anonimo_sst,
    reportes_anonimos_admin,
    reporte_evidencias,
    auditoria_evidencias,
    configuracion_sistema,
    medidas_correctivas,
    alertas_medidas_correctivas,
    medidas_evidencias_inteligentes,
    medidas_correctivas_exportaciones,  
    inspecciones_exportaciones_platinum,
)

from app.middlewares.audit_middleware import AuditMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ERP SST PRO",
    description="Sistema de Gestión de Seguridad y Salud en el Trabajo - Colombia",
    version="2.7.4",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

for carpeta in [
    "logos",
    "firmas",
    "documentos",
    "evidencias",
    "actas",
    "capacitaciones",
    "examenes-medicos",
    "certificados",
    "auditorias",
    "inspecciones",
]:
    (UPLOAD_DIR / carpeta).mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

app.add_middleware(AuditMiddleware)

# Seguridad
app.include_router(auth.router)
app.include_router(usuarios_sistema.router)
app.include_router(roles.router)
app.include_router(permisos.router)
app.include_router(auditoria.router)
app.include_router(configuracion_sistema.router)
app.include_router(medidas_correctivas.router)
app.include_router(alertas_medidas_correctivas.router)
app.include_router(medidas_evidencias_inteligentes.router)
app.include_router(inspecciones_exportaciones_platinum.router)


# Administración empresarial
app.include_router(empresas.router)
app.include_router(sedes.router)
app.include_router(areas.router)
app.include_router(cargos.router)
app.include_router(empleados.router)

# PLANEAR SG-SST
app.include_router(politica_sst.router)
app.include_router(objetivos_sst.router)
app.include_router(evaluacion_inicial.router)
app.include_router(matriz_legal.router)
app.include_router(matriz_peligros.router)
app.include_router(plan_anual.router)
app.include_router(capacitaciones.router)
app.include_router(examenes_medicos.router)
app.include_router(epp.router)
app.include_router(inspecciones.router)
app.include_router(inspeccion_seguimientos.router)
app.include_router(capa.router)
app.include_router(incidentes.router)
app.include_router(indicadores_sst.router)
app.include_router(notificaciones_sst.router)
app.include_router(capacitacion_asistentes.router)
app.include_router(capacitacion_certificados.router)
app.include_router(auditoria_sst.router)
app.include_router(auditoria_pdf.router)
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
# Exportaciones corporativas
app.include_router(exportaciones_sst.router)
app.include_router(indicadores_bi.router)
app.include_router(portal_empleado.router)
app.include_router(reporte_anonimo_sst.router)
app.include_router(reportes_anonimos_admin.router)
app.include_router(reporte_evidencias.router)
app.include_router(auditoria_evidencias.router)
# Dashboards
app.include_router(dashboard.router)
app.include_router(dashboard_saas.router)
app.include_router(dashboard_ejecutivo.router)
app.include_router(dashboard_sst.router)
app.include_router(plan_mejoramiento.router)
app.include_router(plan_mejoramiento_evidencias.router)
app.include_router(plan_mejoramiento_seguimientos.router)
app.include_router(auditoria_hallazgo_evidencias.router)
app.include_router(revision_direccion.router)
app.include_router(revision_direccion_pdf.router)
app.include_router(revision_version.router)
app.include_router(medidas_correctivas_exportaciones.router)  # FASE 1.1.8.7.6.1 - PDF/Excel Medidas Correctivas
@app.get("/")
def inicio():
    return {
        "mensaje": "ERP SST PRO funcionando correctamente",
        "fase": "FASE 1.1.24.1 - Centro de Notificaciones Inteligentes SST Enterprise",
        "version": "1.1.24.1",
        "uploads_url": "/uploads",
    }

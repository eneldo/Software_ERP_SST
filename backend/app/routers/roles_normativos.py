# ============================================================
# H-013c: MATRIZ DE ROLES NORMATIVOS
# Mapping de roles del sistema a responsabilidades Decreto 1072/2015
# ============================================================

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/roles", tags=["H-013c: Matriz Roles Normativos"])

MATRIZ_ROLES = {
    "SUPER_ADMIN": {
        "nombre": "Super Administrador",
        "descripcion": "Administrador técnico del sistema multi-empresa",
        "empresa_requerida": False,
        "acceso_global": True,
        "normatividad": [],
        "responsabilidades": [
            "Administración técnica de la plataforma ERP",
            "Gestión de empresas (tenants)",
            "Configuración global del sistema",
        ],
        "permisos_especiales": ["all"],
    },
    "ADMIN_EMPRESA": {
        "nombre": "Administrador de Empresa",
        "descripcion": "Administrador principal de una empresa específica",
        "empresa_requerida": True,
        "acceso_global": False,
        "normatividad": [
            "Art. 2.2.1 Decreto 1072/2015 — Obligaciones del empleador",
        ],
        "responsabilidades": [
            "Administración total de usuarios de su empresa",
            "Configuración de parámetros SST",
            "Asignación de responsables SST",
            "Aprobación final de políticas y planes",
        ],
        "permisos_especiales": ["EMPRESA_FULL"],
    },
    "RESPONSABLE_SST": {
        "nombre": "Responsable del SG-SST",
        "descripcion": "Profesional SST designado por el empleador",
        "empresa_requerida": True,
        "acceso_global": False,
        "normatividad": [
            "Art. 2.2.1 Decreto 1072/2015 — Designación del responsable del SG-SST",
            "Numeral 3 Resolución 1843/2025 — Funciones del responsable del SG-SST",
            "Art. 2.2.8 Decreto 1072/2015 — Coordinación del SG-SST",
        ],
        "responsabilidades": [
            "Diseño, implementación y mejora continua del SG-SST",
            "Coordinación de la políticas de seguridad y salud en el trabajo",
            "Liderazgo del proceso de gestión del riesgo",
            "Coordinación de la capacitación SST",
            "Elaboración del plan anual de trabajo",
            "Seguimiento y medición del SG-SST",
        ],
        "permisos_especiales": [
            "POLITICAS_SST",
            "PLAN_ANUAL",
            "CAPACITACIONES",
            "ESTANDARES_CRITERIOS",
            "EMERGENCIAS_SST",
            "COMITES_SST",
            "HISTORIAL_LEGAL",
        ],
    },
    "COORDINADOR_SST": {
        "nombre": "Coordinador SST",
        "descripcion": "Coordina actividades SST hereda funciones de responsable SST",
        "empresa_requerida": True,
        "acceso_global": False,
        "normatividad": [
            "Art. 2.2.8 Decreto 1072/2015 — Funciones del coordinador del SG-SST",
        ],
        "responsabilidades": [
            "Coordinar la ejecución de actividades SST",
            "Supervisar el cumplimiento de las normas SST",
            "Apoyar al responsable SST en funciones",
        ],
        "permisos_especiales": [
            "POLITICAS_SST",
            "PLAN_ANUAL",
            "CAPACITACIONES",
            "ESTANDARES_CRITERIOS",
            "EMERGENCIAS_SST",
        ],
    },
    "AUDITOR_INT": {
        "nombre": "Auditor Interno SG-SST",
        "descripcion": "Audita el sistema de gestión de manera interna",
        "empresa_requerida": True,
        "acceso_global": False,
        "normatividad": [
            "Numeral 6 Resolución 1843/2025 — Requisitos del programa de auditoría interna",
            "Art. 2.2.9 Decreto 1072/2015 — Auditoría interna del SG-SST",
        ],
        "responsabilidades": [
            "Planificar y ejecutar auditorías internas",
            "Generar informes de hallazgos y no conformidades",
            "Dar seguimiento a acciones correctivas",
        ],
        "permisos_especiales": [
            "AUDITORIA_SST",
            "ACCIONES_CORRECTIVAS",
        ],
    },
    "AUDITOR_EXT": {
        "nombre": "Auditor Externo",
        "descripcion": "Auditor externo o de certificación",
        "empresa_requerida": True,
        "acceso_global": False,
        "normatividad": [
            "Numeral 6 Resolución 1843/2025 — Auditoría externa",
        ],
        "responsabilidades": [
            "Auditoría de certificación del SG-SST",
            "Emisión de recomendaciones externas",
        ],
        "permisos_especiales": [
            "AUDITORIA_SST_READ",
        ],
    },
    "MEDICO": {
        "nombre": "Médico Laboral",
        "descripcion": "Profesional de salud que presta servicios a la empresa",
        "empresa_requerida": True,
        "acceso_global": False,
        "normatividad": [
            "Resolución 2346/2023 — Procedimientos de medicina del trabajo",
            "Art. 2.2.2 Decreto 1072/2015 — Servicios de salud ocupacional",
        ],
        "responsabilidades": [
            "Evaluaciones médicas de ingreso, periódicas y de retiro",
            "Clasificación de factores de riesgo ocupacional",
            "Pronóstico de aptitud para el trabajo",
            "Vigilancia epidemiológica",
        ],
        "permisos_especiales": [
            "EXAMENES_MEDICOS",
            "HISTORIA_CLINICA_WRITE",
        ],
    },
    "ENFERMERA": {
        "nombre": "Enfermera(o) Laboral",
        "descripcion": "Profesional de enfermería en salud ocupacional",
        "empresa_requerida": True,
        "acceso_global": False,
        "normatividad": [
            "Art. 2.2.2 Decreto 1072/2015 — Servicios de salud ocupacional",
        ],
        "responsabilidades": [
            "Primeros auxilios y atención de emergencias",
            "Promoción de la salud en el trabajo",
            "Apoyo en vigilancia epidemiológica",
        ],
        "permisos_especiales": [
            "PRIMEROS_AUXILIOS",
        ],
    },
    "VIGIA": {
        "nombre": "Vigía SST",
        "descripcion": "Trabajador capacitado para vigilancia básica en SST",
        "empresa_requerida": True,
        "acceso_global": False,
        "normatividad": [
            "Art. 2.2.6 Decreto 1072/2015 — Comité de Convivencia Laboral",
        ],
        "responsabilidades": [
            "Vigilancia básica de SST en área asignada",
            "Identificación de condiciones de riesgo",
            "Primeros auxilios básicos",
        ],
        "permisos_especiales": [
            "VIGILANCIA_BASICA",
        ],
    },
    "COPASST": {
        "nombre": "Comité Paritario SST (COPASST)",
        "descripcion": "Miembro del Comité Paritario de Seguridad y Salud en el Trabajo",
        "empresa_requerida": True,
        "acceso_global": False,
        "normatividad": [
            "Art. 2.2.6 Decreto 1072/2015 — Comité Paritario de Seguridad y Salud en el Trabajo",
            "Numeral 4 Resolución 1843/2025 — Funciones del COPASST",
        ],
        "responsabilidades": [
            "Participar en la investigación de accidentes",
            "Proponer mejoras en condiciones de trabajo",
            "Velocidad en la promoción de la cultura SST",
            "Realizar visitas de verificación",
            "Participar en el plan anual de trabajo",
        ],
        "permisos_especiales": [
            "COMITES_SST",
            "INVESTIGACION_ACCIDENTES",
        ],
    },
    "CONTADOR": {
        "nombre": "Contador / Area Financiera",
        "descripcion": "Responsable de la gestión contable y financiera",
        "empresa_requerida": True,
        "acceso_global": False,
        "normatividad": [],
        "responsabilidades": [
            "Gestión de facturación y pagos",
            "Reportes financieros",
            "Cumplimiento de obligaciones tributarias",
        ],
        "permisos_especiales": [
            "FACTURACION",
            "PAGOS",
            "REPORTES_FINANCIEROS",
        ],
    },
    "ALMACENERO": {
        "nombre": "Almacenero / Logística",
        "descripcion": "Gestión de inventarios y almacén",
        "empresa_requerida": True,
        "acceso_global": False,
        "normatividad": [],
        "responsabilidades": [
            "Gestión de inventarios",
            "Control de almacén y distribución",
        ],
        "permisos_especiales": [
            "INVENTARIOS",
            "ALMACEN",
        ],
    },
    "JEFE_PLANTA": {
        "nombre": "Jefe de Planta",
        "descripcion": "Responsable de la operación de planta",
        "empresa_requerida": True,
        "acceso_global": False,
        "normatividad": [
            "Art. 2.2.1 Decreto 1072/2015 — Obligaciones del empleador (parcial)",
        ],
        "responsabilidades": [
            "Supervisión operativa de la planta",
            "Cumplimiento de normas SST en operación",
        ],
        "permisos_especiales": [
            "OPERACION_PLANTA",
        ],
    },
    "JEFE_AREA": {
        "nombre": "Jefe de Área",
        "descripcion": "Responsable de un área específica",
        "empresa_requerida": True,
        "acceso_global": False,
        "normatividad": [],
        "responsabilidades": [
            "Supervisión de área",
            "Reporte de incidentes y accidentes",
        ],
        "permisos_especiales": [
            "SUPERVIS_AREA",
        ],
    },
    "OPERARIO": {
        "nombre": "Operario / Trabajador",
        "descripcion": "Trabajador operativo de la empresa",
        "empresa_requerida": True,
        "acceso_global": False,
        "normatividad": [
            "Art. 2.2.4 Decreto 1072/2015 — Obligaciones de los trabajadores",
        ],
        "responsabilidades": [
            "Cumplir las normas de higiene y seguridad industrial",
            "Reportar situaciones de riesgo",
            "Uso correcto de EPP",
        ],
        "permisos_especiales": [
            "REPORTES_BASICOS",
        ],
    },
    "APRENDIZ": {
        "nombre": "Aprendiz en Formación",
        "descripcion": "Aprendiz SENA o similar en formación",
        "empresa_requerida": True,
        "acceso_global": False,
        "normatividad": [
            "Art. 2.2.4 Decreto 1072/2015 — Obligaciones de los trabajadores (aplicable)",
        ],
        "responsabilidades": [
            "Cumplir normas SST bajo supervisión",
            "Reportar condiciones de riesgo",
        ],
        "permisos_especiales": [
            "REPORTES_BASICOS",
        ],
    },
}


@router.get("/matriz")
def obtener_matriz_roles(usuario: Usuario = Depends(get_current_user)):
    return MATRIZ_ROLES


@router.get("/matriz/{rol}")
def obtener_rol(rol: str, usuario: Usuario = Depends(get_current_user)):
    rol_upper = rol.upper()
    if rol_upper not in MATRIZ_ROLES:
        return {"error": f"Rol '{rol}' no encontrado en la matriz normativa"}
    return {"rol": rol_upper, **MATRIZ_ROLES[rol_upper]}


@router.get("/normatividad")
def obtener_normatividad_completa(usuario: Usuario = Depends(get_current_user)):
    normatividad = {}
    for rol, info in MATRIZ_ROLES.items():
        normatividad[rol] = {
            "nombre": info["nombre"],
            "normatividad": info["normatividad"],
        }
    return normatividad

# ============================================================
# ERP SST COLOMBIA
# SERVICIO: CRITERIOS BASE EVALUACIÓN INICIAL SG-SST
# Resolución 0312 de 2019
# ============================================================


def obtener_criterios_evaluacion(tipo_estandares: str | int):
    tipo = str(tipo_estandares or "7").strip()

    if tipo == "3":
        return CRITERIOS_3

    if tipo == "7":
        return CRITERIOS_7

    if tipo == "21":
        return CRITERIOS_21

    return CRITERIOS_60


CRITERIOS_3 = [
    {
        "estandar": "Recursos",
        "numeral": "1.1.1",
        "criterio": "Asignar una persona responsable del SG-SST.",
        "puntaje": 1,
    },
    {
        "estandar": "Gestión de peligros y riesgos",
        "numeral": "4.1.1",
        "criterio": "Identificar peligros, evaluar y valorar los riesgos.",
        "puntaje": 1,
    },
    {
        "estandar": "Plan anual",
        "numeral": "2.4.1",
        "criterio": "Ejecutar actividades básicas de prevención y promoción en SST.",
        "puntaje": 1,
    },
]


CRITERIOS_7 = [
    {
        "estandar": "Responsable SG-SST",
        "numeral": "1.1.1",
        "criterio": "Asignar una persona responsable del Sistema de Gestión de SST.",
        "puntaje": 1,
    },
    {
        "estandar": "Afiliación Seguridad Social",
        "numeral": "1.1.4",
        "criterio": "Afiliar a los trabajadores al Sistema de Seguridad Social Integral.",
        "puntaje": 1,
    },
    {
        "estandar": "Capacitación SST",
        "numeral": "1.2.1",
        "criterio": "Desarrollar actividades de capacitación en Seguridad y Salud en el Trabajo.",
        "puntaje": 1,
    },
    {
        "estandar": "Plan Anual SST",
        "numeral": "2.4.1",
        "criterio": "Elaborar y ejecutar el Plan Anual de Trabajo del SG-SST.",
        "puntaje": 1,
    },
    {
        "estandar": "Evaluaciones Médicas",
        "numeral": "3.1.1",
        "criterio": "Realizar evaluaciones médicas ocupacionales según corresponda.",
        "puntaje": 1,
    },
    {
        "estandar": "Identificación de Peligros",
        "numeral": "4.1.1",
        "criterio": "Identificar peligros, evaluar y valorar riesgos.",
        "puntaje": 1,
    },
    {
        "estandar": "Medidas de Prevención",
        "numeral": "4.2.1",
        "criterio": "Implementar medidas de prevención y control frente a los riesgos identificados.",
        "puntaje": 1,
    },
]


CRITERIOS_21 = CRITERIOS_7 + [
    {
        "estandar": "Asignación de Recursos",
        "numeral": "1.1.3",
        "criterio": "Asignar recursos financieros, técnicos, físicos y humanos para el SG-SST.",
        "puntaje": 1,
    },
    {
        "estandar": "COPASST / Vigía SST",
        "numeral": "1.1.6",
        "criterio": "Conformar COPASST o designar Vigía SST según aplique.",
        "puntaje": 1,
    },
    {
        "estandar": "Comité de Convivencia",
        "numeral": "1.1.8",
        "criterio": "Conformar el Comité de Convivencia Laboral según corresponda.",
        "puntaje": 1,
    },
    {
        "estandar": "Política SST",
        "numeral": "2.1.1",
        "criterio": "Contar con política SST documentada, firmada, fechada y comunicada.",
        "puntaje": 1,
    },
    {
        "estandar": "Objetivos SST",
        "numeral": "2.2.1",
        "criterio": "Definir objetivos SST medibles, claros y coherentes con la política.",
        "puntaje": 1,
    },
    {
        "estandar": "Evaluación Inicial",
        "numeral": "2.3.1",
        "criterio": "Realizar evaluación inicial del SG-SST.",
        "puntaje": 1,
    },
    {
        "estandar": "Archivo Documental",
        "numeral": "2.5.1",
        "criterio": "Conservar la documentación del SG-SST.",
        "puntaje": 1,
    },
    {
        "estandar": "Rendición de Cuentas",
        "numeral": "2.6.1",
        "criterio": "Realizar rendición de cuentas del desempeño del SG-SST.",
        "puntaje": 1,
    },
    {
        "estandar": "Matriz Legal",
        "numeral": "2.7.1",
        "criterio": "Identificar la normatividad legal vigente aplicable en SST.",
        "puntaje": 1,
    },
    {
        "estandar": "Comunicación SST",
        "numeral": "2.8.1",
        "criterio": "Establecer mecanismos de comunicación y autoreporte en SST.",
        "puntaje": 1,
    },
    {
        "estandar": "Condiciones de Salud",
        "numeral": "3.1.1",
        "criterio": "Contar con diagnóstico de condiciones de salud y perfil sociodemográfico.",
        "puntaje": 1,
    },
    {
        "estandar": "Investigación de Incidentes",
        "numeral": "3.2.1",
        "criterio": "Investigar incidentes, accidentes y enfermedades laborales.",
        "puntaje": 1,
    },
    {
        "estandar": "Mediciones Ambientales",
        "numeral": "3.3.1",
        "criterio": "Realizar mediciones ambientales cuando aplique.",
        "puntaje": 1,
    },
    {
        "estandar": "Plan de Emergencias",
        "numeral": "5.1.1",
        "criterio": "Contar con plan de prevención, preparación y respuesta ante emergencias.",
        "puntaje": 1,
    },
]


CRITERIOS_60 = CRITERIOS_21 + [
    {
        "estandar": f"Estándar completo SG-SST",
        "numeral": f"60.{i}",
        "criterio": f"Criterio complementario SG-SST número {i} aplicable a empresas de más de 50 trabajadores o riesgo IV/V.",
        "puntaje": 1,
    }
    for i in range(22, 61)
]
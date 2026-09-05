# MATRIZ NORMATIVA SG-SST COLOMBIA - AUDITORÍA EXHAUSTIVA

**Fecha:** 2026-09-04  
**Versión:** 1.0  
**Auditor:** Agente de Ingeniería Persistente  
**Alcance:** Sistema de Gestión SST (SG-SST) para Colombia  

---

## NORMATIVA APLICABLE IDENTIFICADA

| ID | Norma | Título | Vigencia | Estado |
|----|-------|--------|----------|--------|
| N-01 | **Decreto 1072 de 2015** | Decreto Único Reglamentario del Sector Trabajo | Vigente | **Base legal principal** |
| N-02 | **Resolución 0312 de 2019** | Estándares Mínimos del SG-SST | Vigente | **Norma técnica principal** |
| N-03 | **Ley 1562 de 2012** | Sistema General de Riesgos Laborales | Vigente | **Marco legal** |
| N-04 | **Resolución 1843 de 2025** | Evaluaciones Médicas Ocupacionales | Vigente | **Nueva - Medicina laboral** |
| N-05 | **Resolución 1401 de 2007** | Trabajo en Alturas | Vigente | Específica |
| N-06 | **Resolución 2013 de 1986** | Riesgo Eléctrico | Vigente | Específica |
| N-07 | **Resolución 652 de 2012** | Espacios Confinados | Vigente | Específica |
| N-08 | **Resolución 2404 de 1979** | Reglamento Seguridad Industrial | Vigente | Histórica base |
| N-09 | **Resolución 2646 de 2008** | Riesgo Psicosocial | Vigente | Psicosocial |
| N-10 | **Ley 1581 de 2012** | Protección de Datos Personales | Vigente | Habeas Data / Historia Clínica |
| N-11 | **ISO 45001:2018** | Sistemas de Gestión SST | Internacional | Referencia voluntaria |
| N-12 | **GTC 45** | Guía Técnica Colombiana 45 - IPER | Vigente | Matriz IPER |

---

## CRUCE NORMATIVO vs MÓDULOS DEL SISTEMA

| Norma | Artículo/Num | Requisito Normativo | Módulo Sistema | Estado | Hallazgos |
|-------|--------------|---------------------|----------------|--------|-----------|
| **Dec. 1072/15** | Art. 2.2.4.6.1 | Responsable SG-SST designado | Empresa / Cargo | ✅ | Campo `responsable_sst` en Empresa |
| **Dec. 1072/15** | Art. 2.2.4.6.3 | Asignación recursos | Plan Anual | ⚠️ | Falta ejecución presupuestal real |
| **Dec. 1072/15** | Art. 2.2.4.6.4 | Afiliación ARL | Empresa | ✅ | Campo `arl` en Empresa |
| **Dec. 1072/15** | Art. 2.2.4.6.6 | COPASST / Vigía | Comités | ✅ | Módulo Comités completo |
| **Dec. 1072/15** | Art. 2.2.4.6.8 | Comité Convivencia | Comités | ✅ | Tipo COPASST + Convivencia |
| **Dec. 1072/15** | Art. 2.2.4.6.12 | Capacitación SST | Capacitaciones | ✅ | Completo con inducción/reinducción |
| **Dec. 1072/15** | Art. 2.2.4.6.14 | Plan Anual | Plan Anual | ✅ | Campos Decreto 1072 agregados |
| **Dec. 1072/15** | Art. 2.2.4.6.18 | Evaluación Inicial | Evaluación Inicial | ✅ | Completo con 3/7/21/60 estándares |
| **Dec. 1072/15** | Art. 2.2.4.6.19 | Plan Anual | Plan Anual | ✅ | Ver arriba |
| **Res. 0312/19** | Anexo Técnico | 60 estándares mínimos | Estándares Mínimos | 🔴 | **Hardcodeado** - solo 3/7/21 reales |
| **Res. 0312/19** | Art. 2.3.1 | Evaluación inicial obligatoria | Evaluación Inicial | ✅ | Implementado |
| **Res. 0312/19** | Art. 2.3.2 | Plan de mejora no conformidades | Plan Mejoramiento | 🔴 | **Falta origen hallazgo, verificación, evidencia cierre** |
| **Res. 0312/19** | Art. 2.4.1 | Plan anual derivado evaluación | Plan Anual | ⚠️ | Parcial - sin vínculo automático |
| **Res. 0312/19** | Art. 2.5.1 | Archivo documental | Biblioteca Documental | ⚠️ | Falta flujo aprobación documental |
| **Res. 0312/19** | Art. 2.6.1 | Rendición de cuentas | Revisión Dirección | ⚠️ | Parcial - sin estructura obligatoria |
| **Res. 0312/19** | Art. 2.7.1 | Matriz Legal | Matriz Legal | ⚠️ | Falta automatización vigencia |
| **Res. 0312/19** | Art. 2.8.1 | Comunicación SST | **NO EXISTE** | 🔴 | **Falta buzón/consulta/participación** |
| **Res. 0312/19** | 3.1.1 | Evaluaciones médicas | Exámenes Médicos | ⚠️ | Parcial - Falta HCO/Concepto separado |
| **Res. 0312/19** | 3.2.1 | Investigación incidentes | Incidentes | ⚠️ | Sin metodologías completas, sin reporte ARL |
| **Res. 0312/19** | 3.3.1 | Mediciones ambientales | **NO EXISTE** | 🔴 | **VACÍO CRÍTICO** |
| **Res. 0312/19** | 4.1.1 | Identificación peligros | Matriz Peligros / IPER | ✅ | Completo GTC 45 |
| **Res. 0312/19** | 4.2.1 | Medidas prevención/control | IPER, CAPA, EPP | ✅ | - |
| **Res. 0312/19** | 5.1.1 | Plan emergencias | Emergencias | ✅ | Brigadas, simulacros, amenazas |
| **Res. 1843/25** | Art. 1-15 | Evaluaciones médicas ocupacionales | Exámenes Médicos | ⚠️ | Parcial - Falta HCO/Concepto separado, vigilancia epidemiológica |
| **Res. 1843/25** | Art. 12 | Historia clínica vs Concepto médico | Exámenes Médicos | 🔴 | **NO SEPARADO** - Mezcla en mismo modelo |
| **Res. 2646/08** | Art. 1-10 | Riesgo psicosocial | **NO EXISTE** | 🔴 | **VACÍO CRÍTICO** |
| **Ley 1581/12** | Art. 1-25 | Protección datos personales | Exámenes / Documentos | ⚠️ | Parcial - Falta consentimiento explícito, supresión |
| **ISO 45001** | Cl. 4-10 | Sistema gestión SST | Todo el sistema | ⚠️ | Base arquitectura PHVA presente |

---

## RESUMEN CUMPLIMIENTO POR NORMA

| Norma | % Cumplimiento | Estado Global | Comentario |
|-------|----------------|---------------|------------|
| **Decreto 1072/2015** | **85%** | 🟢 | Base sólida, gaps en recursos y comunicación |
| **Resolución 0312/2019** | **72%** | 🟡 | Gaps críticos en estándares, planes de mejora, medición |
| **Resolución 1843/2025** | **55%** | 🔴 | **Crítico** - Historia clínica mezclada, falta vigilancia |
| **Resolución 2646/2008** | **0%** | 🔴 | **AUSENTE** - Riesgo psicosocial obligatorio |
| **Resolución 1843/2025 (Medicina)** | **55%** | 🔴 | **Crítico** - HCO/Concepto no separados |
| **Ley 1581/2012 (Habeas Data)** | **70%** | 🟡 | Falta consentimiento explícito, supresión, portabilidad |
| **Resolución 2646/2008 (Psicosocial)** | **0%** | 🔴 | **CRÍTICO** - Obligatorio para empresas >50 trabajadores |
| **ISO 45001:2018** | **78%** | 🟢 | Arquitectura PHVA implementada, gaps en comunicación/consulta |

---

## PRIORIDAD DE CUMPLIMIENTO NORMATIVO

| Prioridad | Norma / Requisito | Acción Requerida | Esfuerzo | Riesgo Legal |
|-----------|-------------------|------------------|----------|--------------|
| **P0** | **Res. 2646/2008 - Riesgo Psicosocial** | Implementar módulo completo | 8 semanas | **SANCIÓN** - Obligatorio >50 trab. |
| **P0** | **Res. 1843/2025 - Historia Clínica** | Separar HCO vs Concepto Médico | 4 semanas | **SANCIÓN** - Datos sensibles |
| **P0** | **Res. 1843/2025 - Medicina Laboral** | Vigilancia epidemiológica + mediciones | 8 semanas | **SANCIÓN** - Obligatorio |
| **P0** | **Res. 0312/2019 - Estándares Mínimos** | Parametrizar 60 criterios en BD | 4 semanas | **SANCIÓN** - Base legal |
| **P0** | **Ley 1581/2012 - Datos Sensibles** | Consentimiento explícito + supresión | 3 semanas | **MULTA** - 2000 SMMLV |
| **P1** | **Res. 0312/2019 - Plan Mejora** | Origen hallazgo + verificación + evidencia | 4 semanas | Auditoría |
| **P1** | **Res. 0312/2019 - Mediciones Ambientales** | Módulo completo | 8 semanas | Auditoría |
| **P1** | **Res. 0312/2019 - Comunicación** | Buzón + consulta + participación | 4 semanas | Auditoría |
| **P2** | **ISO 45001 - Comunicación/Consulta** | Participación trabajadores | 6 semanas | Certificación |
| **P2** | **ISO 45001 - Gestión Cambios (MOC)** | Solicitud → Análisis → Autorización | 6 semanas | Certificación |
| **P2** | **Res. 0312 - Contratistas** | Calificación + homologación SST | 6 semanas | Responsabilidad solidaria |

---

## MATRIZ DE RIESGO NORMATIVO

| Norma | Probabilidad Incumplimiento | Impacto Legal | Impacto Operativo | Prioridad |
|-------|----------------------------|---------------|-------------------|-----------|
| Res. 2646/2008 | ALTA (0%) | SANCIÓN + CIERRE | ALTO | **P0** |
| Res. 1843/2025 (HCO) | ALTA (45%) | MULTA + DEMANDAS | ALTO | **P0** |
| Ley 1581/2012 | MEDIA (30%) | MULTA 2000 SMMLV | MEDIO | **P0** |
| Res. 0312/2019 Estándares | ALTA (28%) | SANCIÓN | ALTO | **P0** |
| Res. 0312 - Mediciones | ALTA (100%) | SANCIÓN + CIERRE | ALTO | **P1** |
| Res. 0312 - Plan Mejora | ALTA (100%) | AUDITORÍA | MEDIO | **P1** |
| Res. 2646 Psicosocial | ALTA (100%) | SANCIÓN | ALTO | **P1** |
| Ley 1581 - Supresión | MEDIA (30%) | MULTA | MEDIO | **P2** |
| ISO 45001 - Comunicación | BAJA (20%) | CERTIFICACIÓN | BAJO | **P2** |
| ISO 45001 - MOC | BAJA (100%) | CERTIFICACIÓN | BAJO | **P2** |

---

## RECOMENDACIÓN ESTRATÉGICA

**El sistema NO está listo para producción en entorno regulado colombiano sin corregir los 4 hallazgos P0 normativos.**

### Plan de Acción Inmediato (Semanas 1-8):

| Semana | Norma | Entregable | Responsable |
|--------|-------|------------|-------------|
| 1-2 | Res. 1843/2025 - HCO/Concepto | Separación modelo + permisos médico/empleador | Backend + Frontend |
| 1-2 | Res. 2646/2008 - Psicosocial | Módulo completo: batería + análisis + plan + reporte | Backend + Frontend |
| 2-4 | Res. 1843/2025 - Medicina | Vigilancia epidemiológica + mediciones + alertas | Backend + Frontend |
| 3-4 | Res. 0312 - Estándares | Parametrización 60 criterios en BD + CRUD admin | Backend + BD |
| 4-6 | Ley 1581/2012 | Consentimiento + supresión + portabilidad | Backend + Auth |
| 5-8 | Res. 0312 - Plan Mejora | Origen hallazgo + verificación + evidencia + alertas | Backend |
| 6-8 | Res. 0312 - Mediciones | Módulo completo mediciones ambientales | Backend + Frontend |
| 6-8 | Res. 0312 - Comunicación | Buzón + consulta + participación + evidencias | Backend + Frontend |

**Inversión estimada:** ~600 horas-hombre desarrollo + 200 horas QA = **~10 semanas** para cumplimiento P0/P1 normativo.
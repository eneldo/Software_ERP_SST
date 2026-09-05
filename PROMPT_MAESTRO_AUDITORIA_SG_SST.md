PROMPT MAESTRO — AUDITORÍA INTEGRAL Y MEJORA DE SOFTWARE SG-SST COLOMBIA

ROL

Actúa como un equipo multidisciplinario experto conformado por:

1. Auditor experto en Seguridad y Salud en el Trabajo — SG-SST en Colombia.
2. Abogado o analista experto en normatividad laboral y SST colombiana.
3. Profesional especialista en medicina laboral y evaluaciones médicas ocupacionales.
4. Arquitecto de software senior.
5. Ingeniero backend.
6. Ingeniero frontend.
7. Especialista en bases de datos.
8. Especialista en ciberseguridad.
9. Especialista en protección de datos personales y datos sensibles.
10. QA / Tester senior.
11. Especialista DevOps.
12. Consultor de experiencia de usuario UX/UI.

OBJETIVO GENERAL

Realizar una auditoría integral del proyecto de software SG-SST suministrado, revisando:

- cumplimiento normativo colombiano;
- cobertura funcional;
- arquitectura;
- backend;
- frontend;
- base de datos;
- seguridad;
- manejo de información médica;
- trazabilidad;
- evidencias;
- reportes;
- indicadores;
- experiencia de usuario;
- calidad del código;
- pruebas;
- preparación para producción.

El objetivo final NO es solamente detectar errores.

Debes identificar brechas, diseñar las soluciones y proponer o implementar los cambios necesarios para convertir el sistema en una plataforma profesional de SG-SST para Colombia.

PRINCIPIO FUNDAMENTAL

No asumir que una funcionalidad existe solamente porque:

- aparece en un menú;
- existe un archivo;
- existe una tabla;
- existe un endpoint;
- existe una pantalla.

Una funcionalidad se considera implementada únicamente cuando exista evidencia verificable de que:

Frontend
→ API
→ lógica de negocio
→ validaciones
→ base de datos
→ permisos
→ trazabilidad
→ evidencia
→ reporte o consulta

funcionan correctamente de extremo a extremo.

==================================================
1. MARCO NORMATIVO
==================================================

Auditar el proyecto con base en la normativa colombiana vigente y aplicable al SG-SST.

Incluir como mínimo:

- Decreto 1072 de 2015.
- Resolución 0312 de 2019.
- Ley 1562 de 2012.
- Resolución 1843 de 2025.
- Resolución 1401 de 2007.
- Resolución 2013 de 1986.
- Resolución 652 de 2012 y sus modificaciones.
- normas de riesgo psicosocial.
- normas de emergencias.
- normas de trabajo en alturas, cuando aplique.
- normas de espacios confinados, cuando aplique.
- normas de riesgo eléctrico, cuando aplique.
- normas relacionadas con teletrabajo y trabajo remoto, cuando aplique.
- normas sobre protección de datos personales.
- demás normas colombianas vigentes relacionadas con SST según la actividad económica.

IMPORTANTE:

Antes de considerar una norma vigente, verificar:

- si fue modificada;
- derogada;
- sustituida;
- compilada;
- adicionada;
- o si existen normas posteriores aplicables.

No inventar requisitos legales.

Cuando exista duda normativa, indicarlo expresamente.

==================================================
2. MATRIZ MAESTRA DE CUMPLIMIENTO
==================================================

Construir una matriz con al menos las siguientes columnas:

ID
Norma
Artículo
Numeral
Requisito
Descripción de la obligación
Aplica / No aplica
Justificación de aplicabilidad
Módulo relacionado
Submódulo
Pantalla
Endpoint relacionado
Tabla de base de datos
Campo de base de datos
Evidencia encontrada
Estado de cumplimiento
Hallazgo
Nivel de riesgo
Impacto
Recomendación
Corrección propuesta
Prioridad
Responsable sugerido
Prueba requerida
Estado final

Utilizar la siguiente clasificación:

🟢 CUMPLE
La funcionalidad existe, funciona y puede demostrar cumplimiento.

🟡 CUMPLE PARCIALMENTE
Existe, pero presenta brechas.

🔴 NO CUMPLE
El requisito no está implementado.

🔵 REQUIERE MODIFICACIÓN
Existe funcionalmente, pero su diseño no corresponde correctamente al requisito.

⚪ NO APLICA
Debe justificarse técnicamente.

Prioridad:

CRÍTICA
ALTA
MEDIA
BAJA

==================================================
3. INVENTARIO FUNCIONAL DEL SOFTWARE
==================================================

Crear primero un mapa completo de la aplicación.

Identificar:

- módulos;
- submódulos;
- menús;
- pantallas;
- formularios;
- campos;
- botones;
- workflows;
- endpoints;
- servicios;
- modelos;
- tablas;
- relaciones;
- reportes;
- dashboards;
- documentos;
- notificaciones;
- tareas programadas;
- roles;
- permisos.

Construir la relación:

MÓDULO
→ FUNCIONALIDAD
→ FRONTEND
→ ENDPOINT
→ SERVICIO
→ MODELO
→ TABLA
→ EVIDENCIA

Identificar también funcionalidades huérfanas:

- pantalla sin endpoint;
- endpoint sin frontend;
- tabla sin uso;
- código muerto;
- archivos duplicados;
- módulos incompletos.

==================================================
4. AUDITORÍA POR MÓDULOS SG-SST
==================================================

Revisar como mínimo la existencia y calidad de los siguientes procesos:

EMPRESA

- datos de empresa;
- sedes;
- centros de trabajo;
- actividad económica;
- clase de riesgo;
- ARL;
- responsables SG-SST;
- configuración general.

EMPLEADOS

- identificación;
- datos laborales;
- tipo de contrato;
- cargo;
- área;
- sede;
- fecha de ingreso;
- estado;
- información relevante para SST.

CARGOS

Revisar:

- nombre;
- código;
- área;
- descripción;
- funciones;
- responsabilidades;
- competencias;
- habilidades;
- requisitos técnicos;
- requisitos físicos;
- requisitos mentales;
- riesgos asociados;
- controles;
- EPP;
- evaluaciones médicas relacionadas.

PROFESIOGRAMA

El profesiograma debe relacionar:

Cargo
→ peligros
→ riesgos
→ exposición
→ requisitos físicos
→ requisitos mentales
→ requisitos técnicos
→ evaluaciones médicas
→ pruebas complementarias
→ periodicidad

Evitar que sea simplemente un documento adjunto.

Debe poder utilizarse funcionalmente dentro del sistema.

==================================================
5. RESOLUCIÓN 1843 DE 2025
==================================================

Realizar una auditoría específica de todo el componente de evaluaciones médicas ocupacionales.

Revisar como mínimo:

- preingreso;
- periódicas programadas;
- periódicas por cambio de ocupación;
- egreso;
- post-incapacidad;
- retorno laboral;
- seguimiento o control.

Validar el flujo:

Empleado
→ Cargo
→ Profesiograma
→ Riesgos
→ Evaluación médica requerida
→ Exámenes complementarios
→ IPS / proveedor
→ realización
→ concepto médico
→ recomendaciones
→ restricciones
→ seguimiento
→ cierre

Verificar además:

- periodicidad;
- próxima evaluación;
- alertas;
- vencimientos;
- trazabilidad;
- historial.

MUY IMPORTANTE:

Diferenciar:

HISTORIA CLÍNICA OCUPACIONAL

de

CONCEPTO MÉDICO OCUPACIONAL.

El software no debe exponer al empleador información clínica que deba permanecer bajo reserva médica.

Revisar cuidadosamente:

- confidencialidad;
- permisos;
- almacenamiento;
- acceso;
- descarga;
- auditoría;
- protección de datos sensibles.

==================================================
6. IDENTIFICACIÓN DE PELIGROS Y VALORACIÓN DEL RIESGO
==================================================

Auditar:

- peligros;
- clasificación;
- fuente;
- medio;
- individuo;
- exposición;
- probabilidad;
- consecuencia;
- nivel de riesgo;
- aceptabilidad;
- controles existentes;
- medidas de intervención;
- responsables;
- fechas;
- seguimiento.

Relacionar:

Área
→ Cargo
→ Actividad
→ Peligro
→ Riesgo
→ Control
→ Trabajador expuesto

Revisar si el sistema permite mantener historial de cambios.

==================================================
7. EPP
==================================================

Auditar:

- catálogo;
- código;
- nombre;
- categoría;
- vida útil;
- certificaciones;
- estado;
- proveedor;
- stock;
- entrega;
- reposición;
- devolución;
- pérdida;
- deterioro;
- vencimiento.

Relacionar:

Cargo
→ Riesgo
→ EPP requerido
→ Trabajador
→ Entrega
→ Firma/evidencia
→ Reposición.

==================================================
8. ACCIDENTES, INCIDENTES Y ENFERMEDAD LABORAL
==================================================

Auditar:

- reporte;
- clasificación;
- trabajador;
- fecha;
- lugar;
- descripción;
- investigación;
- causas inmediatas;
- causas básicas;
- plan de acción;
- responsables;
- evidencias;
- seguimiento;
- cierre.

Relacionar cuando corresponda:

Accidente
→ investigación
→ causa
→ acción correctiva
→ responsable
→ vencimiento
→ evidencia
→ verificación
→ cierre.

==================================================
9. CAPACITACIONES
==================================================

Revisar:

- plan anual;
- inducción;
- reinducción;
- capacitación por riesgo;
- asistentes;
- convocatoria;
- evidencia;
- evaluación;
- certificado;
- responsable;
- horas;
- próxima capacitación.

==================================================
10. COMITÉS
==================================================

Auditar:

COPASST o Vigía SST.

Comité de Convivencia Laboral.

Revisar:

- conformación;
- integrantes;
- cargos;
- períodos;
- elecciones;
- reuniones;
- actas;
- compromisos;
- responsables;
- seguimiento.

==================================================
11. EMERGENCIAS
==================================================

Auditar:

- amenazas;
- vulnerabilidad;
- recursos;
- brigadas;
- integrantes;
- capacitaciones;
- simulacros;
- resultados;
- planes de mejora;
- inspecciones;
- equipos de emergencia.

==================================================
12. CARACTERIZACIÓN SOCIODEMOGRÁFICA
==================================================

Revisar si existe información suficiente para caracterizar la población trabajadora.

Verificar:

- edad;
- sexo;
- nivel educativo;
- estado civil cuando corresponda;
- antigüedad;
- cargo;
- área;
- tipo de contrato;
- jornada;
- sede;
- demás variables útiles para SST.

Evitar recolección innecesaria de información sensible.

==================================================
13. POLÍTICAS Y OBJETIVOS
==================================================

Auditar:

- política SST;
- política prevención consumo de alcohol, tabaco y sustancias cuando corresponda;
- política de convivencia;
- otras políticas aplicables.

Cada política debe permitir:

- versión;
- fecha;
- aprobación;
- responsable;
- vigencia;
- evidencia;
- publicación;
- historial.

==================================================
14. PLAN ANUAL DE TRABAJO
==================================================

Debe permitir gestionar:

Actividad
Responsable
Fecha inicio
Fecha límite
Recursos
Indicador
Meta
Estado
Evidencia
Porcentaje de avance
Observaciones

El dashboard debe alimentarse de datos reales.

==================================================
15. INDICADORES
==================================================

Auditar indicadores de:

- estructura;
- proceso;
- resultado.

Además revisar indicadores de:

- accidentalidad;
- ausentismo;
- capacitaciones;
- inspecciones;
- acciones correctivas;
- evaluaciones médicas;
- cumplimiento del plan;
- estándares mínimos;
- gestión de riesgos.

Verificar fórmulas.

No aceptar valores escritos manualmente cuando puedan calcularse desde el sistema.

==================================================
16. ESTÁNDARES MÍNIMOS
==================================================

Auditar la implementación de la Resolución 0312 de 2019.

El sistema debería permitir:

- identificar estándares aplicables;
- registrar calificación;
- evidencia;
- observaciones;
- responsable;
- plan de mejora;
- porcentaje de cumplimiento;
- historial.

No codificar rígidamente la norma en la interfaz si puede almacenarse de forma parametrizable.

==================================================
17. MATRIZ LEGAL
==================================================

Debe permitir almacenar:

Norma
Entidad
Fecha
Tema
Artículo
Requisito
Aplicabilidad
Responsable
Evidencia
Estado
Fecha de revisión
Vigencia
Modificaciones
Observaciones

Diseñar la matriz normativa como información parametrizable.

PRINCIPIO:

Las actualizaciones normativas NO deberían requerir modificar código fuente.

==================================================
18. DOCUMENTOS Y EVIDENCIAS
==================================================

Revisar:

- carga;
- clasificación;
- versión;
- fecha;
- responsable;
- aprobación;
- vencimiento;
- estado;
- historial;
- firma;
- hash cuando aplique;
- descarga;
- permisos.

Cada evidencia debe poder asociarse a:

- requisito;
- actividad;
- auditoría;
- acción;
- capacitación;
- inspección;
- comité;
- accidente;
- empleado;
- evaluación médica;
- plan de trabajo.

==================================================
19. PLANES DE MEJORAMIENTO
==================================================

Implementar o revisar el flujo:

Hallazgo
→ causa
→ acción
→ responsable
→ fecha límite
→ avance
→ evidencia
→ verificación
→ cierre.

Permitir origen del hallazgo:

- auditoría;
- inspección;
- incidente;
- accidente;
- estándar mínimo;
- indicador;
- revisión por dirección;
- requisito legal.

==================================================
20. PHVA
==================================================

Clasificar todas las funcionalidades dentro del ciclo:

PLANEAR

- política;
- objetivos;
- evaluación inicial;
- matriz legal;
- riesgos;
- plan anual;
- recursos.

HACER

- capacitación;
- EPP;
- vigilancia;
- evaluaciones médicas;
- emergencias;
- inspecciones.

VERIFICAR

- indicadores;
- auditorías;
- investigaciones;
- evaluación de estándares.

ACTUAR

- acciones correctivas;
- acciones preventivas;
- planes de mejoramiento;
- revisión gerencial.

Detectar vacíos dentro del ciclo.

==================================================
21. DASHBOARD
==================================================

Evaluar si el dashboard sirve para tomar decisiones.

Debe mostrar información real, por ejemplo:

- porcentaje general de cumplimiento;
- cumplimiento Resolución 0312;
- cumplimiento plan anual;
- acciones vencidas;
- acciones próximas a vencer;
- evaluaciones médicas pendientes;
- evaluaciones próximas a vencer;
- capacitaciones pendientes;
- inspecciones pendientes;
- accidentes;
- incidentes;
- indicadores críticos.

Cada indicador debe permitir ir al registro fuente.

No utilizar datos ficticios en producción.

==================================================
22. USUARIOS, ROLES Y PERMISOS
==================================================

Auditar RBAC.

Considerar como mínimo posibles perfiles:

- Superadministrador;
- Administrador empresa;
- Responsable SG-SST;
- Profesional SST;
- Médico ocupacional;
- Talento Humano;
- Auditor;
- Trabajador;
- Consulta.

Aplicar mínimo privilegio.

Verificar permisos tanto en frontend como en backend.

Ocultar un botón NO constituye seguridad.

==================================================
23. MULTIEMPRESA
==================================================

Si la plataforma es SaaS o multiempresa:

Auditar aislamiento de datos por tenant.

Ningún usuario de una empresa debe poder consultar información de otra empresa mediante:

- frontend;
- API;
- manipulación de IDs;
- consultas;
- exportaciones;
- documentos;
- reportes.

Verificar tenant_id o mecanismo equivalente en toda entidad relevante.

==================================================
24. BASE DE DATOS
==================================================

Auditar:

- normalización;
- claves primarias;
- claves foráneas;
- índices;
- constraints;
- unicidad;
- NULL;
- timestamps;
- soft-delete;
- auditoría;
- campos sensibles;
- cifrado;
- migraciones.

Detectar:

- tablas duplicadas;
- columnas innecesarias;
- relaciones incorrectas;
- datos inconsistentes;
- ausencia de constraints;
- problemas de integridad referencial.

Proponer mejoras SQL concretas.

==================================================
25. BACKEND
==================================================

Auditar:

- arquitectura;
- routers;
- controladores;
- servicios;
- repositorios;
- modelos;
- schemas;
- validaciones;
- excepciones;
- middleware;
- autenticación;
- autorización;
- logging;
- rate limiting;
- CORS;
- seguridad.

Buscar:

- SQL injection;
- IDOR;
- mass assignment;
- broken access control;
- exposición de datos;
- secretos;
- contraseñas inseguras;
- JWT mal implementado;
- endpoints sin protección.

==================================================
26. FRONTEND
==================================================

Auditar:

- estructura;
- navegación;
- UX;
- validación;
- componentes;
- estados;
- errores;
- loading;
- accesibilidad;
- responsive;
- coherencia visual.

Detectar formularios que permitan:

- datos inválidos;
- duplicados;
- fechas imposibles;
- registros inconsistentes.

==================================================
27. CIBERSEGURIDAD
==================================================

Revisar alineación con OWASP.

Incluir:

- autenticación;
- autorización;
- sesiones;
- JWT;
- cookies;
- CORS;
- CSRF cuando aplique;
- XSS;
- SQL injection;
- IDOR;
- SSRF;
- subida de archivos;
- directory traversal;
- exposición de secretos;
- logs sensibles;
- dependencias vulnerables.

Clasificar vulnerabilidades:

CRÍTICA
ALTA
MEDIA
BAJA

Cuando sea posible incluir:

- descripción;
- impacto;
- ubicación;
- evidencia;
- remediación;
- ejemplo de código corregido.

==================================================
28. TRAZABILIDAD
==================================================

Toda operación crítica debe registrar:

Quién
Qué
Cuándo
Desde dónde
Registro anterior
Registro nuevo
Motivo
Entidad afectada

Auditar especialmente:

- trabajadores;
- evaluaciones médicas;
- recomendaciones;
- riesgos;
- accidentes;
- documentos;
- acciones correctivas;
- usuarios;
- permisos.

==================================================
29. AUDITORÍA DEL SISTEMA
==================================================

Diseñar o validar una bitácora que permita responder:

¿Quién modificó este dato?

¿Cuándo?

¿Qué valor tenía antes?

¿Qué valor quedó?

¿Desde qué usuario o IP?

¿A qué empresa pertenecía?

==================================================
30. ALERTAS Y VENCIMIENTOS
==================================================

Auditar alertas para:

- evaluaciones médicas;
- capacitaciones;
- EPP;
- certificaciones;
- inspecciones;
- acciones;
- documentos;
- comités;
- simulacros;
- contratos;
- responsables.

Clasificar alertas:

VENCIDO
CRÍTICO
PRÓXIMO
NORMAL.

==================================================
31. REPORTES
==================================================

Auditar exportaciones:

- PDF;
- Excel;
- CSV cuando corresponda.

Los reportes deben identificar:

- empresa;
- período;
- fecha generación;
- responsable;
- filtros utilizados.

Evitar exposición accidental de datos de otros tenants.

==================================================
32. CALIDAD DE CÓDIGO
==================================================

Buscar:

- duplicación;
- código muerto;
- funciones demasiado largas;
- nombres inconsistentes;
- comentarios obsoletos;
- TODO pendientes;
- dependencias innecesarias;
- archivos obsoletos;
- hardcoding;
- errores silenciosos.

Proponer refactorización priorizada.

==================================================
33. PRUEBAS
==================================================

Determinar cobertura existente.

Crear o recomendar:

- unit tests;
- integration tests;
- API tests;
- permission tests;
- security tests;
- end-to-end tests.

Casos críticos:

Usuario empresa A no puede consultar empresa B.

Empleado sin permisos no puede consultar información médica.

Registro eliminado no rompe relaciones.

Las fechas de vencimiento se calculan correctamente.

No se permiten duplicados donde corresponda.

==================================================
34. PRODUCCIÓN
==================================================

Revisar:

- variables de entorno;
- secretos;
- HTTPS;
- proxy;
- Docker;
- servicios;
- base de datos;
- migraciones;
- backups;
- restore;
- logs;
- monitoreo;
- healthcheck;
- actualizaciones.

Preparar checklist de producción.

==================================================
35. METODOLOGÍA DE TRABAJO
==================================================

Realizar la auditoría por fases.

FASE 1
Cumplimiento normativo.

FASE 2
Inventario funcional.

FASE 3
Auditoría módulo por módulo.

FASE 4
Resolución 1843 de 2025 y medicina laboral.

FASE 5
Ciclo PHVA.

FASE 6
Arquitectura y código.

FASE 7
Seguridad y datos sensibles.

FASE 8
Trazabilidad y evidencias.

FASE 9
Dashboard, indicadores y reportes.

FASE 10
QA, producción y cierre.

No pasar una fase como terminada mientras existan hallazgos críticos sin documentar.

==================================================
36. FORMATO DE CADA HALLAZGO
==================================================

Cada hallazgo deberá indicar:

ID:
Nombre:
Área:
Módulo:
Archivo:
Línea:
Endpoint:
Tabla:
Norma relacionada:
Artículo:
Descripción:
Evidencia:
Impacto:
Nivel de riesgo:
Estado actual:
Solución propuesta:
Cambios requeridos:
Prueba de validación:
Prioridad:

==================================================
37. PLAN DE ACCIÓN
==================================================

Después de la auditoría construir backlog priorizado.

ORDEN DE PRIORIDAD:

P0 — CRÍTICO
Seguridad, pérdida de datos, exposición de información médica, incumplimientos legales críticos.

P1 — ALTO
Funcionalidad normativa obligatoria ausente.

P2 — MEDIO
Mejoras funcionales importantes.

P3 — BAJO
UX, optimización, limpieza y mejoras menores.

No mezclar correcciones cosméticas con hallazgos regulatorios críticos.

==================================================
38. REGLAS PARA MODIFICAR EL PROYECTO
==================================================

Antes de modificar:

1. analizar;
2. identificar dependencias;
3. verificar impacto;
4. documentar hallazgo;
5. diseñar solución.

Durante la modificación:

- conservar funcionalidades existentes;
- evitar romper compatibilidad;
- no borrar información útil;
- no crear código duplicado;
- respetar arquitectura;
- utilizar migraciones para cambios de BD;
- agregar validaciones;
- agregar pruebas.

Después:

- ejecutar pruebas;
- comprobar funcionamiento;
- documentar resultado.

==================================================
39. REGLAS DE NO ALUCINACIÓN
==================================================

Nunca afirmar que algo existe sin comprobarlo.

Nunca afirmar cumplimiento legal solamente porque existe un campo o una pantalla.

Nunca inventar:

- normas;
- artículos;
- tablas;
- endpoints;
- archivos;
- columnas;
- resultados de pruebas.

Cuando no exista evidencia escribir:

NO VERIFICADO

o

NO ENCONTRADO.

==================================================
40. ENTREGABLE FINAL
==================================================

Entregar al finalizar:

1. Resumen ejecutivo.
2. Arquitectura encontrada.
3. Inventario de módulos.
4. Matriz normativa completa.
5. Matriz de cumplimiento.
6. Hallazgos críticos.
7. Hallazgos altos.
8. Hallazgos medios.
9. Hallazgos bajos.
10. Vulnerabilidades.
11. Brechas funcionales.
12. Brechas normativas.
13. Brechas de medicina laboral.
14. Brechas de seguridad.
15. Brechas de base de datos.
16. Mejoras UX.
17. Arquitectura objetivo recomendada.
18. Plan de acción.
19. Backlog P0/P1/P2/P3.
20. Pruebas necesarias.
21. Checklist de producción.
22. Porcentaje estimado de cumplimiento.
23. Recomendación final para puesta en producción.

==================================================
41. RESULTADO OBJETIVO DEL SISTEMA
==================================================

El producto final debe evolucionar hacia esta relación:

NORMA
↓
REQUISITO
↓
PROCESO
↓
MÓDULO
↓
RESPONSABLE
↓
ACTIVIDAD
↓
EVIDENCIA
↓
INDICADOR
↓
VENCIMIENTO
↓
AUDITORÍA
↓
PLAN DE MEJORAMIENTO

El software no debe ser solamente un repositorio de documentos.

Debe convertirse en un SISTEMA DE GESTIÓN Y EVIDENCIA DE CUMPLIMIENTO SG-SST.

==================================================
42. INSTRUCCIÓN DE INICIO
==================================================

Comienza por la FASE 1.

Primero:

1. inspecciona completamente el proyecto;
2. identifica la tecnología utilizada;
3. genera el inventario preliminar de módulos;
4. identifica estructura backend/frontend/base de datos;
5. construye la matriz normativa;
6. cruza requisitos contra funcionalidades reales;
7. presenta los primeros hallazgos.

No hagas cambios masivos todavía.

Primero presenta el diagnóstico de la FASE 1.

Al finalizar cada fase presenta:

- qué se revisó;
- qué se encontró;
- qué cumple;
- qué no cumple;
- riesgos;
- cambios recomendados;
- cambios que deben ejecutarse;
- porcentaje de avance;
- siguiente fase.

Continúa automáticamente con las siguientes fases una vez aprobado el diagnóstico, manteniendo trazabilidad de todos los hallazgos.
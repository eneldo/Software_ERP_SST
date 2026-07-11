// ============================================================
// CONFIGURACIÓN GLOBAL - ENTIDADES ELIMINACIÓN INTELIGENTE
// ERP SST PRO ENTERPRISE
// FASE 37.2 — Framework Global de Eliminación Inteligente
// Archivo: frontend/src/config/smartDeleteEntities.js
// ============================================================

export const SMART_DELETE_ENTITIES = {
  empresa: {
    entidad: "empresa",
    etiqueta: "empresa",
    etiquetaPlural: "empresas",
    idField: "id",
    getNombre: (item) => {
      const nombre = item?.nombre || "Empresa seleccionada";
      return item?.nit ? `${nombre} • NIT ${item.nit}` : nombre;
    },
  },

  sede: {
    entidad: "sede",
    etiqueta: "sede",
    etiquetaPlural: "sedes",
    idField: "id",
    getNombre: (item) => item?.nombre || item?.sede_nombre || "Sede seleccionada",
  },

  area: {
    entidad: "area",
    etiqueta: "área",
    etiquetaPlural: "áreas",
    idField: "id",
    getNombre: (item) => item?.nombre || item?.area_nombre || "Área seleccionada",
  },

  cargo: {
    entidad: "cargo",
    etiqueta: "cargo",
    etiquetaPlural: "cargos",
    idField: "id",
    getNombre: (item) => item?.nombre || item?.cargo_nombre || "Cargo seleccionado",
  },

  empleado: {
    entidad: "empleado",
    etiqueta: "empleado",
    etiquetaPlural: "empleados",
    idField: "id",
    getNombre: (item) => {
      const nombres = [item?.nombres, item?.apellidos].filter(Boolean).join(" ");
      return nombres || item?.nombre_completo || item?.documento || "Empleado seleccionado";
    },
  },


  examen_medico: {
    entidad: "examen_medico",
    etiqueta: "examen médico",
    etiquetaPlural: "exámenes médicos",
    idField: "id",
    getNombre: (item) => {
      const empleado = item?.empleado_nombre || item?.nombre_empleado || "Empleado sin nombre";
      const tipo = item?.tipo_examen || "Examen médico";
      const fecha = item?.fecha_examen ? ` • ${item.fecha_examen}` : "";
      return `${empleado} • ${tipo}${fecha}`;
    },
  },

  epp: {
    entidad: "epp",
    etiqueta: "EPP",
    etiquetaPlural: "EPP",
    idField: "id",
    getNombre: (item) => item?.nombre || item?.elemento || "EPP seleccionado",
  },

  inspeccion: {
    entidad: "inspeccion",
    etiqueta: "inspección",
    etiquetaPlural: "inspecciones",
    idField: "id",
    getNombre: (item) => item?.codigo || item?.titulo || item?.nombre || "Inspección seleccionada",
  },

  capa: {
    entidad: "capa",
    etiqueta: "CAPA",
    etiquetaPlural: "CAPA",
    idField: "id",
    getNombre: (item) => item?.codigo || item?.titulo || "CAPA seleccionada",
  },

  incidente: {
    entidad: "incidente",
    etiqueta: "incidente",
    etiquetaPlural: "incidentes",
    idField: "id",
    getNombre: (item) => item?.codigo || item?.titulo || "Incidente seleccionado",
  },
};

export const getSmartDeleteConfig = (entidad) => {
  if (!entidad) return null;
  return SMART_DELETE_ENTITIES[entidad] || null;
};


// ============================================================
// FASE 37.4 — ENTERPRISE CORE FRAMEWORK
// Metadata frontend local para mantener la UI funcional incluso si
// el backend metadata endpoint no se ha consultado todavía.
// ============================================================
export const SMART_DELETE_CORE_METADATA = {
  empresa: { modulo: "Organización", icono: "building-2", color: "blue", severidad: "LEGAL" },
  sede: { modulo: "Organización", icono: "map-pin", color: "indigo", severidad: "HIGH" },
  area: { modulo: "Organización", icono: "network", color: "cyan", severidad: "HIGH" },
  cargo: { modulo: "Organización", icono: "briefcase", color: "violet", severidad: "HIGH" },
  empleado: { modulo: "Organización", icono: "users", color: "emerald", severidad: "CRITICAL" },
  examen_medico: { modulo: "Hacer", icono: "stethoscope", color: "sky", severidad: "LEGAL" },
  epp: { modulo: "Hacer", icono: "hard-hat", color: "amber", severidad: "HIGH" },
  inspeccion: { modulo: "Hacer", icono: "search-check", color: "orange", severidad: "HIGH" },
  capa: { modulo: "Actuar", icono: "wrench", color: "red", severidad: "CRITICAL" },
  incidente: { modulo: "Hacer", icono: "siren", color: "rose", severidad: "LEGAL" },
};

export const getSmartDeleteCoreMetadata = (entidad) => {
  if (!entidad) return null;
  return SMART_DELETE_CORE_METADATA[entidad] || null;
};

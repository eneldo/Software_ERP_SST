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

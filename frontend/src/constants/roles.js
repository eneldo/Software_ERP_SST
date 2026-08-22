export const ROLES_TRABAJADORES = ["EMPLEADO", "TRABAJADOR", "CONTRATISTA"];

export const ROLES_PORTAL_EMPLEADO = [
  "SUPER_ADMIN",
  "ADMIN_EMPRESA",
  "RESPONSABLE_SST",
  "COORDINADOR_SST",
  "TECNICO_SST",
  "COPASST",
  "VIGIA_SST",
  "JEFE_AREA",
  ...ROLES_TRABAJADORES,
];

export const ROLES_DASHBOARD = [
  "SUPER_ADMIN",
  "ADMIN_EMPRESA",
  "RESPONSABLE_SST",
  "COORDINADOR_SST",
  "TECNICO_SST",
  "ALTA_DIRECCION",
  "REPRESENTANTE_LEGAL",
  "AUDITOR",
  "COPASST",
  "VIGIA_SST",
  "JEFE_AREA",
  "TALENTO_HUMANO",
  "MEDICO_OCUPACIONAL",
  "SOLO_LECTURA",
];

// Roles con acceso de administración (gestión de usuarios, roles, permisos, configuración)
export const ROLES_ADMIN_SISTEMA = ["SUPER_ADMIN"];

// Roles con acceso total a módulos SST (gestión)
export const ROLES_GESTION_SST = [
  "SUPER_ADMIN",
  "ADMIN_EMPRESA",
  "RESPONSABLE_SST",
  "COORDINADOR_SST",
];

// Roles con acceso a módulos de organización
export const ROLES_ORGANIZACION = [
  "SUPER_ADMIN",
  "ADMIN_EMPRESA",
  "RESPONSABLE_SST",
  "COORDINADOR_SST",
  "TALENTO_HUMANO",
  "JEFE_AREA",
];

// Roles con acceso a módulos PLANEAR
export const ROLES_PLANEAR = [
  "SUPER_ADMIN",
  "ADMIN_EMPRESA",
  "RESPONSABLE_SST",
  "COORDINADOR_SST",
  "TECNICO_SST",
  "COPASST",
];

// Roles con acceso a módulos HACER
export const ROLES_HACER = [
  "SUPER_ADMIN",
  "ADMIN_EMPRESA",
  "RESPONSABLE_SST",
  "COORDINADOR_SST",
  "TECNICO_SST",
  "COPASST",
  "VIGIA_SST",
  "JEFE_AREA",
  "TALENTO_HUMANO",
  "MEDICO_OCUPACIONAL",
];

// Roles con acceso a módulos VERIFICAR
export const ROLES_VERIFICAR = [
  "SUPER_ADMIN",
  "ADMIN_EMPRESA",
  "RESPONSABLE_SST",
  "COORDINADOR_SST",
  "TECNICO_SST",
  "AUDITOR",
  "COPASST",
  "VIGIA_SST",
  "ALTA_DIRECCION",
  "REPRESENTANTE_LEGAL",
];

// Roles con acceso a módulos documentales
export const ROLES_DOCUMENTAL = [
  "SUPER_ADMIN",
  "ADMIN_EMPRESA",
  "RESPONSABLE_SST",
  "COORDINADOR_SST",
  "TECNICO_SST",
  "TALENTO_HUMANO",
];

// Roles con acceso a exámenes médicos
export const ROLES_EXAMENES = [
  "SUPER_ADMIN",
  "ADMIN_EMPRESA",
  "RESPONSABLE_SST",
  "COORDINADOR_SST",
  "TECNICO_SST",
  "TALENTO_HUMANO",
  "MEDICO_OCUPACIONAL",
];

// Roles con acceso a capacitaciones
export const ROLES_CAPACITACIONES = [
  "SUPER_ADMIN",
  "ADMIN_EMPRESA",
  "RESPONSABLE_SST",
  "COORDINADOR_SST",
  "TECNICO_SST",
  "COPASST",
  "TALENTO_HUMANO",
];

// Roles con acceso a incidentes/accidentes
export const ROLES_INCIDENTES = [
  "SUPER_ADMIN",
  "ADMIN_EMPRESA",
  "RESPONSABLE_SST",
  "COORDINADOR_SST",
  "TECNICO_SST",
  "COPASST",
  "VIGIA_SST",
  "JEFE_AREA",
];

// Roles con acceso a auditorías SST
export const ROLES_AUDITORIAS = [
  "SUPER_ADMIN",
  "ADMIN_EMPRESA",
  "RESPONSABLE_SST",
  "COORDINADOR_SST",
  "AUDITOR",
  "COPASST",
];

// Roles con acceso a indicadores
export const ROLES_INDICADORES = [
  "SUPER_ADMIN",
  "ADMIN_EMPRESA",
  "RESPONSABLE_SST",
  "COORDINADOR_SST",
  "TECNICO_SST",
  "ALTA_DIRECCION",
  "REPRESENTANTE_LEGAL",
  "AUDITOR",
];

// Roles con acceso a reportes anónimos
export const ROLES_REPORTES_ANONIMOS = [
  "SUPER_ADMIN",
  "ADMIN_EMPRESA",
  "RESPONSABLE_SST",
  "COORDINADOR_SST",
  "AUDITOR",
  "COPASST",
];

// Roles con acceso a acciones correctivas
export const ROLES_ACCIONES_CORRECTIVAS = [
  "SUPER_ADMIN",
  "ADMIN_EMPRESA",
  "RESPONSABLE_SST",
  "COORDINADOR_SST",
  "TECNICO_SST",
  "COPASST",
];

export function normalizarRol(usuario) {
  return String(usuario?.rol || "").trim().toUpperCase();
}

export function esRolTrabajador(usuario) {
  return ROLES_TRABAJADORES.includes(normalizarRol(usuario));
}

export function rutaInicialPorRol(usuario) {
  return esRolTrabajador(usuario) ? "/portal-empleado" : "/admin/dashboard";
}

export function resolverDestinoIngreso(usuario, destinoSolicitado = null) {
  if (esRolTrabajador(usuario)) return "/portal-empleado";

  if (!destinoSolicitado || destinoSolicitado === "/") {
    return "/admin/dashboard";
  }

  if (destinoSolicitado.startsWith("/portal-empleado")) {
    return "/admin/dashboard";
  }

  return destinoSolicitado;
}

export function tieneAccesoModulo(usuario, rolesPermitidos) {
  const rol = normalizarRol(usuario);
  return rolesPermitidos.includes(rol);
}

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

  // El portal puede ser consultado después desde el menú por los roles SST
  // autorizados, pero nunca debe convertirse en su pantalla inicial.
  if (destinoSolicitado.startsWith("/portal-empleado")) {
    return "/admin/dashboard";
  }

  return destinoSolicitado;
}

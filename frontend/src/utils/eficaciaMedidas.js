// ============================================================
// UTILIDADES EFICACIA MEDIDAS CORRECTIVAS
// ERP SST PRO
// FASE 1.1.8.7.5.3 — Indicador de eficacia en tabla principal
// Archivo: frontend/src/utils/eficaciaMedidas.js
// ============================================================

export function normalizarNumero(value, fallback = 0) {
  if (value === null || value === undefined || value === "") return fallback;
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

export function getEficaciaEstado(medida = {}) {
  const estado = String(medida.estado || "").toUpperCase();
  const efectiva = medida.efectiva;
  const porcentaje = medida.porcentaje_eficacia;

  if (estado !== "CERRADA" && porcentaje === null && porcentaje === undefined && !medida.verificacion_eficacia) {
    return {
      key: "PENDIENTE",
      label: "Pendiente",
      shortLabel: "—",
      percent: null,
      className: "pendiente",
      description: "Sin verificación de eficacia",
    };
  }

  if (efectiva === true || normalizarNumero(porcentaje, -1) >= 80) {
    return {
      key: "EFICAZ",
      label: "Eficaz",
      shortLabel: "EFICAZ",
      percent: porcentaje !== null && porcentaje !== undefined ? normalizarNumero(porcentaje, 100) : 100,
      className: "eficaz",
      description: "La medida eliminó o controló la causa raíz",
    };
  }

  if (porcentaje !== null && porcentaje !== undefined) {
    const numeric = normalizarNumero(porcentaje, 0);

    if (numeric >= 50) {
      return {
        key: "PARCIAL",
        label: "Parcial",
        shortLabel: "PARCIAL",
        percent: numeric,
        className: "parcial",
        description: "La medida requiere refuerzo o seguimiento adicional",
      };
    }

    return {
      key: "NO_EFICAZ",
      label: "No eficaz",
      shortLabel: "NO EFICAZ",
      percent: numeric,
      className: "no-eficaz",
      description: "La medida no eliminó la causa raíz",
    };
  }

  if (efectiva === false && medida.verificacion_eficacia) {
    return {
      key: "NO_EFICAZ",
      label: "No eficaz",
      shortLabel: "NO EFICAZ",
      percent: 0,
      className: "no-eficaz",
      description: "Verificación registrada como no eficaz",
    };
  }

  return {
    key: "PENDIENTE",
    label: "Pendiente",
    shortLabel: "—",
    percent: null,
    className: "pendiente",
    description: "Sin verificación de eficacia",
  };
}

export function getEficaciaResumen(medidas = []) {
  const resumen = {
    total: medidas.length,
    eficaces: 0,
    parciales: 0,
    no_eficaces: 0,
    pendientes: 0,
    promedio: 0,
  };

  let suma = 0;
  let conValor = 0;

  medidas.forEach((medida) => {
    const estado = getEficaciaEstado(medida);

    if (estado.key === "EFICAZ") resumen.eficaces += 1;
    else if (estado.key === "PARCIAL") resumen.parciales += 1;
    else if (estado.key === "NO_EFICAZ") resumen.no_eficaces += 1;
    else resumen.pendientes += 1;

    if (estado.percent !== null && estado.percent !== undefined) {
      suma += Number(estado.percent);
      conValor += 1;
    }
  });

  resumen.promedio = conValor ? Math.round((suma / conValor) * 10) / 10 : 0;
  return resumen;
}

// ============================================================
// API EXPORTACIONES ENTERPRISE MEDIDAS CORRECTIVAS
// ERP SST PRO
// FASE 1.1.8.7.6.1 — PDF + Excel individual
// ============================================================

import api from "./axios";

const BASE_URL = "/medidas-correctivas-exportaciones";

function descargarBlob(response, filename, mimeType) {
  const blob = new Blob([response.data], { type: mimeType });
  const url = window.URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();

  window.URL.revokeObjectURL(url);
}

export async function descargarPdfMedidaCorrectiva(id, codigo = "") {
  const response = await api.get(`${BASE_URL}/${id}/pdf`, {
    responseType: "blob",
  });

  descargarBlob(response, `medida_correctiva_${codigo || id}.pdf`, "application/pdf");
}

export async function descargarExcelMedidaCorrectiva(id, codigo = "") {
  const response = await api.get(`${BASE_URL}/${id}/excel`, {
    responseType: "blob",
  });

  descargarBlob(
    response,
    `medida_correctiva_${codigo || id}.xlsx`,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  );
}

// ============================================================
// API EXPORTACIONES ENTERPRISE MEDIDAS CORRECTIVAS
// ERP SST PRO
// FASE 1.1.8.7.6.1 — PDF + Excel individual
// ============================================================

import api from "./axios";

const BASE_URL = "/medidas-correctivas-exportaciones";

async function descargarBlob(response, filename, mimeType) {
  const arrayBuffer = response.data instanceof Blob ? await response.data.arrayBuffer() : response.data;
  const bytes = new Uint8Array(arrayBuffer);
  let binary = "";
  for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
  const base64 = btoa(binary);
  const dataUrl = `data:${mimeType};base64,${base64}`;

  const link = document.createElement("a");
  link.href = dataUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
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

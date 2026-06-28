// ============================================================
// API ÁREAS SST ENTERPRISE 360°
// Archivo: frontend/src/api/areaSstApi.js
// FASE 1.1.3 — Áreas SST Enterprise 360°
// ============================================================

import api from "./axios";

export const listarAreasSST = async (params = {}) => {
  const response = await api.get("/areas/", { params });
  return response.data;
};

export const obtenerDashboardAreasSST = async (params = {}) => {
  const response = await api.get("/areas/dashboard/resumen", { params });
  return response.data;
};

export const obtenerAreaSST = async (id) => {
  const response = await api.get(`/areas/${id}`);
  return response.data;
};

export const crearAreaSST = async (data) => {
  const response = await api.post("/areas/", data);
  return response.data;
};

export const actualizarAreaSST = async (id, data) => {
  const response = await api.put(`/areas/${id}`, data);
  return response.data;
};

export const eliminarAreaSST = async (id) => {
  const response = await api.delete(`/areas/${id}`);
  return response.data;
};

export const cambiarEstadoAreaSST = async (id, activo) => {
  const response = await api.patch(`/areas/${id}/estado`, null, {
    params: { activo },
  });
  return response.data;
};

export const listarEmpresasParaAreasSST = async () => {
  const response = await api.get("/empresas/");
  return response.data;
};

export const listarSedesParaAreasSST = async (params = {}) => {
  const response = await api.get("/sedes/", { params });
  return response.data;
};

// ============================================================
// FASE 1.1.3.2 / 1.1.3.3 — Exportaciones Áreas SST
// ============================================================
function descargarBlob(response, nombreFallback) {
  const contentDisposition = response.headers?.["content-disposition"] || "";
  const match = contentDisposition.match(/filename="?([^";]+)"?/i);
  const nombreArchivo = match?.[1] || nombreFallback;

  const blob = new Blob([response.data], {
    type: response.headers?.["content-type"] || "application/octet-stream",
  });

  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = nombreArchivo;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export const exportarAreasSSTExcel = async (params = {}) => {
  const response = await api.get("/areas/exportar/excel", {
    params,
    responseType: "blob",
  });
  descargarBlob(response, "areas_sst_analytics_pro.xlsx");
  return true;
};

export const exportarAreasSSTPDF = async (params = {}) => {
  const response = await api.get("/areas/exportar/pdf", {
    params,
    responseType: "blob",
  });
  descargarBlob(response, "areas_sst_analytics_pro.pdf");
  return true;
};


// ============================================================
// FASE 1.1.3.4 — Histórico SST por Área
// ============================================================
export const listarHistorialAreaSST = async (areaId, params = {}) => {
  const response = await api.get(`/areas/${areaId}/historial`, { params });
  return response.data;
};

export const obtenerResumenHistorialAreaSST = async (areaId) => {
  const response = await api.get(`/areas/${areaId}/historial/resumen`);
  return response.data;
};

export const crearHistorialAreaSST = async (areaId, data) => {
  const response = await api.post(`/areas/${areaId}/historial`, data);
  return response.data;
};

export const actualizarHistorialAreaSST = async (eventoId, data) => {
  const response = await api.put(`/areas/historial/${eventoId}`, data);
  return response.data;
};

export const eliminarHistorialAreaSST = async (eventoId) => {
  const response = await api.delete(`/areas/historial/${eventoId}`);
  return response.data;
};

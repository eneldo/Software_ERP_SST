export const MAX_FILE_SIZE_MB = 10;
export const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

export const EXTENSIONES_PERMITIDAS = [
  ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff",
  ".pdf", ".doc", ".docx", ".xls", ".xlsx",
];

export function validarArchivoAntesDeSubir(file) {
  if (!file) {
    return { ok: false, mensaje: "No se seleccionó ningún archivo." };
  }

  if (file.size > MAX_FILE_SIZE_BYTES) {
    return {
      ok: false,
      mensaje: `El archivo supera ${MAX_FILE_SIZE_MB} MB. Seleccione un archivo más liviano.`,
    };
  }

  const nombre = file.name || "";
  const extension = nombre.substring(nombre.lastIndexOf(".")).toLowerCase();

  if (!EXTENSIONES_PERMITIDAS.includes(extension)) {
    return { ok: false, mensaje: `Formato no permitido: ${extension}.` };
  }

  return { ok: true, mensaje: "" };
}

import React, { useMemo, useState } from "react";
import {
  CheckCircle2,
  Copy,
  Download,
  ExternalLink,
  QrCode,
  ShieldAlert,
} from "lucide-react";

const construirUrlPublica = () => {
  if (typeof window === "undefined") return "/reporte-sst";
  return `${window.location.origin}/reporte-sst`;
};

const construirUrlQr = (url) =>
  `https://api.qrserver.com/v1/create-qr-code/?size=320x320&margin=16&data=${encodeURIComponent(url)}`;

export default function PublicReportPublisher() {
  const [mostrarQr, setMostrarQr] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const urlPublica = useMemo(construirUrlPublica, []);
  const urlQr = useMemo(() => construirUrlQr(urlPublica), [urlPublica]);

  const copiarEnlace = async () => {
    try {
      await navigator.clipboard.writeText(urlPublica);
      setMensaje("Enlace público copiado. Ya puedes compartirlo.");
    } catch {
      setMensaje("No fue posible copiar automáticamente. Selecciona el enlace mostrado.");
    }
  };

  return (
    <section className="public-report-publisher" aria-label="Publicación del formulario público SST">
      <div className="public-report-publisher-copy">
        <span className="public-report-publisher-tag">
          <ShieldAlert size={16} /> Participación de trabajadores y visitantes
        </span>
        <h3>Publicar formulario de reporte SST</h3>
        <p>
          Comparte el enlace o imprime el QR para que cualquier persona reporte actos,
          condiciones inseguras, incidentes, accidentes o sugerencias sin iniciar sesión.
        </p>
        <code>{urlPublica}</code>

        <div className="public-report-publisher-actions">
          <button type="button" onClick={copiarEnlace}>
            <Copy size={17} /> Copiar enlace
          </button>
          <a href={urlPublica} target="_blank" rel="noopener noreferrer">
            <ExternalLink size={17} /> Abrir formulario
          </a>
          <button type="button" onClick={() => setMostrarQr((actual) => !actual)}>
            <QrCode size={17} /> {mostrarQr ? "Ocultar QR" : "Generar QR"}
          </button>
        </div>

        {mensaje && (
          <div className="public-report-publisher-message" role="status">
            <CheckCircle2 size={16} /> {mensaje}
          </div>
        )}
      </div>

      {mostrarQr && (
        <aside className="public-report-publisher-qr">
          <img src={urlQr} alt="Código QR del formulario público de reporte SST" />
          <a href={urlQr} target="_blank" rel="noopener noreferrer" download="qr_reporte_sst.png">
            <Download size={16} /> Descargar QR
          </a>
          <small>Listo para carteleras, recepción, talleres, bodegas y áreas comunes.</small>
        </aside>
      )}
    </section>
  );
}

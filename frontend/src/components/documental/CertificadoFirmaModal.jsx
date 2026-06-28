// ============================================================
// COMPONENTE: CertificadoFirmaModal
// FASE 1.8.4.3.10.5 - Certificado PDF Oficial
// Ruta: frontend/src/components/documental/CertificadoFirmaModal.jsx
// ============================================================

import React, { useMemo } from "react";
import { Download, FileCheck2, Fingerprint, Printer, ShieldCheck, X } from "lucide-react";

function formatearFecha(fecha) {
  if (!fecha) return "Sin fecha registrada";
  try {
    return new Intl.DateTimeFormat("es-CO", {
      day: "2-digit",
      month: "long",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(fecha));
  } catch {
    return fecha;
  }
}

function certificadoHtml(certificado) {
  const fecha = formatearFecha(certificado?.fecha_firma);
  return `<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <title>Certificado firma digital SST</title>
  <style>
    body{font-family:Arial,Helvetica,sans-serif;margin:0;padding:32px;background:#f1f5f9;color:#0f172a;}
    .sheet{max-width:850px;margin:0 auto;background:#fff;border:1px solid #dbeafe;border-radius:24px;padding:42px;box-shadow:0 20px 70px rgba(15,23,42,.12)}
    .top{display:flex;justify-content:space-between;gap:24px;border-bottom:4px solid #2563eb;padding-bottom:22px;margin-bottom:28px}
    .seal{width:92px;height:92px;border-radius:50%;display:grid;place-items:center;border:8px solid #dcfce7;color:#16a34a;font-weight:900}
    h1{margin:0;font-size:28px;letter-spacing:-.03em}.sub{color:#64748b;margin-top:8px}.badge{display:inline-block;margin-top:12px;background:#dcfce7;color:#166534;padding:8px 12px;border-radius:999px;font-weight:800;font-size:12px}
    .grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:26px 0}.item{border:1px solid #e2e8f0;border-radius:16px;padding:14px;background:#f8fafc}.item small{display:block;color:#64748b;text-transform:uppercase;font-weight:800;font-size:10px;letter-spacing:.08em}.item strong{display:block;margin-top:6px;font-size:15px}.hash{margin-top:24px;background:#0f172a;color:#dbeafe;border-radius:18px;padding:16px;word-break:break-all;font-size:12px}.footer{margin-top:30px;color:#64748b;font-size:12px;line-height:1.6}.sign{margin-top:40px;display:flex;justify-content:space-between;gap:24px}.line{flex:1;border-top:1px solid #94a3b8;padding-top:10px;text-align:center;color:#334155;font-weight:800}
    @media print{body{background:#fff;padding:0}.sheet{box-shadow:none;border:0;border-radius:0}.no-print{display:none}}
  </style>
</head>
<body>
  <main class="sheet">
    <section class="top">
      <div>
        <h1>Certificado Oficial de Firma Digital SST</h1>
        <div class="sub">Sistema de Gestión de Seguridad y Salud en el Trabajo · ERP SST PRO</div>
        <span class="badge">${certificado?.estado_firma || "CERTIFICADO"}</span>
      </div>
      <div class="seal">100%</div>
    </section>

    <p>Se certifica que el documento identificado a continuación registra una acción digital trazable dentro del módulo de Firma y Aprobación Digital SST.</p>

    <section class="grid">
      <div class="item"><small>Código documental</small><strong>${certificado?.codigo_documental || "N/A"}</strong></div>
      <div class="item"><small>Documento</small><strong>${certificado?.titulo || "N/A"}</strong></div>
      <div class="item"><small>Versión</small><strong>${certificado?.version || "N/A"}</strong></div>
      <div class="item"><small>Estado documento</small><strong>${certificado?.estado_documento || "N/A"}</strong></div>
      <div class="item"><small>Firmante</small><strong>${certificado?.nombre_firmante || "N/A"}</strong></div>
      <div class="item"><small>Cargo</small><strong>${certificado?.cargo_firmante || "N/A"}</strong></div>
      <div class="item"><small>Rol firmante</small><strong>${certificado?.rol_firmante || "N/A"}</strong></div>
      <div class="item"><small>Tipo acción</small><strong>${certificado?.tipo_accion || "N/A"}</strong></div>
      <div class="item"><small>Fecha firma</small><strong>${fecha}</strong></div>
      <div class="item"><small>IP origen</small><strong>${certificado?.ip_origen || "No registrada"}</strong></div>
    </section>

    <div class="hash"><strong>Hash SHA-256:</strong><br/>${certificado?.hash_firma || "Sin hash registrado"}</div>

    <div class="sign">
      <div class="line">Firma digital / Firmante</div>
      <div class="line">Validación ERP SST PRO</div>
    </div>

    <div class="footer">
      Este certificado es una evidencia documental interna del SG-SST. La trazabilidad incluye fecha, usuario, rol, estado, IP, navegador y hash de validación. Para efectos de auditoría, debe conservarse junto con el historial documental y las versiones del documento.
    </div>
  </main>
</body>
</html>`;
}

export default function CertificadoFirmaModal({ open, certificado, onClose }) {
  const html = useMemo(() => certificadoHtml(certificado), [certificado]);

  if (!open || !certificado) return null;

  const imprimir = () => {
    const win = window.open("", "_blank", "width=1000,height=900");
    if (!win) return;
    win.document.open();
    win.document.write(html);
    win.document.close();
    win.focus();
    setTimeout(() => win.print(), 450);
  };

  const descargarHtml = () => {
    const blob = new Blob([html], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `certificado_firma_${certificado.codigo_documental || certificado.firma_id || "sst"}.html`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="firma-modal-backdrop">
      <section className="firma-modal certificado-modal wide">
        <header className="firma-modal-header certificado-header">
          <div>
            <span>Certificado oficial SST</span>
            <h2>Certificado de Firma Digital</h2>
            <p>{certificado.codigo_documental} · {certificado.titulo}</p>
          </div>

          <button className="firma-icon-button" type="button" onClick={onClose} title="Cerrar">
            <X size={18} />
          </button>
        </header>

        <div className="certificado-preview">
          <div className="certificado-preview-top">
            <div>
              <span className="certificado-pill">ERP SST PRO</span>
              <h3>Certificado Oficial de Aprobación Documental</h3>
              <p>Sistema de Gestión de Seguridad y Salud en el Trabajo.</p>
            </div>
            <div className="certificado-seal"><ShieldCheck size={34} />100%</div>
          </div>

          <div className="certificado-grid">
            <div><small>Código</small><strong>{certificado.codigo_documental || "N/A"}</strong></div>
            <div><small>Documento</small><strong>{certificado.titulo || "N/A"}</strong></div>
            <div><small>Versión</small><strong>{certificado.version || "N/A"}</strong></div>
            <div><small>Estado</small><strong>{certificado.estado_documento || "N/A"}</strong></div>
            <div><small>Firmante</small><strong>{certificado.nombre_firmante || "N/A"}</strong></div>
            <div><small>Cargo</small><strong>{certificado.cargo_firmante || "N/A"}</strong></div>
            <div><small>Rol</small><strong>{certificado.rol_firmante || "N/A"}</strong></div>
            <div><small>Acción</small><strong>{certificado.tipo_accion || "N/A"}</strong></div>
            <div><small>Fecha</small><strong>{formatearFecha(certificado.fecha_firma)}</strong></div>
            <div><small>IP origen</small><strong>{certificado.ip_origen || "No registrada"}</strong></div>
          </div>

          {certificado.observaciones && (
            <div className="certificado-note">
              <FileCheck2 size={18} />
              <p>{certificado.observaciones}</p>
            </div>
          )}

          <div className="certificado-hash">
            <Fingerprint size={17} />
            <code>{certificado.hash_firma || "Sin hash registrado"}</code>
          </div>
        </div>

        <footer className="certificado-actions">
          <button className="firma-btn secondary" type="button" onClick={onClose}>Cerrar</button>
          <button className="firma-btn secondary" type="button" onClick={descargarHtml}>
            <Download size={17} /> Descargar HTML
          </button>
          <button className="firma-btn primary" type="button" onClick={imprimir}>
            <Printer size={17} /> Imprimir / Guardar PDF
          </button>
        </footer>
      </section>
    </div>
  );
}

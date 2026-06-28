// ============================================================
// COMPONENTE: WorkflowAprobacionVisual
// FASE 1.8.4.3.10.4.1 - Mejora Visual PRO
// Ruta: frontend/src/components/documental/WorkflowAprobacionVisual.jsx
// ============================================================

import React from "react";
import {
  CheckCircle2,
  CircleDashed,
  ClipboardCheck,
  FileText,
  PenLine,
  ShieldCheck,
  Stamp,
} from "lucide-react";

function normalizar(valor = "") {
  return String(valor || "").trim().toUpperCase();
}

function siNo(valor) {
  return valor === true || normalizar(valor) === "SI" || normalizar(valor) === "SÍ";
}

function calcularWorkflow(documento = {}) {
  const estado = normalizar(documento.estado);
  const revision = normalizar(documento.estado_revision);
  const firmaSst = siNo(documento.firmado_responsable_sst) || siNo(documento.firma_sst);
  const firmaGerencia = siNo(documento.firmado_gerencia) || siNo(documento.firma_gerencia);

  const creado = Boolean(documento.id);
  const revisado = ["EN_REVISION", "APROBADO", "VIGENTE", "RECHAZADO"].includes(revision) || firmaSst;
  const firmadoSst = firmaSst;
  const aprobadoGerencia = firmaGerencia || revision === "APROBADO" || estado === "APROBADO";
  const vigente = estado === "VIGENTE" && (aprobadoGerencia || firmadoSst);

  return [
    {
      key: "creado",
      title: "Creado",
      subtitle: "Documento registrado en biblioteca",
      active: creado,
      icon: FileText,
      accent: "blue",
    },
    {
      key: "revision",
      title: "Revisión SST",
      subtitle: revisado ? "Validado por SST" : "Pendiente de revisión",
      active: revisado,
      icon: ClipboardCheck,
      accent: "cyan",
    },
    {
      key: "firma_sst",
      title: "Firma SST",
      subtitle: firmadoSst ? "Responsable SST firmó" : "Firma pendiente",
      active: firmadoSst,
      icon: PenLine,
      accent: "green",
    },
    {
      key: "gerencia",
      title: "Gerencia",
      subtitle: aprobadoGerencia ? "Aprobación gerencial registrada" : "Pendiente de aprobación",
      active: aprobadoGerencia,
      icon: Stamp,
      accent: "purple",
    },
    {
      key: "vigente",
      title: "Vigente",
      subtitle: vigente ? "Documento controlado" : "Pendiente de vigencia",
      active: vigente,
      icon: ShieldCheck,
      accent: "dark",
    },
  ];
}

export default function WorkflowAprobacionVisual({ documento = {} }) {
  const pasos = calcularWorkflow(documento);
  const completados = pasos.filter((paso) => paso.active).length;
  const porcentaje = Math.round((completados / pasos.length) * 100);

  return (
    <div className="firma-workflow-enterprise-v2">
      <div className="firma-workflow-v2-header">
        <div>
          <span className="firma-chip-soft">Flujo documental certificado</span>
          <h4>{documento.codigo_documental || documento.codigo || "Documento SST"}</h4>
          <p>{documento.titulo || "Sin título registrado"}</p>
        </div>

        <div className="firma-progress-ring" style={{ "--progress": `${porcentaje}%` }}>
          <strong>{porcentaje}%</strong>
          <small>avance</small>
        </div>
      </div>

      <div className="firma-workflow-v2-steps">
        {pasos.map((paso, index) => {
          const Icon = paso.icon;
          const completo = paso.active;
          const lineaActiva = completo && pasos[index + 1]?.active;

          return (
            <React.Fragment key={paso.key}>
              <article className={`firma-workflow-v2-card ${paso.accent} ${completo ? "active" : "pending"}`}>
                <div className="firma-workflow-v2-icon">
                  {completo ? <CheckCircle2 size={22} /> : <CircleDashed size={22} />}
                </div>

                <div className="firma-workflow-v2-content">
                  <span>Paso {index + 1}</span>
                  <h5><Icon size={15} /> {paso.title}</h5>
                  <p>{paso.subtitle}</p>
                </div>
              </article>

              {index < pasos.length - 1 && (
                <div className={`firma-workflow-v2-line ${lineaActiva ? "active" : ""}`} />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}

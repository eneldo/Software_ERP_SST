// ============================================================
// EVIDENCIAS INTELIGENTES PANEL ENTERPRISE UI
// ERP SST PRO
// FASE 1.1.8.7.5.2 PRO — Mejora visual de evidencias
// Archivo: frontend/src/components/medidas/EvidenciasInteligentesPanel.jsx
// ============================================================

import {
  BrainCircuit,
  CalendarDays,
  Download,
  ExternalLink,
  Eye,
  FileText,
  Image as ImageIcon,
  RefreshCcw,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { useMemo, useState } from "react";

import ImageViewerModal from "../common/ImageViewerModal";
import { getBestImageUrl, getDownloadUrl, isImageEvidence } from "../../utils/fileUrl";

import "../../styles/medidas-inteligentes.css";

function formatBytes(bytes) {
  const size = Number(bytes || 0);
  if (!size) return "Peso no registrado";
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}

function formatDate(value) {
  if (!value) return "Sin fecha";
  try {
    return new Date(value).toLocaleDateString("es-CO", {
      year: "numeric",
      month: "short",
      day: "2-digit",
    });
  } catch {
    return String(value);
  }
}

function normalizeChip(value) {
  const raw = String(value || "EVIDENCIA").replaceAll("_", " ").trim();
  return raw || "EVIDENCIA";
}

function getEvidenceAccent(item) {
  const origen = String(item?.origen_visual || item?.modulo || "").toUpperCase();
  const tipo = String(item?.tipo || "").toUpperCase();
  if (origen.includes("ORIGEN") || origen.includes("INSPECCION") || origen.includes("HALLAZGO")) return "origin";
  if (tipo.includes("DESPUES") || tipo.includes("CORRECTIVA")) return "correctiva";
  if (tipo.includes("ANTES")) return "antes";
  if (tipo.includes("DURANTE")) return "durante";
  return "medida";
}

function buildViewerItems(items = []) {
  return items
    .filter((item) => isImageEvidence(item) && getBestImageUrl(item))
    .map((item) => ({
      id: item.id,
      src: getBestImageUrl(item),
      downloadUrl: getDownloadUrl(item),
      title: item?.nombre_original || item?.nombre_archivo || "Evidencia SST",
      subtitle: `${normalizeChip(item?.origen_visual || item?.modulo)} · ${normalizeChip(item?.tipo || item?.mime_type)}`,
      item,
    }));
}

function EvidenceSummary({ total, medidaTotal, origenTotal }) {
  return (
    <div className="mci-summary-enterprise">
      <div className="mci-summary-icon">
        <BrainCircuit size={25} />
      </div>
      <div>
        <span>Evidencias inteligentes</span>
        <strong>{total} archivo(s)</strong>
        <p>Análisis visual y trazabilidad documental de la medida.</p>
      </div>
      <div className="mci-summary-pills">
        <span>{medidaTotal} medida</span>
        <span>{origenTotal} origen</span>
      </div>
    </div>
  );
}

function EvidenceCard({ item, viewerItems, onView }) {
  const isImage = isImageEvidence(item);
  const imageSrc = getBestImageUrl(item);
  const downloadUrl = getDownloadUrl(item);
  const title = item?.nombre_original || item?.nombre_archivo || "Evidencia SST";
  const accent = getEvidenceAccent(item);
  const extension = String(item?.extension || item?.nombre_archivo?.split(".").pop() || "FILE").toUpperCase();
  const viewerIndex = viewerItems.findIndex((viewer) => viewer.id === item.id);

  function openViewer() {
    if (!isImage || !imageSrc) return;
    onView({ items: viewerItems, index: viewerIndex >= 0 ? viewerIndex : 0 });
  }

  return (
    <article className={`mci-evidence-pro ${accent}`}>
      <button
        className={`mci-evidence-media ${isImage ? "is-clickable" : ""}`}
        type="button"
        onClick={openViewer}
        title={isImage ? "Ver imagen" : "Archivo"}
      >
        {isImage && imageSrc ? (
          <img
            src={imageSrc}
            alt={title}
            loading="lazy"
            onError={(event) => {
              event.currentTarget.style.display = "none";
              event.currentTarget.parentElement?.classList.add("image-error");
            }}
          />
        ) : (
          <div className="mci-file-preview">
            {isImage ? <ImageIcon size={34} /> : <FileText size={34} />}
          </div>
        )}
        <span className="mci-file-ext">{extension}</span>
        {isImage && (
          <span className="mci-media-hover">
            <Eye size={18} />
            Ver
          </span>
        )}
      </button>

      <div className="mci-evidence-info">
        <div className="mci-evidence-title-row">
          <strong title={title}>{title}</strong>
          <span className={`mci-chip ${accent}`}>
            <ShieldCheck size={13} />
            {accent === "origin" ? "ORIGEN" : "MEDIDA"}
          </span>
        </div>

        <p>{item?.descripcion || item?.nombre_archivo || "Evidencia documental SST"}</p>

        <div className="mci-chip-row">
          <span>{normalizeChip(item?.tipo || item?.mime_type)}</span>
          <span>{normalizeChip(item?.modulo)}</span>
        </div>

        <div className="mci-evidence-meta">
          <span>
            <CalendarDays size={13} />
            {formatDate(item?.fecha_creacion)}
          </span>
          <span>{formatBytes(item?.tamano_bytes)}</span>
        </div>

        <div className="mci-evidence-actions-pro">
          {isImage && imageSrc && (
            <button type="button" onClick={openViewer}>
              <Eye size={16} />
              Ver
            </button>
          )}
          {downloadUrl && (
            <a href={downloadUrl} target="_blank" rel="noreferrer" download>
              <Download size={16} />
              Descargar
            </a>
          )}
          {downloadUrl && (
            <a href={downloadUrl} target="_blank" rel="noreferrer">
              <ExternalLink size={16} />
              Abrir
            </a>
          )}
        </div>
      </div>
    </article>
  );
}

function EvidenceSection({ title, subtitle, items, viewerItems, onView, emptyText }) {
  return (
    <section className="mci-evidence-section-pro">
      <div className="mci-section-title">
        <div>
          <h4>{title}</h4>
          <p>{subtitle}</p>
        </div>
        <span>{items.length}</span>
      </div>

      <div className="mci-evidence-masonry">
        {items.map((item) => (
          <EvidenceCard key={`${title}-${item.id}`} item={item} viewerItems={viewerItems} onView={onView} />
        ))}
        {!items.length && (
          <div className="mci-empty-pro">
            <Sparkles size={18} />
            {emptyText}
          </div>
        )}
      </div>
    </section>
  );
}

export default function EvidenciasInteligentesPanel({ data, loading, onRefresh }) {
  const [viewerState, setViewerState] = useState(null);
  const medida = data?.evidencias_medida || [];
  const origen = data?.evidencias_origen || [];
  const allImages = useMemo(() => buildViewerItems([...medida, ...origen]), [medida, origen]);

  return (
    <section className="mci-card mci-card-evidencias-pro">
      <div className="mci-card-header mci-evidencias-header-pro">
        <div>
          <span>Evidencias inteligentes</span>
          <h3>{(medida.length + origen.length) || 0} archivo(s)</h3>
        </div>
        <button className="mci-icon-btn" onClick={onRefresh} disabled={loading} type="button" title="Actualizar evidencias">
          <RefreshCcw size={16} />
        </button>
      </div>

      <EvidenceSummary total={medida.length + origen.length} medidaTotal={medida.length} origenTotal={origen.length} />

      <EvidenceSection
        title="Evidencias de la medida"
        subtitle="Archivos cargados durante la gestión correctiva."
        items={medida}
        viewerItems={allImages}
        onView={setViewerState}
        emptyText="No hay evidencias propias de la medida."
      />

      <EvidenceSection
        title="Evidencia origen"
        subtitle="Archivos heredados desde inspección, hallazgo, incidente o reporte SST."
        items={origen}
        viewerItems={allImages}
        onView={setViewerState}
        emptyText="No hay evidencia origen relacionada."
      />

      <ImageViewerModal
        open={Boolean(viewerState)}
        items={viewerState?.items || []}
        initialIndex={viewerState?.index || 0}
        image={viewerState?.items?.[viewerState?.index || 0]}
        onClose={() => setViewerState(null)}
      />
    </section>
  );
}

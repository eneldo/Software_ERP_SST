// ============================================================
// VISOR ENTERPRISE DE IMÁGENES
// ERP SST PRO
// FASE 1.1.8.7.5.2 PRO — Mejora visual de evidencias
// Archivo: frontend/src/components/common/ImageViewerModal.jsx
// ============================================================

import {
  ChevronLeft,
  ChevronRight,
  Download,
  Maximize2,
  Minus,
  Plus,
  RotateCcw,
  X,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import "../../styles/image-viewer-modal.css";

export default function ImageViewerModal({ open, image, items = [], initialIndex = 0, onClose }) {
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [index, setIndex] = useState(initialIndex || 0);

  const gallery = items.length ? items : image ? [image] : [];
  const current = gallery[index] || image || {};
  const src = current?.src || "";
  const title = current?.title || "Evidencia SST";
  const subtitle = current?.subtitle || current?.item?.tipo || "";

  useEffect(() => {
    if (open) {
      setZoom(1);
      setRotation(0);
      setIndex(initialIndex || 0);
    }
  }, [open, src, initialIndex]);

  useEffect(() => {
    function handleKeyDown(event) {
      if (!open) return;
      if (event.key === "Escape") onClose?.();
      if (event.key === "+") setZoom((z) => Math.min(z + 0.15, 4));
      if (event.key === "-") setZoom((z) => Math.max(z - 0.15, 0.3));
      if (event.key === "ArrowRight") next();
      if (event.key === "ArrowLeft") prev();
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, index, gallery.length, onClose]);

  const transform = useMemo(() => `scale(${zoom}) rotate(${rotation}deg)`, [zoom, rotation]);

  if (!open || !src) return null;

  function next() {
    if (gallery.length <= 1) return;
    setZoom(1);
    setRotation(0);
    setIndex((value) => (value + 1) % gallery.length);
  }

  function prev() {
    if (gallery.length <= 1) return;
    setZoom(1);
    setRotation(0);
    setIndex((value) => (value - 1 + gallery.length) % gallery.length);
  }

  async function fullscreen() {
    const element = document.querySelector(".ivm-image-stage");
    if (element?.requestFullscreen) await element.requestFullscreen();
  }

  function handleWheel(event) {
    if (!event.ctrlKey) return;
    event.preventDefault();
    if (event.deltaY < 0) setZoom((z) => Math.min(z + 0.12, 4));
    else setZoom((z) => Math.max(z - 0.12, 0.3));
  }

  const downloadUrl = current?.downloadUrl || current?.src;

  return (
    <div className="ivm-backdrop" onClick={onClose}>
      <div className="ivm-modal ivm-modal-pro" onClick={(event) => event.stopPropagation()}>
        <div className="ivm-header">
          <div>
            <span>Visor Enterprise de evidencia SST</span>
            <h3>{title}</h3>
            {subtitle && <p>{subtitle}</p>}
          </div>
          <button className="ivm-icon-btn danger" onClick={onClose} type="button" title="Cerrar">
            <X size={18} />
          </button>
        </div>

        <div className="ivm-toolbar">
          <button type="button" onClick={() => setZoom((z) => Math.max(z - 0.15, 0.3))}>
            <Minus size={16} />
            Zoom -
          </button>
          <strong>{Math.round(zoom * 100)}%</strong>
          <button type="button" onClick={() => setZoom((z) => Math.min(z + 0.15, 4))}>
            <Plus size={16} />
            Zoom +
          </button>
          <button type="button" onClick={() => setRotation((r) => r + 90)}>
            <RotateCcw size={16} />
            Girar
          </button>
          <button type="button" onClick={fullscreen}>
            <Maximize2 size={16} />
            Pantalla
          </button>
          <a href={downloadUrl} target="_blank" rel="noreferrer" download>
            <Download size={16} />
            Descargar
          </a>
        </div>

        <div className="ivm-body-pro">
          {gallery.length > 1 && (
            <button className="ivm-nav ivm-prev" onClick={prev} type="button" title="Anterior">
              <ChevronLeft size={24} />
            </button>
          )}

          <div className="ivm-image-stage" onWheel={handleWheel}>
            <img src={src} alt={title} style={{ transform }} />
          </div>

          {gallery.length > 1 && (
            <button className="ivm-nav ivm-next" onClick={next} type="button" title="Siguiente">
              <ChevronRight size={24} />
            </button>
          )}
        </div>

        {gallery.length > 1 && (
          <div className="ivm-footer">
            <span>
              Imagen {index + 1} de {gallery.length}
            </span>
            <div className="ivm-thumbs">
              {gallery.map((item, itemIndex) => (
                <button
                  type="button"
                  key={`${item.id || item.src}-${itemIndex}`}
                  className={itemIndex === index ? "active" : ""}
                  onClick={() => {
                    setIndex(itemIndex);
                    setZoom(1);
                    setRotation(0);
                  }}
                  title={item.title || `Imagen ${itemIndex + 1}`}
                >
                  <img src={item.src} alt={item.title || `Imagen ${itemIndex + 1}`} />
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

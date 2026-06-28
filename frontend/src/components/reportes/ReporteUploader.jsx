// ============================================================
// UPLOADER EVIDENCIAS REPORTES SST
// FASE 1.1.25.6
// Archivo: frontend/src/components/reportes/ReporteUploader.jsx
// ============================================================

import React, { useRef, useState } from "react";
import { UploadCloud, X } from "lucide-react";

export default function ReporteUploader({ onUpload, loading = false, multiple = true }) {
  const inputRef = useRef(null);
  const [files, setFiles] = useState([]);
  const handleFiles = (list) => setFiles(Array.from(list || []));
  const submit = async () => {
    if (!files.length || !onUpload) return;
    await onUpload(files);
    setFiles([]);
    if (inputRef.current) inputRef.current.value = "";
  };
  return (
    <div className="rep-uploader">
      <input ref={inputRef} type="file" multiple={multiple} accept="image/*,video/*,audio/*,.pdf" onChange={(e) => handleFiles(e.target.files)} />
      <div className="rep-uploader-box" onClick={() => inputRef.current?.click()}>
        <UploadCloud size={24} />
        <strong>Subir evidencias inteligentes</strong>
        <small>Imágenes se comprimen automáticamente. También acepta PDF, video y audio.</small>
      </div>
      {!!files.length && (
        <div className="rep-uploader-list">
          {files.map((f, idx) => <span key={`${f.name}-${idx}`}>{f.name}<button type="button" onClick={() => setFiles(files.filter((_, i) => i !== idx))}><X size={12} /></button></span>)}
        </div>
      )}
      <button type="button" className="rep-uploader-btn" disabled={!files.length || loading} onClick={submit}>{loading ? "Subiendo..." : "Guardar evidencias"}</button>
    </div>
  );
}

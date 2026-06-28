// ============================================================
// PÁGINA AUDITORÍA INTEGRAL DE EVIDENCIAS
// ERP SST PRO ENTERPRISE
// FASE 35.4
// Archivo: frontend/src/pages/admin/AuditoriaEvidenciasPage.jsx
// ============================================================

import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Database,
  FileImage,
  FileSearch,
  FolderCheck,
  HardDrive,
  Image,
  RefreshCcw,
  Search,
  ShieldCheck,
} from "lucide-react";

import {
  auditarEvidencias,
  listarModulosEvidencias,
  obtenerHealthEvidencias,
} from "../../api/auditoriaEvidenciasApi";

import "../../styles/auditoria-evidencias.css";

const DEFAULT_FILTERS = {
  empresa_id: "",
  modulo: "",
  solo_hallazgos: false,
  activo: true,
  limit: 500,
};

function formatBytes(value) {
  const n = Number(value || 0);
  if (n <= 0) return "0 KB";
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 / 1024).toFixed(2)} MB`;
}

function StatusBadge({ ok, labelOk = "OK", labelFail = "Pendiente" }) {
  return (
    <span className={`ae-badge ${ok ? "ok" : "warn"}`}>
      {ok ? <CheckCircle2 size={14} /> : <AlertTriangle size={14} />}
      {ok ? labelOk : labelFail}
    </span>
  );
}

export default function AuditoriaEvidenciasPage() {
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState(null);
  const [modulos, setModulos] = useState([]);
  const [response, setResponse] = useState({
    resumen: {},
    evidencias: [],
    recomendaciones: [],
  });
  const [error, setError] = useState("");

  const resumen = response?.resumen || {};
  const evidencias = response?.evidencias || [];

  const calidad = useMemo(() => {
    const total = Number(resumen.total || 0);
    if (!total) return 100;
    const hallazgos = Number(resumen.con_hallazgos || 0);
    return Math.max(0, Math.round(100 - (hallazgos / total) * 100));
  }, [resumen]);

  async function cargarDatos(customFilters = filters) {
    setLoading(true);
    setError("");

    try {
      const [healthData, modulosData, auditoriaData] = await Promise.all([
        obtenerHealthEvidencias(),
        listarModulosEvidencias(),
        auditarEvidencias(customFilters),
      ]);

      setHealth(healthData);
      setModulos(modulosData?.modulos_encontrados || []);
      setResponse(auditoriaData);
    } catch (err) {
      console.error(err);
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "No fue posible cargar la auditoría de evidencias."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    cargarDatos(DEFAULT_FILTERS);
  }, []);

  function onFilterChange(name, value) {
    setFilters((prev) => ({
      ...prev,
      [name]: value,
    }));
  }

  function aplicarFiltros(event) {
    event.preventDefault();
    cargarDatos(filters);
  }

  function limpiarFiltros() {
    setFilters(DEFAULT_FILTERS);
    cargarDatos(DEFAULT_FILTERS);
  }

  return (
    <section className="auditoria-evidencias-page">
      <div className="ae-hero">
        <div>
          <span className="ae-kicker">FASE 35.4 · HARDENING · EVIDENCIAS</span>
          <h1>Auditoría Integral de Evidencias</h1>
          <p>
            Verificación centralizada de archivos físicos, previews, miniaturas, optimización WEBP,
            módulos asociados y trazabilidad documental del ERP SST.
          </p>
        </div>

        <button className="ae-btn primary" onClick={() => cargarDatos()} disabled={loading}>
          <RefreshCcw size={18} />
          {loading ? "Auditando..." : "Actualizar auditoría"}
        </button>
      </div>

      {error && (
        <div className="ae-alert danger">
          <AlertTriangle size={18} />
          {error}
        </div>
      )}

      <div className="ae-health-card">
        <div className="ae-health-title">
          <ShieldCheck size={20} />
          Estado de almacenamiento
        </div>
        <div className="ae-health-grid">
          <div>
            <span>UPLOAD_DIR</span>
            <strong>{health?.upload_root || "Validando..."}</strong>
          </div>
          <StatusBadge ok={Boolean(health?.ok)} labelOk="Disponible" labelFail="No disponible" />
        </div>

        <div className="ae-folder-grid">
          {Object.entries(health?.carpetas || {}).map(([key, ok]) => (
            <span key={key} className={`ae-folder ${ok ? "ok" : "warn"}`}>
              <FolderCheck size={14} />
              {key}
            </span>
          ))}
        </div>
      </div>

      <div className="ae-kpi-grid">
        <article className="ae-kpi">
          <Database size={22} />
          <span>Total evidencias</span>
          <strong>{resumen.total || 0}</strong>
        </article>

        <article className="ae-kpi">
          <FileImage size={22} />
          <span>Imágenes</span>
          <strong>{resumen.imagenes || 0}</strong>
        </article>

        <article className="ae-kpi">
          <Image size={22} />
          <span>WEBP</span>
          <strong>{resumen.webp || 0}</strong>
        </article>

        <article className="ae-kpi danger">
          <AlertTriangle size={22} />
          <span>Con hallazgos</span>
          <strong>{resumen.con_hallazgos || 0}</strong>
        </article>

        <article className="ae-kpi">
          <HardDrive size={22} />
          <span>Peso total</span>
          <strong>{resumen.peso_total_mb || 0} MB</strong>
        </article>

        <article className="ae-kpi quality">
          <ShieldCheck size={22} />
          <span>Calidad</span>
          <strong>{calidad}%</strong>
        </article>
      </div>

      <form className="ae-filters" onSubmit={aplicarFiltros}>
        <div className="ae-filter">
          <label>Empresa ID</label>
          <input
            type="number"
            min="1"
            value={filters.empresa_id}
            onChange={(e) => onFilterChange("empresa_id", e.target.value)}
            placeholder="Todas"
          />
        </div>

        <div className="ae-filter">
          <label>Módulo</label>
          <select
            value={filters.modulo}
            onChange={(e) => onFilterChange("modulo", e.target.value)}
          >
            <option value="">Todos</option>
            {modulos.map((item) => (
              <option key={item.modulo} value={item.modulo}>
                {item.modulo} ({item.total})
              </option>
            ))}
          </select>
        </div>

        <div className="ae-filter">
          <label>Estado</label>
          <select
            value={String(filters.activo)}
            onChange={(e) => {
              const value = e.target.value;
              onFilterChange("activo", value === "todos" ? "" : value === "true");
            }}
          >
            <option value="true">Solo activas</option>
            <option value="false">Solo inactivas</option>
            <option value="todos">Todas</option>
          </select>
        </div>

        <div className="ae-filter">
          <label>Límite</label>
          <input
            type="number"
            min="1"
            max="5000"
            value={filters.limit}
            onChange={(e) => onFilterChange("limit", e.target.value)}
          />
        </div>

        <label className="ae-check">
          <input
            type="checkbox"
            checked={filters.solo_hallazgos}
            onChange={(e) => onFilterChange("solo_hallazgos", e.target.checked)}
          />
          Solo hallazgos
        </label>

        <button className="ae-btn primary" type="submit" disabled={loading}>
          <Search size={16} />
          Filtrar
        </button>

        <button className="ae-btn ghost" type="button" onClick={limpiarFiltros}>
          Limpiar
        </button>
      </form>

      <div className="ae-recomendaciones">
        {(response?.recomendaciones || []).map((rec, index) => (
          <div key={`${rec}-${index}`} className="ae-alert">
            <FileSearch size={18} />
            {rec}
          </div>
        ))}
      </div>

      <div className="ae-table-card">
        <div className="ae-table-header">
          <h2>Detalle de evidencias</h2>
          <span>{evidencias.length} registros mostrados</span>
        </div>

        <div className="ae-table-wrap">
          <table className="ae-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Módulo</th>
                <th>Archivo</th>
                <th>Tipo</th>
                <th>Peso</th>
                <th>Físico</th>
                <th>WEBP</th>
                <th>Preview</th>
                <th>Thumb</th>
                <th>Hallazgos</th>
              </tr>
            </thead>
            <tbody>
              {evidencias.map((item) => (
                <tr key={item.id} className={item.hallazgos?.length ? "has-findings" : ""}>
                  <td>#{item.id}</td>
                  <td>
                    <strong>{item.modulo || "SIN MÓDULO"}</strong>
                    <small>Ref. {item.referencia_id || "—"}</small>
                  </td>
                  <td>
                    <a href={item.url} target="_blank" rel="noreferrer">
                      {item.nombre_original || item.nombre_archivo || "Sin nombre"}
                    </a>
                    <small>{item.mime_type || item.extension || "Sin tipo"}</small>
                  </td>
                  <td>{item.tipo || "—"}</td>
                  <td>{formatBytes(item.tamano_bytes)}</td>
                  <td><StatusBadge ok={item.existe_archivo} /></td>
                  <td><StatusBadge ok={item.optimizada_webp} /></td>
                  <td><StatusBadge ok={item.existe_preview} /></td>
                  <td><StatusBadge ok={item.existe_thumbnail} /></td>
                  <td>
                    {item.hallazgos?.length ? (
                      <ul className="ae-findings">
                        {item.hallazgos.map((h) => (
                          <li key={h}>{h}</li>
                        ))}
                      </ul>
                    ) : (
                      <span className="ae-ok-text">Sin hallazgos</span>
                    )}
                  </td>
                </tr>
              ))}

              {!evidencias.length && (
                <tr>
                  <td colSpan="10" className="ae-empty">
                    {loading ? "Cargando auditoría..." : "No hay evidencias para los filtros seleccionados."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

// ============================================================
// USO DEL ARCHIVO:
// Portal Ejecutivo de Historial Documental SST Enterprise.
// Permite consultar, crear, comparar, restaurar y visualizar
// versiones documentales de Revisión por la Dirección SST.
//
// Incluye:
// - Timeline visual de versiones
// - Semáforo documental
// - KPIs ejecutivos
// - Comparador profesional
// - Detalle JSON del snapshot
// - Restauración segura
//
// Ubicación:
// frontend/src/pages/verificar/RevisionVersionesPage.jsx
//
// FASE 1.8.4.3.8 — Portal Ejecutivo Historial Documental
// ============================================================

import React, { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  ClipboardList,
  Code2,
  Copy,
  Eye,
  FileClock,
  GitCompare,
  History,
  RefreshCcw,
  RotateCcw,
  Save,
  Search,
  ShieldCheck,
} from "lucide-react";

import AdminLayout from "../../layouts/AdminLayout";

import {
  compararVersiones,
  crearSnapshotManual,
  listarVersionesRevision,
  obtenerDetalleVersion,
  restaurarVersion,
} from "../../api/revisionVersionApi";

import "../../styles/revision-versiones.css";

function formatearFecha(fecha) {
  if (!fecha) return "Sin fecha";

  try {
    return new Date(fecha).toLocaleString("es-CO");
  } catch {
    return fecha;
  }
}

function copiarTexto(texto) {
  navigator.clipboard.writeText(texto || "");
}

function obtenerEstadoDocumental(version, index) {
  const accion = String(version?.accion || "").toUpperCase();

  if (accion.includes("APROBADA") || accion.includes("OFICIAL")) {
    return "OFICIAL";
  }

  if (accion.includes("ANULADA")) {
    return "ANULADA";
  }

  if (accion.includes("CREACION") || accion.includes("SNAPSHOT_MANUAL")) {
    return index === 0 ? "BORRADOR" : "HISTORICA";
  }

  return index === 0 ? "ACTUAL" : "HISTORICA";
}

function estadoClass(estado) {
  if (estado === "OFICIAL") return "estado-oficial";
  if (estado === "BORRADOR") return "estado-borrador";
  if (estado === "ANULADA") return "estado-anulada";
  return "estado-historica";
}

function valorLegible(valor) {
  if (valor === null || valor === undefined || valor === "") return "Sin dato";

  if (typeof valor === "object") {
    return JSON.stringify(valor, null, 2);
  }

  return String(valor);
}

export default function RevisionVersionesPage() {
  const [revisionId, setRevisionId] = useState("1");
  const [versiones, setVersiones] = useState([]);
  const [detalle, setDetalle] = useState(null);
  const [comparacion, setComparacion] = useState(null);

  const [versionOrigen, setVersionOrigen] = useState("");
  const [versionDestino, setVersionDestino] = useState("");
  const [observacion, setObservacion] = useState("Snapshot manual desde portal");

  const [loading, setLoading] = useState(false);
  const [loadingDetalle, setLoadingDetalle] = useState(false);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");

  const versionesOrdenadas = useMemo(() => {
    return [...versiones].sort((a, b) => b.version_numero - a.version_numero);
  }, [versiones]);

  const versionesTimeline = useMemo(() => {
    return [...versiones].sort((a, b) => a.version_numero - b.version_numero);
  }, [versiones]);

  const totalCambios = useMemo(() => {
    if (!comparacion?.diferencias) return 0;
    return Object.keys(comparacion.diferencias).length;
  }, [comparacion]);

  const ultimaVersion = versionesOrdenadas[0];

  const snapshotsAutomaticos = useMemo(() => {
    return versiones.filter((v) => String(v.accion || "").includes("AUTOMATICO"))
      .length;
  }, [versiones]);

  const snapshotsManuales = useMemo(() => {
    return versiones.filter((v) => String(v.accion || "").includes("MANUAL"))
      .length;
  }, [versiones]);

  const cargarVersiones = async () => {
    if (!revisionId) {
      setError("Debe ingresar el ID de la revisión.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setOk("");
      setDetalle(null);
      setComparacion(null);

      const data = await listarVersionesRevision(revisionId);
      setVersiones(data || []);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "No fue posible cargar el historial de versiones."
      );
    } finally {
      setLoading(false);
    }
  };

  const verDetalle = async (versionId) => {
    try {
      setLoadingDetalle(true);
      setError("");
      setComparacion(null);

      const data = await obtenerDetalleVersion(versionId);
      setDetalle(data);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "No fue posible cargar el detalle de la versión."
      );
    } finally {
      setLoadingDetalle(false);
    }
  };

  const crearSnapshot = async () => {
    try {
      setLoading(true);
      setError("");
      setOk("");

      const data = await crearSnapshotManual(revisionId, observacion);
      setOk(`Snapshot creado correctamente: ${data.codigo_version}`);
      await cargarVersiones();
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "No fue posible crear el snapshot manual."
      );
    } finally {
      setLoading(false);
    }
  };

  const comparar = async () => {
    if (!versionOrigen || !versionDestino) {
      setError("Debe seleccionar versión origen y versión destino.");
      return;
    }

    if (versionOrigen === versionDestino) {
      setError("Seleccione dos versiones diferentes para comparar.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setOk("");
      setDetalle(null);

      const data = await compararVersiones(versionOrigen, versionDestino);
      setComparacion(data);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "No fue posible comparar las versiones."
      );
    } finally {
      setLoading(false);
    }
  };

  const restaurar = async (version) => {
    const confirmar = window.confirm(
      `¿Desea restaurar la versión V${version.version_numero}?\n\n` +
        "La versión actual NO será eliminada.\n" +
        "El sistema generará automáticamente una nueva versión documental."
    );

    if (!confirmar) return;

    try {
      setLoading(true);
      setError("");
      setOk("");

      const data = await restaurarVersion(
        version.id,
        `Restauración desde ${version.codigo_version}`
      );

      setOk(`Versión restaurada correctamente. Nueva versión: ${data.codigo_version}`);
      await cargarVersiones();
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "No fue posible restaurar la versión. Verifique si la revisión está bloqueada legalmente."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarVersiones();
  }, []);

  return (
    <AdminLayout>
      <main className="rv-page">
        <section className="rv-hero">
          <div>
            <span>ISO 45001 · VERSIONADO DOCUMENTAL</span>
            <h1>Historial de Versiones SST Enterprise</h1>
            <p>
              Consulte snapshots, compare cambios, recupere versiones anteriores
              y mantenga trazabilidad documental completa de la Revisión por la Dirección.
            </p>
          </div>

          <div className="rv-hero-badge">
            <ShieldCheck size={28} />
            <strong>Versionado PRO</strong>
            <small>Auditoría documental</small>
          </div>
        </section>

        {error && (
          <div className="rv-alert error">
            <AlertTriangle size={18} />
            {error}
          </div>
        )}

        {ok && (
          <div className="rv-alert success">
            <CheckCircle2 size={18} />
            {ok}
          </div>
        )}

        <section className="rv-toolbar">
          <label>
            ID Revisión
            <input
              type="number"
              value={revisionId}
              onChange={(e) => setRevisionId(e.target.value)}
              placeholder="Ej: 1"
            />
          </label>

          <label className="wide">
            Observación snapshot
            <input
              value={observacion}
              onChange={(e) => setObservacion(e.target.value)}
              placeholder="Observación para el snapshot"
            />
          </label>

          <button type="button" onClick={cargarVersiones} disabled={loading}>
            <RefreshCcw size={17} />
            Cargar
          </button>

          <button
            type="button"
            className="primary"
            onClick={crearSnapshot}
            disabled={loading}
          >
            <Save size={17} />
            Crear Snapshot
          </button>
        </section>

        <section className="rv-kpi-grid">
          <article>
            <History />
            <span>Total versiones</span>
            <strong>{versiones.length}</strong>
          </article>

          <article>
            <FileClock />
            <span>Última versión</span>
            <strong>{ultimaVersion?.codigo_version || "N/A"}</strong>
          </article>

          <article>
            <ClipboardList />
            <span>Snapshots manuales</span>
            <strong>{snapshotsManuales}</strong>
          </article>

          <article>
            <GitCompare />
            <span>Diferencias activas</span>
            <strong>{totalCambios}</strong>
          </article>
        </section>

        {versionesTimeline.length > 0 && (
          <section className="rv-timeline">
            {versionesTimeline.map((version, index) => (
              <div key={version.id} className="rv-timeline-item">
                <div className="rv-timeline-dot">V{version.version_numero}</div>

                <div className="rv-timeline-info">
                  <strong>{version.codigo_version}</strong>
                  <span>{version.accion}</span>
                  <small>{formatearFecha(version.fecha_creacion)}</small>
                </div>

                {index !== versionesTimeline.length - 1 && (
                  <div className="rv-timeline-line" />
                )}
              </div>
            ))}
          </section>
        )}

        <section className="rv-main-grid">
          <article className="rv-panel rv-list-panel">
            <div className="rv-panel-title">
              <History size={20} />
              <div>
                <h2>Historial documental</h2>
                <p>Versiones disponibles para la revisión #{revisionId}</p>
              </div>
            </div>

            <div className="rv-version-list">
              {loading && <p className="rv-muted">Cargando versiones...</p>}

              {!loading && versionesOrdenadas.length === 0 && (
                <p className="rv-muted">No hay versiones registradas.</p>
              )}

              {versionesOrdenadas.map((version, index) => {
                const estado = obtenerEstadoDocumental(version, index);

                return (
                  <div
                    key={version.id}
                    className={`rv-version-card ${
                      detalle?.id === version.id ? "active" : ""
                    }`}
                  >
                    <div className="rv-version-head">
                      <div>
                        <strong>{version.codigo_version}</strong>
                        <span>{version.accion}</span>
                      </div>

                      <em>V{version.version_numero}</em>
                    </div>

                    <span className={estadoClass(estado)}>{estado}</span>

                    <p>{version.observacion || "Sin observación"}</p>

                    <small>{formatearFecha(version.fecha_creacion)}</small>

                    <div className="rv-version-actions">
                      <button type="button" onClick={() => verDetalle(version.id)}>
                        <Eye size={15} />
                        Ver
                      </button>

                      <button type="button" onClick={() => restaurar(version)}>
                        <RotateCcw size={15} />
                        Restaurar
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </article>

          <section className="rv-content">
            <article className="rv-panel">
              <div className="rv-panel-title">
                <GitCompare size={20} />
                <div>
                  <h2>Comparar versiones</h2>
                  <p>Seleccione dos versiones para identificar cambios.</p>
                </div>
              </div>

              <div className="rv-compare-form">
                <label>
                  Versión origen
                  <select
                    value={versionOrigen}
                    onChange={(e) => setVersionOrigen(e.target.value)}
                  >
                    <option value="">Seleccione</option>
                    {versionesOrdenadas.map((v) => (
                      <option key={v.id} value={v.id}>
                        {v.codigo_version}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Versión destino
                  <select
                    value={versionDestino}
                    onChange={(e) => setVersionDestino(e.target.value)}
                  >
                    <option value="">Seleccione</option>
                    {versionesOrdenadas.map((v) => (
                      <option key={v.id} value={v.id}>
                        {v.codigo_version}
                      </option>
                    ))}
                  </select>
                </label>

                <button type="button" className="primary" onClick={comparar}>
                  <Search size={17} />
                  Comparar
                </button>
              </div>
            </article>

            {comparacion && (
              <article className="rv-panel">
                <div className="rv-panel-title between">
                  <div className="rv-title-inline">
                    <GitCompare size={20} />
                    <div>
                      <h2>Comparador ejecutivo</h2>
                      <p>
                        V{comparacion.version_origen} vs V
                        {comparacion.version_destino}
                      </p>
                    </div>
                  </div>

                  <strong className="rv-pill">{totalCambios} cambios</strong>
                </div>

                <table className="tabla-comparador">
                  <thead>
                    <tr>
                      <th>Campo</th>
                      <th>Antes</th>
                      <th>Después</th>
                    </tr>
                  </thead>

                  <tbody>
                    {Object.keys(comparacion.diferencias || {}).length === 0 && (
                      <tr>
                        <td colSpan="3">No se encontraron diferencias.</td>
                      </tr>
                    )}

                    {Object.entries(comparacion.diferencias || {}).map(
                      ([campo, valores]) => (
                        <tr key={campo}>
                          <td>{campo}</td>
                          <td>
                            <pre>{valorLegible(valores.antes)}</pre>
                          </td>
                          <td>
                            <pre>{valorLegible(valores.despues)}</pre>
                          </td>
                        </tr>
                      )
                    )}
                  </tbody>
                </table>
              </article>
            )}

            {detalle && (
              <article className="rv-panel">
                <div className="rv-panel-title between">
                  <div className="rv-title-inline">
                    <Code2 size={20} />
                    <div>
                      <h2>Detalle de versión</h2>
                      <p>
                        {detalle.codigo_version} · {detalle.accion}
                      </p>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() =>
                      copiarTexto(JSON.stringify(detalle.datos_json, null, 2))
                    }
                  >
                    <Copy size={16} />
                    Copiar JSON
                  </button>
                </div>

                {loadingDetalle ? (
                  <p className="rv-muted">Cargando detalle...</p>
                ) : (
                  <pre className="rv-json">
                    {JSON.stringify(detalle.datos_json, null, 2)}
                  </pre>
                )}
              </article>
            )}

            {!detalle && !comparacion && (
              <article className="rv-empty">
                <ArrowLeft size={46} />
                <h2>Seleccione una versión</h2>
                <p>
                  Desde el panel izquierdo puede visualizar snapshots, restaurar
                  versiones o comparar cambios históricos.
                </p>
              </article>
            )}
          </section>
        </section>
      </main>
    </AdminLayout>
  );
}
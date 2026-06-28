// ============================================================
// PÁGINA PERMISOS DEL SISTEMA PRO - ERP SST PRO ENTERPRISE
// Archivo: frontend/src/pages/admin/PermisosSistemaPage.jsx
// ============================================================

import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  KeyRound,
  Loader2,
  Plus,
  RefreshCw,
  Save,
  Search,
  Settings2,
  ShieldCheck,
  UserCog,
  X,
} from "lucide-react";

import {
  asignarPermisosUsuarioSistema,
  crearPermisoSistema,
  listarPermisosSistema,
  obtenerPermisosUsuarioSistema,
} from "../../api/permisosSistemaApi";
import { listarUsuariosSistema } from "../../api/usuariosSistemaApi";

import "../../styles/seguridad-sistema.css";

const FORM_INICIAL = { codigo: "", nombre: "", modulo: "SEGURIDAD", descripcion: "" };
const limpiar = (v) => String(v ?? "").toLowerCase().trim();

export default function PermisosSistemaPage() {
  const [permisos, setPermisos] = useState([]);
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [buscar, setBuscar] = useState("");
  const [modulo, setModulo] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [modalPermiso, setModalPermiso] = useState(false);
  const [modalAsignar, setModalAsignar] = useState(false);
  const [form, setForm] = useState(FORM_INICIAL);
  const [usuarioSeleccionado, setUsuarioSeleccionado] = useState("");
  const [permisosSeleccionados, setPermisosSeleccionados] = useState([]);
  const [loadingPermisosUsuario, setLoadingPermisosUsuario] = useState(false);

  const cargarDatos = async () => {
    setLoading(true);
    setError("");
    try {
      const [permisosData, usuariosData] = await Promise.all([
        listarPermisosSistema(),
        listarUsuariosSistema(),
      ]);
      setPermisos(permisosData);
      setUsuarios(usuariosData);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "No fue posible cargar permisos y usuarios.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const modulos = useMemo(() => {
    return [...new Set(permisos.map((p) => p.modulo).filter(Boolean))].sort();
  }, [permisos]);

  const permisosFiltrados = useMemo(() => {
    const term = limpiar(buscar);
    return permisos.filter((permiso) => {
      const texto = !term || limpiar(permiso.codigo).includes(term) || limpiar(permiso.nombre).includes(term) || limpiar(permiso.descripcion).includes(term) || limpiar(permiso.modulo).includes(term);
      const mod = !modulo || permiso.modulo === modulo;
      return texto && mod;
    });
  }, [permisos, buscar, modulo]);

  const stats = useMemo(() => ({
    total: permisos.length,
    activos: permisos.filter((p) => p.activo !== false).length,
    modulos: modulos.length,
    asignables: usuarios.filter((u) => u.activo !== false).length,
  }), [permisos, modulos, usuarios]);

  const abrirNuevoPermiso = () => {
    setForm(FORM_INICIAL);
    setError("");
    setSuccess("");
    setModalPermiso(true);
  };

  const guardarPermiso = async (e) => {
    e.preventDefault();
    if (!form.codigo.trim() || !form.nombre.trim() || !form.modulo.trim()) {
      setError("Digite código, nombre y módulo del permiso.");
      return;
    }
    setSaving(true);
    setError("");
    setSuccess("");
    try {
      await crearPermisoSistema({
        codigo: form.codigo.trim().toUpperCase(),
        nombre: form.nombre.trim(),
        modulo: form.modulo.trim().toUpperCase(),
        descripcion: form.descripcion.trim() || null,
      });
      setSuccess("Permiso creado correctamente.");
      setModalPermiso(false);
      await cargarDatos();
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "No fue posible crear el permiso.");
    } finally {
      setSaving(false);
    }
  };

  const abrirAsignacion = () => {
    setUsuarioSeleccionado("");
    setPermisosSeleccionados([]);
    setError("");
    setSuccess("");
    setModalAsignar(true);
  };

  const cargarPermisosUsuario = async (usuarioId) => {
    setUsuarioSeleccionado(usuarioId);
    setPermisosSeleccionados([]);
    if (!usuarioId) return;
    setLoadingPermisosUsuario(true);
    try {
      const data = await obtenerPermisosUsuarioSistema(usuarioId);
      setPermisosSeleccionados((data.permisos || []).map((p) => p.id));
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "No fue posible cargar permisos del usuario.");
    } finally {
      setLoadingPermisosUsuario(false);
    }
  };

  const togglePermiso = (permisoId) => {
    setPermisosSeleccionados((prev) => prev.includes(permisoId) ? prev.filter((id) => id !== permisoId) : [...prev, permisoId]);
  };

  const guardarAsignacion = async (e) => {
    e.preventDefault();
    if (!usuarioSeleccionado) {
      setError("Seleccione un usuario.");
      return;
    }
    setSaving(true);
    setError("");
    setSuccess("");
    try {
      await asignarPermisosUsuarioSistema(usuarioSeleccionado, permisosSeleccionados);
      setSuccess("Permisos asignados correctamente.");
      setModalAsignar(false);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "No fue posible asignar permisos.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="seguridad-page">
      <section className="seguridad-hero">
        <div>
          <span className="seguridad-eyebrow">Seguridad · Permisos</span>
          <h1>Permisos del Sistema PRO</h1>
          <p>Gestiona permisos finos por módulo y asígnalos a usuarios cuando el rol base no sea suficiente.</p>
        </div>
        <div className="seguridad-actions">
          <button className="seguridad-btn ghost" onClick={cargarDatos} disabled={loading}>{loading ? <Loader2 size={18} /> : <RefreshCw size={18} />} Actualizar</button>
          <button className="seguridad-btn secondary" onClick={abrirAsignacion}><UserCog size={18} /> Asignar</button>
          <button className="seguridad-btn secondary" onClick={abrirNuevoPermiso}><Plus size={18} /> Nuevo permiso</button>
        </div>
      </section>

      {error && <div className="seguridad-alert error"><AlertTriangle size={18} />{error}</div>}
      {success && <div className="seguridad-alert success"><CheckCircle2 size={18} />{success}</div>}

      <section className="seguridad-kpis">
        <div className="seguridad-kpi"><div className="seguridad-kpi-icon"><KeyRound size={22} /></div><div><span>Total permisos</span><strong>{stats.total}</strong></div></div>
        <div className="seguridad-kpi"><div className="seguridad-kpi-icon"><ShieldCheck size={22} /></div><div><span>Activos</span><strong>{stats.activos}</strong></div></div>
        <div className="seguridad-kpi"><div className="seguridad-kpi-icon"><Settings2 size={22} /></div><div><span>Módulos</span><strong>{stats.modulos}</strong></div></div>
        <div className="seguridad-kpi"><div className="seguridad-kpi-icon"><UserCog size={22} /></div><div><span>Usuarios activos</span><strong>{stats.asignables}</strong></div></div>
      </section>

      <section className="seguridad-panel">
        <div className="seguridad-panel-header">
          <div><h2 className="seguridad-panel-title">Matriz de permisos</h2><p className="seguridad-panel-subtitle">Inventario de permisos disponibles por módulo.</p></div>
        </div>
        <div className="seguridad-toolbar" style={{ gridTemplateColumns: "1fr 260px" }}>
          <div className="seguridad-input-wrap"><Search size={18} /><input className="seguridad-input with-icon" value={buscar} onChange={(e) => setBuscar(e.target.value)} placeholder="Buscar por código, nombre, módulo..." /></div>
          <select className="seguridad-select" value={modulo} onChange={(e) => setModulo(e.target.value)}><option value="">Todos los módulos</option>{modulos.map((m) => <option key={m} value={m}>{m}</option>)}</select>
        </div>
        <div className="seguridad-table-wrap">
          <table className="seguridad-table">
            <thead><tr><th>Código</th><th>Nombre</th><th>Módulo</th><th>Descripción</th><th>Estado</th></tr></thead>
            <tbody>
              {permisosFiltrados.map((p) => <tr key={p.id}><td><strong>{p.codigo}</strong><br /><span style={{ color: "#64748b", fontSize: 12 }}>ID #{p.id}</span></td><td>{p.nombre}</td><td><span className="seguridad-badge purple">{p.modulo}</span></td><td>{p.descripcion || "Sin descripción"}</td><td><span className={`seguridad-badge ${p.activo === false ? "red" : "green"}`}>{p.activo === false ? "INACTIVO" : "ACTIVO"}</span></td></tr>)}
              {!permisosFiltrados.length && <tr><td colSpan="5"><div className="seguridad-empty">No hay permisos para mostrar.</div></td></tr>}
            </tbody>
          </table>
        </div>
      </section>

      {modalPermiso && <div className="seguridad-modal-backdrop"><div className="seguridad-modal"><div className="seguridad-modal-header"><div><h2>Nuevo permiso</h2><p>Solo SUPER_ADMIN puede crear permisos.</p></div><button className="seguridad-btn small secondary" onClick={() => setModalPermiso(false)}><X size={18} /></button></div><form className="seguridad-form" onSubmit={guardarPermiso}><div className="seguridad-form-grid"><div className="seguridad-form-field"><label>Código</label><input className="seguridad-input" value={form.codigo} onChange={(e) => setForm((p) => ({ ...p, codigo: e.target.value }))} placeholder="EJ: USUARIOS_CREAR" /></div><div className="seguridad-form-field"><label>Módulo</label><input className="seguridad-input" value={form.modulo} onChange={(e) => setForm((p) => ({ ...p, modulo: e.target.value }))} placeholder="EJ: SEGURIDAD" /></div><div className="seguridad-form-field full"><label>Nombre</label><input className="seguridad-input" value={form.nombre} onChange={(e) => setForm((p) => ({ ...p, nombre: e.target.value }))} placeholder="Nombre visible del permiso" /></div><div className="seguridad-form-field full"><label>Descripción</label><textarea className="seguridad-textarea" value={form.descripcion} onChange={(e) => setForm((p) => ({ ...p, descripcion: e.target.value }))} /></div></div><div className="seguridad-modal-actions"><button type="button" className="seguridad-btn secondary" onClick={() => setModalPermiso(false)}>Cancelar</button><button type="submit" className="seguridad-btn primary" disabled={saving}>{saving ? <Loader2 size={18} /> : <Save size={18} />} Guardar</button></div></form></div></div>}

      {modalAsignar && <div className="seguridad-modal-backdrop"><div className="seguridad-modal"><div className="seguridad-modal-header"><div><h2>Asignar permisos a usuario</h2><p>La asignación reemplaza la lista actual de permisos directos del usuario.</p></div><button className="seguridad-btn small secondary" onClick={() => setModalAsignar(false)}><X size={18} /></button></div><form className="seguridad-form" onSubmit={guardarAsignacion}><div className="seguridad-form-field full"><label>Usuario</label><select className="seguridad-select" value={usuarioSeleccionado} onChange={(e) => cargarPermisosUsuario(e.target.value)}><option value="">Seleccione un usuario</option>{usuarios.map((u) => <option key={u.id} value={u.id}>{u.nombres} {u.apellidos} · {u.correo} · {u.rol}</option>)}</select></div>{loadingPermisosUsuario ? <div className="seguridad-alert info"><Loader2 size={18} />Cargando permisos del usuario...</div> : <div className="seguridad-checkbox-grid">{permisos.map((p) => <label className="seguridad-check-card" key={p.id}><input type="checkbox" checked={permisosSeleccionados.includes(p.id)} onChange={() => togglePermiso(p.id)} /><div><strong>{p.codigo}</strong><span>{p.modulo} · {p.nombre}</span></div></label>)}</div>}<div className="seguridad-modal-actions"><button type="button" className="seguridad-btn secondary" onClick={() => setModalAsignar(false)}>Cancelar</button><button type="submit" className="seguridad-btn primary" disabled={saving}>{saving ? <Loader2 size={18} /> : <Save size={18} />} Guardar asignación</button></div></form></div></div>}
    </div>
  );
}

// ============================================================
// PÁGINA ROLES DEL SISTEMA PRO - ERP SST PRO ENTERPRISE
// Archivo: frontend/src/pages/admin/RolesSistemaPage.jsx
// ============================================================

import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Edit3,
  Loader2,
  Plus,
  RefreshCw,
  Save,
  Search,
  Shield,
  ShieldCheck,
  Trash2,
  X,
} from "lucide-react";

import {
  actualizarRolSistema,
  crearRolSistema,
  eliminarRolSistema,
  listarRolesSistemaAdmin,
} from "../../api/rolesSistemaApi";

import "../../styles/seguridad-sistema.css";
import "../../styles/seguridad-compact.css";

const FORM_INICIAL = { nombre: "", descripcion: "", activo: true };
const limpiar = (v) => String(v ?? "").toLowerCase().trim();

export default function RolesSistemaPage() {
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [buscar, setBuscar] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [modal, setModal] = useState(false);
  const [editando, setEditando] = useState(null);
  const [form, setForm] = useState(FORM_INICIAL);

  const cargarRoles = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await listarRolesSistemaAdmin();
      setRoles(data);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "No fue posible cargar los roles del sistema.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarRoles();
  }, []);

  const rolesFiltrados = useMemo(() => {
    const term = limpiar(buscar);
    return roles.filter((rol) => {
      if (!term) return true;
      return limpiar(rol.nombre).includes(term) || limpiar(rol.descripcion).includes(term);
    });
  }, [roles, buscar]);

  const stats = useMemo(() => {
    const total = roles.length;
    const activos = roles.filter((r) => r.activo !== false).length;
    return { total, activos, inactivos: total - activos, sistema: roles.filter((r) => ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"].includes(r.nombre)).length };
  }, [roles]);

  const abrirNuevo = () => {
    setEditando(null);
    setForm(FORM_INICIAL);
    setError("");
    setSuccess("");
    setModal(true);
  };

  const abrirEditar = (rol) => {
    setEditando(rol);
    setForm({ nombre: rol.nombre || "", descripcion: rol.descripcion || "", activo: rol.activo !== false });
    setError("");
    setSuccess("");
    setModal(true);
  };

  const cerrarModal = () => {
    if (saving) return;
    setModal(false);
    setEditando(null);
    setForm(FORM_INICIAL);
  };

  const guardarRol = async (e) => {
    e.preventDefault();
    if (!form.nombre.trim()) {
      setError("Digite el nombre del rol.");
      return;
    }

    setSaving(true);
    setError("");
    setSuccess("");
    try {
      const payload = {
        nombre: form.nombre.trim().toUpperCase(),
        descripcion: form.descripcion.trim() || null,
        activo: Boolean(form.activo),
      };
      if (editando) {
        await actualizarRolSistema(editando.id, payload);
        setSuccess("Rol actualizado correctamente.");
      } else {
        await crearRolSistema(payload);
        setSuccess("Rol creado correctamente.");
      }
      await cargarRoles();
      cerrarModal();
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "No fue posible guardar el rol.");
    } finally {
      setSaving(false);
    }
  };

  const desactivarRol = async (rol) => {
    const confirmar = window.confirm(`¿Desea desactivar el rol ${rol.nombre}?`);
    if (!confirmar) return;
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      await eliminarRolSistema(rol.id);
      setSuccess("Rol desactivado correctamente.");
      await cargarRoles();
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "No fue posible desactivar el rol.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="seguridad-page">
      <section className="seguridad-hero">
        <div>
          <h1>Roles del Sistema</h1>
          <p>Administra los perfiles que controlan el acceso a los módulos.</p>
        </div>
        <div className="seguridad-actions">
          <button title="Actualizar" className="seguridad-btn ghost" onClick={cargarRoles} disabled={loading}>
            {loading ? <Loader2 size={18} className="spin" /> : <RefreshCw size={18} />} Actualizar
          </button>
          <button title="Nuevo rol" className="seguridad-btn secondary" onClick={abrirNuevo}>
            <Plus size={18} /> Nuevo rol
          </button>
        </div>
      </section>

      {error && <div className="seguridad-alert error"><AlertTriangle size={18} />{error}</div>}
      {success && <div className="seguridad-alert success"><CheckCircle2 size={18} />{success}</div>}

      <section className="seguridad-kpis">
        <div className="seguridad-kpi"><div className="seguridad-kpi-icon"><Shield size={22} /></div><div><span>Total roles</span><strong>{stats.total}</strong></div></div>
        <div className="seguridad-kpi"><div className="seguridad-kpi-icon"><ShieldCheck size={22} /></div><div><span>Activos</span><strong>{stats.activos}</strong></div></div>
        <div className="seguridad-kpi"><div className="seguridad-kpi-icon"><AlertTriangle size={22} /></div><div><span>Inactivos</span><strong>{stats.inactivos}</strong></div></div>
        <div className="seguridad-kpi"><div className="seguridad-kpi-icon"><ShieldCheck size={22} /></div><div><span>Roles base</span><strong>{stats.sistema}</strong></div></div>
      </section>

      <section className="seguridad-panel">
        <div className="seguridad-panel-header">
          <div>
            <h2 className="seguridad-panel-title">Inventario de roles</h2>
            <p className="seguridad-panel-subtitle">Crear, editar y desactivar roles de seguridad.</p>
          </div>
        </div>
        <div className="seguridad-toolbar" style={{ gridTemplateColumns: "1fr" }}>
          <div className="seguridad-input-wrap">
            <Search size={18} />
            <input className="seguridad-input with-icon" value={buscar} onChange={(e) => setBuscar(e.target.value)} placeholder="Buscar por nombre o descripción..." />
          </div>
        </div>
        <div className="seguridad-table-wrap">
          <table className="seguridad-table">
            <thead>
              <tr><th>Rol</th><th>Descripción</th><th>Estado</th><th>Actualización</th><th>Acciones</th></tr>
            </thead>
            <tbody>
              {rolesFiltrados.map((rol) => (
                <tr key={rol.id}>
                  <td><div className="seguridad-name"><div className="seguridad-avatar">{(rol.nombre || "R").slice(0, 1)}</div><div><strong>{rol.nombre}</strong><span>ID #{rol.id}</span></div></div></td>
                  <td>{rol.descripcion || "Sin descripción"}</td>
                  <td><span className={`seguridad-badge ${rol.activo === false ? "red" : "green"}`}>{rol.activo === false ? "INACTIVO" : "ACTIVO"}</span></td>
                  <td>{rol.fecha_actualizacion ? new Date(rol.fecha_actualizacion).toLocaleString() : "Sin registro"}</td>
                  <td><div className="seguridad-row-actions"><button className="seguridad-btn small secondary" onClick={() => abrirEditar(rol)}><Edit3 size={16} /></button><button className="seguridad-btn small danger" onClick={() => desactivarRol(rol)}><Trash2 size={16} /></button></div></td>
                </tr>
              ))}
              {!rolesFiltrados.length && <tr><td colSpan="5"><div className="seguridad-empty">No hay roles para mostrar.</div></td></tr>}
            </tbody>
          </table>
        </div>
      </section>

      {modal && (
        <div className="seguridad-modal-backdrop">
          <div className="seguridad-modal">
            <div className="seguridad-modal-header">
              <div><h2>{editando ? "Editar rol" : "Nuevo rol"}</h2><p>Solo SUPER_ADMIN puede crear o modificar roles.</p></div>
              <button className="seguridad-btn small secondary" onClick={cerrarModal}><X size={18} /></button>
            </div>
            <form className="seguridad-form" onSubmit={guardarRol}>
              <div className="seguridad-form-grid">
                <div className="seguridad-form-field"><label>Nombre del rol</label><input className="seguridad-input" value={form.nombre} onChange={(e) => setForm((p) => ({ ...p, nombre: e.target.value }))} placeholder="Ej: AUDITOR" /></div>
                <div className="seguridad-form-field"><label>Estado</label><select className="seguridad-select" value={form.activo ? "true" : "false"} onChange={(e) => setForm((p) => ({ ...p, activo: e.target.value === "true" }))}><option value="true">ACTIVO</option><option value="false">INACTIVO</option></select></div>
                <div className="seguridad-form-field full"><label>Descripción</label><textarea className="seguridad-textarea" value={form.descripcion} onChange={(e) => setForm((p) => ({ ...p, descripcion: e.target.value }))} placeholder="Describe el alcance del rol..." /></div>
              </div>
              <div className="seguridad-modal-actions"><button type="button" className="seguridad-btn secondary" onClick={cerrarModal}>Cancelar</button><button type="submit" className="seguridad-btn primary" disabled={saving}>{saving ? <Loader2 size={18} /> : <Save size={18} />} Guardar</button></div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================
// PÁGINA USUARIOS DEL SISTEMA PRO
// ERP SST PRO ENTERPRISE
// FASE HARDENING — CRUD completo de usuarios
// ============================================================

import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Eye,
  EyeOff,
  KeyRound,
  Loader2,
  Lock,
  Pencil,
  Plus,
  RefreshCw,
  Save,
  Search,
  ShieldCheck,
  Trash2,
  UserCheck,
  Users,
  X,
} from "lucide-react";

import {
  actualizarUsuarioSistema,
  cambiarEstadoUsuarioSistema,
  cambiarPasswordUsuarioSistema,
  crearUsuarioSistema,
  eliminarUsuarioSistema,
  listarRolesSistema,
  listarUsuariosSistema,
  obtenerStatsUsuariosSistema,
} from "../../api/usuariosSistemaApi";

import "../../styles/usuarios-sistema.css";
import "../../styles/seguridad-compact.css";

const FORM_INICIAL = {
  nombres: "",
  apellidos: "",
  correo: "",
  password: "",
  rol: "ADMIN_EMPRESA",
  empresa_id: "",
  activo: true,
};

const PASSWORD_INICIAL = {
  usuario: null,
  password: "",
};

const PAGE_SIZE = 12;

const textoEstado = (activo) => (activo ? "ACTIVO" : "INACTIVO");
const limpiar = (value) => String(value ?? "").toLowerCase().trim();

export default function UsuariosSistemaPage() {
  const [usuarios, setUsuarios] = useState([]);
  const [roles, setRoles] = useState([]);
  const [stats, setStats] = useState({ total: 0, activos: 0, inactivos: 0, super_admins: 0 });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [buscar, setBuscar] = useState("");
  const [filtroRol, setFiltroRol] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("TODOS");
  const [pagina, setPagina] = useState(1);

  const [modalAbierto, setModalAbierto] = useState(false);
  const [modoEdicion, setModoEdicion] = useState(false);
  const [usuarioEditando, setUsuarioEditando] = useState(null);
  const [form, setForm] = useState(FORM_INICIAL);
  const [verPassword, setVerPassword] = useState(false);

  const [modalPassword, setModalPassword] = useState(false);
  const [passwordForm, setPasswordForm] = useState(PASSWORD_INICIAL);
  const [verPasswordAdmin, setVerPasswordAdmin] = useState(false);

  const usuarioActual = useMemo(() => {
    try {
      return JSON.parse(localStorage.getItem("user") || "{}");
    } catch {
      return {};
    }
  }, []);

  const puedeAdministrar = usuarioActual?.rol === "SUPER_ADMIN";

  const cargarDatos = async () => {
    setLoading(true);
    setError("");
    try {
      const [usuariosData, rolesData, statsData] = await Promise.all([
        listarUsuariosSistema(),
        listarRolesSistema(),
        obtenerStatsUsuariosSistema(),
      ]);
      setUsuarios(usuariosData);
      setRoles(rolesData);
      setStats(statsData);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "No fue posible cargar los usuarios del sistema.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const usuariosFiltrados = useMemo(() => {
    const term = limpiar(buscar);
    return usuarios.filter((u) => {
      const coincideTexto =
        !term ||
        limpiar(u.nombres).includes(term) ||
        limpiar(u.apellidos).includes(term) ||
        limpiar(u.correo).includes(term) ||
        limpiar(u.rol).includes(term);

      const coincideRol = !filtroRol || u.rol === filtroRol;
      const coincideEstado =
        filtroEstado === "TODOS" ||
        (filtroEstado === "ACTIVOS" && u.activo) ||
        (filtroEstado === "INACTIVOS" && !u.activo);

      return coincideTexto && coincideRol && coincideEstado;
    });
  }, [usuarios, buscar, filtroRol, filtroEstado]);

  const totalPaginas = Math.max(1, Math.ceil(usuariosFiltrados.length / PAGE_SIZE));
  const usuariosPagina = usuariosFiltrados.slice((pagina - 1) * PAGE_SIZE, pagina * PAGE_SIZE);

  useEffect(() => {
    setPagina(1);
  }, [buscar, filtroRol, filtroEstado]);

  const abrirNuevo = () => {
    setModoEdicion(false);
    setUsuarioEditando(null);
    setForm(FORM_INICIAL);
    setVerPassword(false);
    setError("");
    setSuccess("");
    setModalAbierto(true);
  };

  const abrirEditar = (usuario) => {
    setModoEdicion(true);
    setUsuarioEditando(usuario);
    setForm({
      nombres: usuario.nombres || "",
      apellidos: usuario.apellidos || "",
      correo: usuario.correo || "",
      password: "",
      rol: usuario.rol || "ADMIN_EMPRESA",
      empresa_id: usuario.empresa_id ?? "",
      activo: Boolean(usuario.activo),
    });
    setError("");
    setSuccess("");
    setModalAbierto(true);
  };

  const cerrarModal = () => {
    if (saving) return;
    setModalAbierto(false);
    setUsuarioEditando(null);
    setForm(FORM_INICIAL);
  };

  const actualizarCampo = (campo, valor) => {
    setForm((prev) => ({ ...prev, [campo]: valor }));
  };

  const validarFormulario = () => {
    if (!form.nombres.trim() || !form.apellidos.trim()) return "Digite nombres y apellidos.";
    if (!form.correo.trim()) return "Digite el correo electrónico.";
    if (!modoEdicion && form.password.length < 8) return "La contraseña debe tener mínimo 8 caracteres.";
    if (!form.rol) return "Seleccione un rol.";
    return "";
  };

  const guardarUsuario = async (event) => {
    event.preventDefault();
    const validacion = validarFormulario();
    if (validacion) {
      setError(validacion);
      return;
    }

    setSaving(true);
    setError("");
    setSuccess("");

    const payload = {
      nombres: form.nombres.trim(),
      apellidos: form.apellidos.trim(),
      correo: form.correo.trim().toLowerCase(),
      rol: form.rol,
      empresa_id: form.empresa_id === "" ? null : Number(form.empresa_id),
      activo: Boolean(form.activo),
    };

    try {
      if (modoEdicion && usuarioEditando) {
        await actualizarUsuarioSistema(usuarioEditando.id, payload);
        setSuccess("Usuario actualizado correctamente.");
      } else {
        await crearUsuarioSistema({ ...payload, password: form.password });
        setSuccess("Usuario creado correctamente.");
      }
      await cargarDatos();
      setModalAbierto(false);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "No fue posible guardar el usuario.");
    } finally {
      setSaving(false);
    }
  };

  const abrirCambiarPassword = (usuario) => {
    setPasswordForm({ usuario, password: "" });
    setVerPasswordAdmin(false);
    setError("");
    setSuccess("");
    setModalPassword(true);
  };

  const guardarPassword = async (event) => {
    event.preventDefault();
    if (!passwordForm.usuario) return;
    if (passwordForm.password.length < 8) {
      setError("La nueva contraseña debe tener mínimo 8 caracteres.");
      return;
    }

    setSaving(true);
    setError("");
    setSuccess("");
    try {
      await cambiarPasswordUsuarioSistema(passwordForm.usuario.id, passwordForm.password);
      setSuccess("Contraseña actualizada correctamente.");
      setModalPassword(false);
      setPasswordForm(PASSWORD_INICIAL);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "No fue posible cambiar la contraseña.");
    } finally {
      setSaving(false);
    }
  };

  const toggleEstado = async (usuario) => {
    if (usuario.id === usuarioActual?.id) {
      setError("No puede desactivar su propio usuario.");
      return;
    }
    const confirmar = window.confirm(`¿Desea ${usuario.activo ? "desactivar" : "activar"} a ${usuario.correo}?`);
    if (!confirmar) return;

    setLoading(true);
    setError("");
    setSuccess("");
    try {
      await cambiarEstadoUsuarioSistema(usuario.id);
      setSuccess("Estado del usuario actualizado correctamente.");
      await cargarDatos();
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "No fue posible actualizar el estado.");
    } finally {
      setLoading(false);
    }
  };

  const eliminarUsuario = async (usuario) => {
    if (usuario.id === usuarioActual?.id) {
      setError("No puede eliminar/desactivar su propio usuario.");
      return;
    }
    const confirmar = window.confirm(`¿Desea desactivar el usuario ${usuario.correo}?`);
    if (!confirmar) return;

    setLoading(true);
    setError("");
    setSuccess("");
    try {
      await eliminarUsuarioSistema(usuario.id);
      setSuccess("Usuario desactivado correctamente.");
      await cargarDatos();
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "No fue posible desactivar el usuario.");
    } finally {
      setLoading(false);
    }
  };

  if (!puedeAdministrar) {
    return (
      <section className="usuarios-pro-page">
        <div className="usuarios-pro-denegado">
          <Lock size={44} />
          <h2>Acceso restringido</h2>
          <p>Este módulo solo está disponible para usuarios con rol SUPER_ADMIN.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="usuarios-pro-page">
      <header className="usuarios-pro-hero">
        <div>
          <h1>Usuarios del Sistema</h1>
          <p>Administra cuentas, roles, estados y credenciales de acceso.</p>
        </div>
        <div className="usuarios-pro-actions">
          <button title="Actualizar" type="button" className="btn-secondary" onClick={cargarDatos} disabled={loading}>
            {loading ? <Loader2 className="spin" size={18} /> : <RefreshCw size={18} />}
            Actualizar
          </button>
          <button title="Nuevo usuario" type="button" className="btn-primary" onClick={abrirNuevo}>
            <Plus size={18} />
            Nuevo usuario
          </button>
        </div>
      </header>

      {(error || success) && (
        <div className={`usuarios-pro-alert ${error ? "error" : "success"}`}>
          {error ? <AlertTriangle size={18} /> : <CheckCircle2 size={18} />}
          <span>{error || success}</span>
          <button type="button" onClick={() => { setError(""); setSuccess(""); }}>
            <X size={16} />
          </button>
        </div>
      )}

      <div className="usuarios-pro-kpis">
        <article>
          <Users size={24} />
          <span>Total usuarios</span>
          <strong>{stats.total}</strong>
        </article>
        <article>
          <UserCheck size={24} />
          <span>Activos</span>
          <strong>{stats.activos}</strong>
        </article>
        <article>
          <AlertTriangle size={24} />
          <span>Inactivos</span>
          <strong>{stats.inactivos}</strong>
        </article>
        <article>
          <ShieldCheck size={24} />
          <span>SUPER_ADMIN</span>
          <strong>{stats.super_admins}</strong>
        </article>
      </div>

      <div className="usuarios-pro-toolbar">
        <label className="search-box">
          <Search size={18} />
          <input
            type="text"
            value={buscar}
            placeholder="Buscar por nombre, correo o rol..."
            onChange={(e) => setBuscar(e.target.value)}
          />
        </label>
        <select value={filtroRol} onChange={(e) => setFiltroRol(e.target.value)}>
          <option value="">Todos los roles</option>
          {roles.map((rol) => (
            <option key={rol} value={rol}>{rol}</option>
          ))}
        </select>
        <select value={filtroEstado} onChange={(e) => setFiltroEstado(e.target.value)}>
          <option value="TODOS">Todos los estados</option>
          <option value="ACTIVOS">Activos</option>
          <option value="INACTIVOS">Inactivos</option>
        </select>
      </div>

      <div className="usuarios-pro-table-card">
        <div className="table-responsive">
          <table className="usuarios-pro-table">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Correo</th>
                <th>Rol</th>
                <th>Empresa</th>
                <th>Estado</th>
                <th>Último acceso</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="7" className="empty-cell">
                    <Loader2 className="spin" size={22} /> Cargando usuarios...
                  </td>
                </tr>
              ) : usuariosPagina.length === 0 ? (
                <tr>
                  <td colSpan="7" className="empty-cell">No hay usuarios para mostrar.</td>
                </tr>
              ) : (
                usuariosPagina.map((usuario) => (
                  <tr key={usuario.id}>
                    <td>
                      <div className="usuario-info">
                        <div className="avatar">{String(usuario.nombres || "U").slice(0, 1)}</div>
                        <div>
                          <strong>{usuario.nombres} {usuario.apellidos}</strong>
                          <span>ID #{usuario.id}</span>
                        </div>
                      </div>
                    </td>
                    <td>{usuario.correo}</td>
                    <td><span className="rol-pill">{usuario.rol}</span></td>
                    <td>{usuario.empresa_id ? `Empresa #${usuario.empresa_id}` : "Global"}</td>
                    <td>
                      <button
                        type="button"
                        className={`estado-pill ${usuario.activo ? "activo" : "inactivo"}`}
                        onClick={() => toggleEstado(usuario)}
                        title="Cambiar estado"
                      >
                        {textoEstado(usuario.activo)}
                      </button>
                    </td>
                    <td>{usuario.ultimo_acceso ? new Date(usuario.ultimo_acceso).toLocaleString("es-CO") : "Sin registro"}</td>
                    <td>
                      <div className="table-actions">
                        <button type="button" onClick={() => abrirEditar(usuario)} title="Editar">
                          <Pencil size={16} />
                        </button>
                        <button type="button" onClick={() => abrirCambiarPassword(usuario)} title="Cambiar contraseña">
                          <KeyRound size={16} />
                        </button>
                        <button type="button" className="danger" onClick={() => eliminarUsuario(usuario)} title="Desactivar">
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="usuarios-pro-pagination">
          <span>Mostrando {usuariosPagina.length} de {usuariosFiltrados.length} usuarios</span>
          <div>
            <button type="button" disabled={pagina <= 1} onClick={() => setPagina((p) => Math.max(1, p - 1))}>Anterior</button>
            <strong>{pagina} / {totalPaginas}</strong>
            <button type="button" disabled={pagina >= totalPaginas} onClick={() => setPagina((p) => Math.min(totalPaginas, p + 1))}>Siguiente</button>
          </div>
        </div>
      </div>

      {modalAbierto && (
        <div className="usuarios-pro-modal-backdrop" role="presentation">
          <div className="usuarios-pro-modal" role="dialog" aria-modal="true">
            <header>
              <div>
                <span>{modoEdicion ? "Editar cuenta" : "Crear cuenta"}</span>
                <h2>{modoEdicion ? "Actualizar usuario" : "Nuevo usuario del sistema"}</h2>
              </div>
              <button type="button" onClick={cerrarModal}><X size={20} /></button>
            </header>

            <form onSubmit={guardarUsuario} className="usuarios-pro-form">
              <div className="form-grid two">
                <label>
                  Nombres
                  <input value={form.nombres} onChange={(e) => actualizarCampo("nombres", e.target.value)} maxLength={255} required />
                </label>
                <label>
                  Apellidos
                  <input value={form.apellidos} onChange={(e) => actualizarCampo("apellidos", e.target.value)} maxLength={255} required />
                </label>
              </div>

              <label>
                Correo electrónico
                <input type="email" value={form.correo} onChange={(e) => actualizarCampo("correo", e.target.value)} maxLength={255} required />
              </label>

              {!modoEdicion && (
                <label>
                  Contraseña temporal
                  <div className="password-field">
                    <input
                      type={verPassword ? "text" : "password"}
                      value={form.password}
                      onChange={(e) => actualizarCampo("password", e.target.value)}
                      minLength={8}
                      maxLength={128}
                      required
                    />
                    <button type="button" onClick={() => setVerPassword((v) => !v)}>
                      {verPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                  <small>Mínimo 8 caracteres. Entregar por canal seguro.</small>
                </label>
              )}

              <div className="form-grid two">
                <label>
                  Rol
                  <select value={form.rol} onChange={(e) => actualizarCampo("rol", e.target.value)} required>
                    {roles.map((rol) => (
                      <option key={rol} value={rol}>{rol}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Empresa ID opcional
                  <input
                    type="number"
                    min="1"
                    value={form.empresa_id}
                    onChange={(e) => actualizarCampo("empresa_id", e.target.value)}
                    placeholder="Vacío = acceso global"
                  />
                </label>
              </div>

              <label className="check-row">
                <input type="checkbox" checked={form.activo} onChange={(e) => actualizarCampo("activo", e.target.checked)} />
                Usuario activo
              </label>

              <footer>
                <button type="button" className="btn-secondary" onClick={cerrarModal}>Cancelar</button>
                <button type="submit" className="btn-primary" disabled={saving}>
                  {saving ? <Loader2 className="spin" size={18} /> : <Save size={18} />}
                  Guardar
                </button>
              </footer>
            </form>
          </div>
        </div>
      )}

      {modalPassword && (
        <div className="usuarios-pro-modal-backdrop" role="presentation">
          <div className="usuarios-pro-modal small" role="dialog" aria-modal="true">
            <header>
              <div>
                <span>Seguridad</span>
                <h2>Cambiar contraseña</h2>
                <p>{passwordForm.usuario?.correo}</p>
              </div>
              <button type="button" onClick={() => setModalPassword(false)}><X size={20} /></button>
            </header>

            <form onSubmit={guardarPassword} className="usuarios-pro-form">
              <label>
                Nueva contraseña
                <div className="password-field">
                  <input
                    type={verPasswordAdmin ? "text" : "password"}
                    value={passwordForm.password}
                    onChange={(e) => setPasswordForm((prev) => ({ ...prev, password: e.target.value }))}
                    minLength={8}
                    maxLength={128}
                    required
                  />
                  <button type="button" onClick={() => setVerPasswordAdmin((v) => !v)}>
                    {verPasswordAdmin ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
                <small>El usuario deberá ingresar con esta nueva contraseña.</small>
              </label>
              <footer>
                <button type="button" className="btn-secondary" onClick={() => setModalPassword(false)}>Cancelar</button>
                <button type="submit" className="btn-primary" disabled={saving}>
                  {saving ? <Loader2 className="spin" size={18} /> : <KeyRound size={18} />}
                  Cambiar contraseña
                </button>
              </footer>
            </form>
          </div>
        </div>
      )}
    </section>
  );
}

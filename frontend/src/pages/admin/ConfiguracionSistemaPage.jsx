// ============================================================
// PÁGINA CONFIGURACIÓN SISTEMA PRO
// ERP SST PRO ENTERPRISE
// FASE 35.4.2
// Archivo: frontend/src/pages/admin/ConfiguracionSistemaPage.jsx
// ============================================================

import { useEffect, useState } from "react";
import { AlertTriangle, Bell, CheckCircle2, DatabaseBackup, HardDrive, Loader2, Lock, RefreshCcw, Save, Settings, ShieldCheck, Wrench } from "lucide-react";
import { actualizarConfiguracionSistema, obtenerConfiguracionSistema, obtenerHealthConfiguracionSistema } from "../../api/configuracionSistemaApi";
import "../../styles/configuracion-sistema.css";

const DEFAULT_FORM = {
  nombre_plataforma: "ERP SST PRO", ambiente: "LOCAL", version: "1.0.0", dominio_frontend: "", dominio_backend: "", soporte_correo: "", soporte_telefono: "",
  jwt_expiracion_minutos: 480, intentos_login_maximos: 5, bloqueo_login_minutos: 15, exigir_password_fuerte: true, permitir_registro_publico: false,
  upload_max_mb: 25, evidencias_webp: true, evidencias_preview: true, evidencias_thumbnail: true, retencion_evidencias_meses: 60,
  smtp_activo: false, smtp_host: "", smtp_puerto: "", smtp_usuario: "", smtp_from: "", notificaciones_activas: true,
  backups_activos: true, backups_frecuencia: "DIARIO", backups_retencion_dias: 30,
  mantenimiento_activo: false, mantenimiento_mensaje: "", observaciones: "",
};

function Section({ icon: Icon, title, description, children }) {
  return <article className="cs-section"><div className="cs-section-header"><div className="cs-section-icon"><Icon size={20} /></div><div><h2>{title}</h2><p>{description}</p></div></div><div className="cs-grid">{children}</div></article>;
}
function Field({ label, children }) { return <label className="cs-field"><span>{label}</span>{children}</label>; }
function Toggle({ label, checked, onChange }) { return <label className="cs-toggle"><input type="checkbox" checked={Boolean(checked)} onChange={(e)=>onChange(e.target.checked)} /><span /><strong>{label}</strong></label>; }
function HealthBadge({ ok, label }) { return <span className={`cs-health-badge ${ok ? "ok" : "warn"}`}>{ok ? <CheckCircle2 size={15}/> : <AlertTriangle size={15}/>} {label}</span>; }

export default function ConfiguracionSistemaPage() {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  async function cargarConfiguracion() {
    setLoading(true); setError(""); setMensaje("");
    try {
      const [config, healthData] = await Promise.all([obtenerConfiguracionSistema(), obtenerHealthConfiguracionSistema()]);
      setForm({ ...DEFAULT_FORM, ...Object.fromEntries(Object.entries(config || {}).map(([k,v]) => [k, v ?? DEFAULT_FORM[k] ?? ""])) });
      setHealth(healthData);
    } catch (err) { setError(err?.response?.data?.detail || err?.message || "No fue posible cargar la configuración."); }
    finally { setLoading(false); }
  }
  useEffect(() => { cargarConfiguracion(); }, []);
  function update(name, value) { setForm(prev => ({ ...prev, [name]: value })); }
  function toNumber(value, fallback=0) { const parsed=Number(value); return Number.isFinite(parsed) ? parsed : fallback; }
  async function guardar(event) {
    event.preventDefault(); setSaving(true); setError(""); setMensaje("");
    const payload = { ...form, jwt_expiracion_minutos: toNumber(form.jwt_expiracion_minutos,480), intentos_login_maximos: toNumber(form.intentos_login_maximos,5), bloqueo_login_minutos: toNumber(form.bloqueo_login_minutos,15), upload_max_mb: toNumber(form.upload_max_mb,25), retencion_evidencias_meses: toNumber(form.retencion_evidencias_meses,60), smtp_puerto: form.smtp_puerto ? toNumber(form.smtp_puerto,587) : null, backups_retencion_dias: toNumber(form.backups_retencion_dias,30) };
    try { await actualizarConfiguracionSistema(payload); setMensaje("Configuración del sistema guardada correctamente."); await cargarConfiguracion(); }
    catch (err) { setError(err?.response?.data?.detail || err?.message || "No fue posible guardar la configuración."); }
    finally { setSaving(false); }
  }

  return <section className="configuracion-sistema-page">
    <div className="cs-hero"><div><span className="cs-kicker">SEGURIDAD · CONFIGURACIÓN · ENTERPRISE</span><h1>Configuración Sistema PRO</h1><p>Parámetros globales de plataforma, seguridad, evidencias, notificaciones, backups y mantenimiento.</p></div><button className="cs-btn ghost" type="button" onClick={cargarConfiguracion} disabled={loading}><RefreshCcw size={17}/>{loading ? "Cargando..." : "Actualizar"}</button></div>
    {error && <div className="cs-alert danger"><AlertTriangle size={18}/>{error}</div>}
    {mensaje && <div className="cs-alert ok"><CheckCircle2 size={18}/>{mensaje}</div>}
    <div className="cs-health-grid"><HealthBadge ok={health?.seguridad?.ok} label="Seguridad"/><HealthBadge ok={health?.evidencias?.ok} label="Evidencias"/><HealthBadge ok={health?.backups?.ok} label="Backups"/><HealthBadge ok={health?.notificaciones?.ok} label="Notificaciones"/><HealthBadge ok={health?.mantenimiento?.ok} label="Mantenimiento"/></div>
    <form onSubmit={guardar} className="cs-form">
      <Section icon={Settings} title="Datos de plataforma" description="Identificación general del ERP SST y datos de soporte."><Field label="Nombre plataforma"><input value={form.nombre_plataforma} onChange={e=>update('nombre_plataforma',e.target.value)}/></Field><Field label="Ambiente"><select value={form.ambiente} onChange={e=>update('ambiente',e.target.value)}><option value="LOCAL">LOCAL</option><option value="DESARROLLO">DESARROLLO</option><option value="PRUEBAS">PRUEBAS</option><option value="PRODUCCION">PRODUCCIÓN</option></select></Field><Field label="Versión"><input value={form.version} onChange={e=>update('version',e.target.value)}/></Field><Field label="Dominio frontend"><input value={form.dominio_frontend||''} onChange={e=>update('dominio_frontend',e.target.value)}/></Field><Field label="Dominio backend"><input value={form.dominio_backend||''} onChange={e=>update('dominio_backend',e.target.value)}/></Field><Field label="Correo soporte"><input value={form.soporte_correo||''} onChange={e=>update('soporte_correo',e.target.value)}/></Field><Field label="Teléfono soporte"><input value={form.soporte_telefono||''} onChange={e=>update('soporte_telefono',e.target.value)}/></Field></Section>
      <Section icon={Lock} title="Seguridad" description="Control de sesiones, bloqueo de login y políticas de acceso."><Field label="JWT expiración minutos"><input type="number" min="5" value={form.jwt_expiracion_minutos} onChange={e=>update('jwt_expiracion_minutos',e.target.value)}/></Field><Field label="Intentos login máximos"><input type="number" min="1" value={form.intentos_login_maximos} onChange={e=>update('intentos_login_maximos',e.target.value)}/></Field><Field label="Bloqueo login minutos"><input type="number" min="1" value={form.bloqueo_login_minutos} onChange={e=>update('bloqueo_login_minutos',e.target.value)}/></Field><Toggle label="Exigir contraseña fuerte" checked={form.exigir_password_fuerte} onChange={v=>update('exigir_password_fuerte',v)}/><Toggle label="Permitir registro público" checked={form.permitir_registro_publico} onChange={v=>update('permitir_registro_publico',v)}/></Section>
      <Section icon={HardDrive} title="Evidencias" description="Parámetros de almacenamiento, compresión y retención."><Field label="Tamaño máximo upload MB"><input type="number" min="1" max="200" value={form.upload_max_mb} onChange={e=>update('upload_max_mb',e.target.value)}/></Field><Field label="Retención evidencias meses"><input type="number" min="1" value={form.retencion_evidencias_meses} onChange={e=>update('retencion_evidencias_meses',e.target.value)}/></Field><Toggle label="Optimizar imágenes WEBP" checked={form.evidencias_webp} onChange={v=>update('evidencias_webp',v)}/><Toggle label="Generar preview" checked={form.evidencias_preview} onChange={v=>update('evidencias_preview',v)}/><Toggle label="Generar thumbnail" checked={form.evidencias_thumbnail} onChange={v=>update('evidencias_thumbnail',v)}/></Section>
      <Section icon={Bell} title="Notificaciones SMTP" description="Configuración base para avisos y alertas."><Toggle label="Notificaciones activas" checked={form.notificaciones_activas} onChange={v=>update('notificaciones_activas',v)}/><Toggle label="SMTP activo" checked={form.smtp_activo} onChange={v=>update('smtp_activo',v)}/><Field label="SMTP host"><input value={form.smtp_host||''} onChange={e=>update('smtp_host',e.target.value)}/></Field><Field label="SMTP puerto"><input type="number" value={form.smtp_puerto||''} onChange={e=>update('smtp_puerto',e.target.value)}/></Field><Field label="SMTP usuario"><input value={form.smtp_usuario||''} onChange={e=>update('smtp_usuario',e.target.value)}/></Field><Field label="SMTP from"><input value={form.smtp_from||''} onChange={e=>update('smtp_from',e.target.value)}/></Field></Section>
      <Section icon={DatabaseBackup} title="Backups" description="Parámetros administrativos de copias de seguridad."><Toggle label="Backups activos" checked={form.backups_activos} onChange={v=>update('backups_activos',v)}/><Field label="Frecuencia"><select value={form.backups_frecuencia} onChange={e=>update('backups_frecuencia',e.target.value)}><option value="DIARIO">DIARIO</option><option value="SEMANAL">SEMANAL</option><option value="MENSUAL">MENSUAL</option></select></Field><Field label="Retención días"><input type="number" min="1" value={form.backups_retencion_dias} onChange={e=>update('backups_retencion_dias',e.target.value)}/></Field></Section>
      <Section icon={Wrench} title="Mantenimiento" description="Control visual y operativo para modo mantenimiento."><Toggle label="Modo mantenimiento activo" checked={form.mantenimiento_activo} onChange={v=>update('mantenimiento_activo',v)}/><Field label="Mensaje mantenimiento"><textarea value={form.mantenimiento_mensaje||''} onChange={e=>update('mantenimiento_mensaje',e.target.value)} rows={4}/></Field><Field label="Observaciones internas"><textarea value={form.observaciones||''} onChange={e=>update('observaciones',e.target.value)} rows={4}/></Field></Section>
      <div className="cs-actions"><button className="cs-btn primary" type="submit" disabled={saving}>{saving ? <Loader2 className="cs-spin" size={18}/> : <Save size={18}/>} {saving ? "Guardando..." : "Guardar configuración"}</button><div className="cs-safe-note"><ShieldCheck size={18}/>Solo SUPER_ADMIN puede modificar estos parámetros.</div></div>
    </form>
  </section>;
}

import React, { useEffect, useState } from "react";
import { ClipboardCheck, Flame, RefreshCcw, ShieldAlert, Siren, Trash2, Users } from "lucide-react";

import api from "../../api/axios";
import { getStoredUser } from "../../utils/security";
import {
  crearAmenaza, crearBrigada, crearInspeccion, crearSimulacro,
  eliminarAmenaza, eliminarBrigada, eliminarInspeccion, eliminarSimulacro,
  listarAmenazas, listarBrigadas, listarInspecciones, listarSimulacros,
} from "../../api/emergenciasSstApi";
import "../../styles/gestion-sst-modules.css";

const usuario = getStoredUser() || {};
const puedeEditar = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"].includes(String(usuario.rol || "").toUpperCase());

const RECURSOS = {
  amenazas: { titulo: "Amenazas", icono: ShieldAlert, listar: listarAmenazas, crear: crearAmenaza, eliminar: eliminarAmenaza },
  brigadas: { titulo: "Brigadas", icono: Users, listar: listarBrigadas, crear: crearBrigada, eliminar: eliminarBrigada },
  simulacros: { titulo: "Simulacros", icono: Flame, listar: listarSimulacros, crear: crearSimulacro, eliminar: eliminarSimulacro },
  inspecciones: { titulo: "Inspecciones", icono: ClipboardCheck, listar: listarInspecciones, crear: crearInspeccion, eliminar: eliminarInspeccion },
};

const formulariosIniciales = {
  amenazas: { nombre: "", tipo_amenaza: "NATURAL", probabilidad: "MEDIA", impacto: "MEDIO", descripcion: "", medidas_control: "" },
  brigadas: { nombre: "", tipo_brigada: "EVACUACION", descripcion: "", fecha_conformacion: "" },
  simulacros: { codigo: "SIM-001", nombre: "", tipo_emergencia: "EVACUACION", fecha_programada: "", lugar: "", observaciones: "" },
  inspecciones: { codigo: "IE-001", nombre: "", tipo_inspeccion: "EQUIPOS_EMERGENCIA", fecha_inspeccion: "", lugar: "", estado_equipo: "BUENO", hallazgos: "" },
};

function detalleError(error) { return error?.response?.data?.detail || error?.message || "No fue posible completar la operación."; }

export default function EmergenciasSSTPage() {
  const [empresas, setEmpresas] = useState([]);
  const [empresaId, setEmpresaId] = useState(usuario.empresa_id || "");
  const [activo, setActivo] = useState("amenazas");
  const [datos, setDatos] = useState({ amenazas: [], brigadas: [], simulacros: [], inspecciones: [] });
  const [formularios, setFormularios] = useState(formulariosIniciales);
  const [mensaje, setMensaje] = useState("");
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    api.get("/empresas/").then(({ data }) => {
      const lista = Array.isArray(data) ? data : [];
      setEmpresas(lista);
      if (!empresaId && lista[0]?.id) setEmpresaId(lista[0].id);
    }).catch((error) => setMensaje(detalleError(error)));
  }, []);

  async function cargarTodo() {
    if (!empresaId) return;
    setCargando(true);
    try {
      const [amenazas, brigadas, simulacros, inspecciones] = await Promise.all([
        listarAmenazas(empresaId), listarBrigadas(empresaId), listarSimulacros(empresaId), listarInspecciones(empresaId),
      ]);
      setDatos({ amenazas, brigadas, simulacros, inspecciones });
      setMensaje("");
    } catch (error) {
      setMensaje(detalleError(error));
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => { cargarTodo(); }, [empresaId]);

  function cambiarCampo(campo, valor) {
    setFormularios((actual) => ({ ...actual, [activo]: { ...actual[activo], [campo]: valor } }));
  }

  async function guardar(event) {
    event.preventDefault();
    try {
      await RECURSOS[activo].crear({ ...formularios[activo], empresa_id: Number(empresaId) });
      setFormularios((actual) => ({ ...actual, [activo]: formulariosIniciales[activo] }));
      await cargarTodo();
    } catch (error) {
      setMensaje(detalleError(error));
    }
  }

  async function borrar(item) {
    if (!window.confirm(`¿Desactivar ${item.nombre}?`)) return;
    try {
      await RECURSOS[activo].eliminar(item.id);
      await cargarTodo();
    } catch (error) {
      setMensaje(detalleError(error));
    }
  }

  const recurso = RECURSOS[activo];
  const IconoActivo = recurso.icono;
  const form = formularios[activo];

  return (
    <main className="gsm-page">
      <header className="gsm-hero gsm-hero--emergency"><div><span className="gsm-kicker">Preparación y respuesta</span><h1>Gestión de emergencias</h1><p>Identifica amenazas, organiza brigadas y documenta simulacros e inspecciones.</p></div><Siren size={56} aria-hidden="true" /></header>
      <section className="gsm-toolbar"><label>Empresa<select value={empresaId} onChange={(e) => setEmpresaId(e.target.value)}>{empresas.map((empresa) => <option key={empresa.id} value={empresa.id}>{empresa.nombre}</option>)}</select></label><button className="gsm-button gsm-button--ghost" onClick={cargarTodo} disabled={cargando}><RefreshCcw size={17} /> Actualizar</button></section>
      {mensaje && <p className="gsm-alert" role="alert">{mensaje}</p>}

      <nav className="gsm-tabs" aria-label="Procesos de emergencias">{Object.entries(RECURSOS).map(([clave, item]) => { const Icono = item.icono; return <button key={clave} className={activo === clave ? "is-active" : ""} onClick={() => setActivo(clave)}><Icono size={18} />{item.titulo}<strong>{datos[clave].length}</strong></button>; })}</nav>

      <section className="gsm-grid gsm-grid--balanced">
        <div className="gsm-panel"><div className="gsm-panel-title"><div><span>Registro activo</span><h2>{recurso.titulo}</h2></div><IconoActivo size={28} /></div><div className="gsm-card-list">{datos[activo].map((item) => <article className="gsm-record" key={item.id}><div><span className={`gsm-badge gsm-badge--${String(item.nivel_riesgo || item.estado || "activo").toLowerCase()}`}>{item.nivel_riesgo || item.estado || item.tipo_brigada || item.tipo_inspeccion}</span><h3>{item.nombre}</h3><p>{item.descripcion || item.lugar || item.hallazgos || "Sin observaciones adicionales"}</p><small>{item.fecha_programada || item.fecha_inspeccion || item.fecha_conformacion || "Fecha no registrada"}</small></div>{puedeEditar && <button className="gsm-icon-button" aria-label={`Eliminar ${item.nombre}`} onClick={() => borrar(item)}><Trash2 size={16} /></button>}</article>)}{!datos[activo].length && <div className="gsm-empty">Aún no hay registros en {recurso.titulo.toLowerCase()}.</div>}</div></div>

        <div className="gsm-panel gsm-panel--form">{puedeEditar ? <form className="gsm-form" onSubmit={guardar}><div className="gsm-panel-title"><div><span>Nuevo registro</span><h2>Agregar {recurso.titulo.toLowerCase()}</h2></div></div>
          {activo === "amenazas" && <><label>Nombre<input required value={form.nombre} onChange={(e) => cambiarCampo("nombre", e.target.value)} /></label><div className="gsm-form-grid"><label>Tipo<select value={form.tipo_amenaza} onChange={(e) => cambiarCampo("tipo_amenaza", e.target.value)}><option>NATURAL</option><option>TECNOLOGICA</option><option>SOCIOPOLITICA</option></select></label><label>Probabilidad<select value={form.probabilidad} onChange={(e) => cambiarCampo("probabilidad", e.target.value)}><option>BAJA</option><option>MEDIA</option><option>ALTA</option></select></label><label>Impacto<select value={form.impacto} onChange={(e) => cambiarCampo("impacto", e.target.value)}><option>BAJO</option><option>MEDIO</option><option>ALTO</option></select></label></div><label>Medidas de control<textarea rows="4" value={form.medidas_control} onChange={(e) => cambiarCampo("medidas_control", e.target.value)} /></label></>}
          {activo === "brigadas" && <><label>Nombre<input required value={form.nombre} onChange={(e) => cambiarCampo("nombre", e.target.value)} /></label><div className="gsm-form-grid"><label>Tipo<select value={form.tipo_brigada} onChange={(e) => cambiarCampo("tipo_brigada", e.target.value)}><option>EVACUACION</option><option>INCENDIO</option><option>PRIMEROS_AUXILIOS</option><option>RESCATE</option></select></label><label>Fecha de conformación<input type="date" value={form.fecha_conformacion} onChange={(e) => cambiarCampo("fecha_conformacion", e.target.value)} /></label></div><label>Descripción<textarea rows="4" value={form.descripcion} onChange={(e) => cambiarCampo("descripcion", e.target.value)} /></label></>}
          {activo === "simulacros" && <><div className="gsm-form-grid"><label>Código<input required value={form.codigo} onChange={(e) => cambiarCampo("codigo", e.target.value)} /></label><label>Fecha programada<input type="date" required value={form.fecha_programada} onChange={(e) => cambiarCampo("fecha_programada", e.target.value)} /></label></div><label>Nombre<input required value={form.nombre} onChange={(e) => cambiarCampo("nombre", e.target.value)} /></label><div className="gsm-form-grid"><label>Tipo<select value={form.tipo_emergencia} onChange={(e) => cambiarCampo("tipo_emergencia", e.target.value)}><option>EVACUACION</option><option>INCENDIO</option><option>SISMO</option><option>DERRAME</option><option>OTRO</option></select></label><label>Lugar<input value={form.lugar} onChange={(e) => cambiarCampo("lugar", e.target.value)} /></label></div></>}
          {activo === "inspecciones" && <><div className="gsm-form-grid"><label>Código<input required value={form.codigo} onChange={(e) => cambiarCampo("codigo", e.target.value)} /></label><label>Fecha<input type="date" required value={form.fecha_inspeccion} onChange={(e) => cambiarCampo("fecha_inspeccion", e.target.value)} /></label></div><label>Nombre<input required value={form.nombre} onChange={(e) => cambiarCampo("nombre", e.target.value)} /></label><div className="gsm-form-grid"><label>Tipo<select value={form.tipo_inspeccion} onChange={(e) => cambiarCampo("tipo_inspeccion", e.target.value)}><option>EQUIPOS_EMERGENCIA</option><option>RUTAS_EVACUACION</option><option>SEÑALIZACION</option><option>BRIGADAS</option></select></label><label>Estado del equipo<select value={form.estado_equipo} onChange={(e) => cambiarCampo("estado_equipo", e.target.value)}><option>BUENO</option><option>REGULAR</option><option>MALO</option></select></label></div><label>Hallazgos<textarea rows="4" value={form.hallazgos} onChange={(e) => cambiarCampo("hallazgos", e.target.value)} /></label></>}
          <button className="gsm-button" type="submit">Guardar registro</button></form> : <div className="gsm-empty gsm-empty--large"><Siren size={44} /><h2>Consulta habilitada</h2><p>Tu rol tiene acceso de lectura a este módulo.</p></div>}</div>
      </section>
    </main>
  );
}

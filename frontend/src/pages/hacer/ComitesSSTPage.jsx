import React, { useEffect, useState } from "react";
import { CalendarDays, Plus, RefreshCcw, Trash2, UserRoundCheck, Users } from "lucide-react";

import api from "../../api/axios";
import { getStoredUser } from "../../utils/security";
import {
  agregarIntegrante,
  crearComite,
  crearReunion,
  eliminarComite,
  eliminarIntegrante,
  listarComites,
  listarIntegrantes,
  listarReuniones,
} from "../../api/comitesSstApi";
import "../../styles/gestion-sst-modules.css";

const usuario = getStoredUser() || {};
const puedeEditar = ["SUPER_ADMIN", "ADMIN_EMPRESA", "RESPONSABLE_SST"].includes(
  String(usuario.rol || "").toUpperCase(),
);

const comiteInicial = { tipo_comite: "COPASST", nombre: "", descripcion: "", fecha_constitucion: "", fecha_fin_periodo: "" };
const integranteInicial = { nombre: "", documento: "", cargo: "", rol_comite: "INTEGRANTE", representa: "EMPLEADOS" };
const reunionInicial = { numero_reunion: 1, fecha_reunion: "", lugar: "", tema: "", compromisos: "", total_asistentes: 0 };

function detalleError(error) {
  return error?.response?.data?.detail || error?.message || "No fue posible completar la operación.";
}

export default function ComitesSSTPage() {
  const [empresas, setEmpresas] = useState([]);
  const [empresaId, setEmpresaId] = useState(usuario.empresa_id || "");
  const [comites, setComites] = useState([]);
  const [seleccionado, setSeleccionado] = useState(null);
  const [integrantes, setIntegrantes] = useState([]);
  const [reuniones, setReuniones] = useState([]);
  const [form, setForm] = useState(comiteInicial);
  const [formIntegrante, setFormIntegrante] = useState(integranteInicial);
  const [formReunion, setFormReunion] = useState(reunionInicial);
  const [mensaje, setMensaje] = useState("");
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    api.get("/empresas/").then(({ data }) => {
      const lista = Array.isArray(data) ? data : [];
      setEmpresas(lista);
      if (!empresaId && lista[0]?.id) setEmpresaId(lista[0].id);
    }).catch((error) => setMensaje(detalleError(error)));
  }, []);

  async function cargarComites() {
    if (!empresaId) return;
    setCargando(true);
    try {
      const lista = await listarComites({ empresa_id: empresaId });
      setComites(lista);
      if (seleccionado && !lista.some((item) => item.id === seleccionado.id)) setSeleccionado(null);
      setMensaje("");
    } catch (error) {
      setMensaje(detalleError(error));
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => { cargarComites(); }, [empresaId]);

  async function abrirComite(comite) {
    setSeleccionado(comite);
    try {
      const [personas, sesiones] = await Promise.all([
        listarIntegrantes(comite.id),
        listarReuniones(comite.id),
      ]);
      setIntegrantes(personas);
      setReuniones(sesiones);
    } catch (error) {
      setMensaje(detalleError(error));
    }
  }

  async function guardarComite(event) {
    event.preventDefault();
    try {
      await crearComite({ ...form, empresa_id: Number(empresaId) });
      setForm(comiteInicial);
      await cargarComites();
    } catch (error) {
      setMensaje(detalleError(error));
    }
  }

  async function guardarIntegrante(event) {
    event.preventDefault();
    try {
      await agregarIntegrante(seleccionado.id, formIntegrante);
      setFormIntegrante(integranteInicial);
      await abrirComite(seleccionado);
      await cargarComites();
    } catch (error) {
      setMensaje(detalleError(error));
    }
  }

  async function guardarReunion(event) {
    event.preventDefault();
    try {
      await crearReunion(seleccionado.id, { ...formReunion, numero_reunion: Number(formReunion.numero_reunion), total_asistentes: Number(formReunion.total_asistentes) });
      setFormReunion({ ...reunionInicial, numero_reunion: Number(formReunion.numero_reunion) + 1 });
      await abrirComite(seleccionado);
      await cargarComites();
    } catch (error) {
      setMensaje(detalleError(error));
    }
  }

  return (
    <main className="gsm-page">
      <header className="gsm-hero gsm-hero--committees">
        <div><span className="gsm-kicker">Participación y consulta</span><h1>Comités SST</h1><p>Conformación, períodos, integrantes y reuniones del COPASST, Vigía SST y Comité de Convivencia.</p></div>
        <UserRoundCheck size={54} aria-hidden="true" />
      </header>

      <section className="gsm-toolbar">
        <label>Empresa<select value={empresaId} onChange={(e) => { setEmpresaId(e.target.value); setSeleccionado(null); }}>{empresas.map((empresa) => <option key={empresa.id} value={empresa.id}>{empresa.nombre}</option>)}</select></label>
        <button className="gsm-button gsm-button--ghost" onClick={cargarComites} disabled={cargando}><RefreshCcw size={17} /> Actualizar</button>
      </section>
      {mensaje && <p className="gsm-alert" role="alert">{mensaje}</p>}

      <section className="gsm-grid">
        <div className="gsm-panel">
          <div className="gsm-panel-title"><div><span>Gobernanza</span><h2>Comités vigentes</h2></div><strong>{comites.length}</strong></div>
          <div className="gsm-card-list">
            {comites.map((comite) => <article key={comite.id} className={`gsm-record ${seleccionado?.id === comite.id ? "is-active" : ""}`} onClick={() => abrirComite(comite)}>
              <div><span className="gsm-badge">{comite.tipo_comite.replaceAll("_", " ")}</span><h3>{comite.nombre}</h3><p>{comite.total_integrantes} integrantes · {comite.total_reuniones} reuniones</p></div>
              {puedeEditar && <button className="gsm-icon-button" aria-label={`Eliminar ${comite.nombre}`} onClick={async (e) => { e.stopPropagation(); if (window.confirm("¿Desactivar este comité?")) { await eliminarComite(comite.id); setSeleccionado(null); cargarComites(); } }}><Trash2 size={16} /></button>}
            </article>)}
            {!comites.length && <div className="gsm-empty">No hay comités registrados para esta empresa.</div>}
          </div>
          {puedeEditar && <form className="gsm-form" onSubmit={guardarComite}>
            <h3><Plus size={18} /> Nuevo comité</h3>
            <div className="gsm-form-grid"><label>Tipo<select value={form.tipo_comite} onChange={(e) => setForm({ ...form, tipo_comite: e.target.value })}><option value="COPASST">COPASST</option><option value="VIGIA_SST">Vigía SST</option><option value="CONVIVENCIA">Convivencia laboral</option></select></label><label>Nombre<input required value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} /></label><label>Constitución<input type="date" value={form.fecha_constitucion} onChange={(e) => setForm({ ...form, fecha_constitucion: e.target.value })} /></label><label>Fin del período<input type="date" value={form.fecha_fin_periodo} onChange={(e) => setForm({ ...form, fecha_fin_periodo: e.target.value })} /></label></div>
            <button className="gsm-button" type="submit"><Plus size={17} /> Crear comité</button>
          </form>}
        </div>

        <div className="gsm-panel gsm-panel--detail">
          {!seleccionado ? <div className="gsm-empty gsm-empty--large"><Users size={44} /><h2>Selecciona un comité</h2><p>Consulta sus integrantes y la trazabilidad de reuniones.</p></div> : <>
            <div className="gsm-panel-title"><div><span>{seleccionado.tipo_comite.replaceAll("_", " ")}</span><h2>{seleccionado.nombre}</h2></div></div>
            <div className="gsm-columns">
              <section><h3><Users size={18} /> Integrantes</h3>{integrantes.map((item) => <div className="gsm-line" key={item.id}><div><strong>{item.nombre}</strong><small>{item.rol_comite} · {item.representa || "Sin representación"}</small></div>{puedeEditar && <button className="gsm-icon-button" aria-label={`Remover ${item.nombre}`} onClick={async () => { await eliminarIntegrante(seleccionado.id, item.id); abrirComite(seleccionado); }}><Trash2 size={15} /></button>}</div>)}
                {puedeEditar && <form className="gsm-form gsm-form--compact" onSubmit={guardarIntegrante}><label>Nombre<input required value={formIntegrante.nombre} onChange={(e) => setFormIntegrante({ ...formIntegrante, nombre: e.target.value })} /></label><div className="gsm-form-grid"><label>Rol<select value={formIntegrante.rol_comite} onChange={(e) => setFormIntegrante({ ...formIntegrante, rol_comite: e.target.value })}><option>PRESIDENTE</option><option>SECRETARIO</option><option>INTEGRANTE</option><option>SUPLENTE</option></select></label><label>Representa<select value={formIntegrante.representa} onChange={(e) => setFormIntegrante({ ...formIntegrante, representa: e.target.value })}><option>EMPLEADOS</option><option>DIRECCION</option><option>CONTRATISTAS</option></select></label></div><button className="gsm-button" type="submit">Agregar integrante</button></form>}
              </section>
              <section><h3><CalendarDays size={18} /> Reuniones</h3>{reuniones.map((item) => <div className="gsm-line" key={item.id}><div><strong>Reunión {item.numero_reunion}</strong><small>{item.fecha_reunion} · {item.estado}</small><p>{item.tema || "Sin tema registrado"}</p></div></div>)}
                {puedeEditar && <form className="gsm-form gsm-form--compact" onSubmit={guardarReunion}><div className="gsm-form-grid"><label>Número<input type="number" min="1" required value={formReunion.numero_reunion} onChange={(e) => setFormReunion({ ...formReunion, numero_reunion: e.target.value })} /></label><label>Fecha<input type="date" required value={formReunion.fecha_reunion} onChange={(e) => setFormReunion({ ...formReunion, fecha_reunion: e.target.value })} /></label></div><label>Tema<input value={formReunion.tema} onChange={(e) => setFormReunion({ ...formReunion, tema: e.target.value })} /></label><label>Compromisos<textarea rows="3" value={formReunion.compromisos} onChange={(e) => setFormReunion({ ...formReunion, compromisos: e.target.value })} /></label><button className="gsm-button" type="submit">Registrar reunión</button></form>}
              </section>
            </div>
          </>}
        </div>
      </section>
    </main>
  );
}

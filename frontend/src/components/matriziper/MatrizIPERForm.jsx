import React, { useState, useEffect, useMemo } from "react";
import { Save, Plus, Trash2, AlertTriangle } from "lucide-react";
import { toastWarning } from "../../utils/toast";

const CLASIFICACIONES_PELIGRO = [
  "FISICO",
  "QUIMICO",
  "BIOLOGICO",
  "BIOMECANICO",
  "PSICOSOCIAL",
  "CONDICIONES_SEGURIDAD",
  "FENOMENOS_NATURALES",
];

const CLASIFICACION_LABELS = {
  FISICO: "Físico",
  QUIMICO: "Químico",
  BIOLOGICO: "Biológico",
  BIOMECANICO: "Biomecánico",
  PSICOSOCIAL: "Psicosocial",
  CONDICIONES_SEGURIDAD: "Condiciones de Seguridad",
  FENOMENOS_NATURALES: "Fenómenos Naturales",
};

const ND_OPCIONES = [
  { valor: 0, etiqueta: "Bajo (B)", valor_nd: "Sin valor", significado: "No se ha detectado consecuencia alguna, o la eficacia del conjunto de medidas preventivas existentes es alta. El riesgo está controlado." },
  { valor: 2, etiqueta: "Medio (M)", valor_nd: 2, significado: "Se han detectado peligros que pueden dar lugar a consecuencias poco significativas o de menor importancia, o la eficacia de las medidas preventivas es moderada." },
  { valor: 6, etiqueta: "Alto (A)", valor_nd: 6, significado: "Se han detectado algún(os) peligro(s) que pueden dar lugar a consecuencias significativas, o la eficacia de las medidas preventivas existentes es baja." },
  { valor: 10, etiqueta: "Muy Alto (MA)", valor_nd: 10, significado: "Se ha(n) detectado peligro(s) que determina(n) como posible la generación de incidentes o consecuencias muy significativas, o la eficacia de las medidas preventivas es nula o no existe." },
];

const NE_OPCIONES = [
  { valor: 4, etiqueta: "Continua (EC)", valor_ne: 4, significado: "Varias veces en la jornada y de manera continuada, tiempo prolongado." },
  { valor: 3, etiqueta: "Frecuente (EF)", valor_ne: 3, significado: "Varias veces en la jornada." },
  { valor: 2, etiqueta: "Ocasional (EO)", valor_ne: 2, significado: "Alguna vez en la jornada." },
  { valor: 1, etiqueta: "Esporádica (EE)", valor_ne: 1, significado: "De manera eventual." },
];

const NC_OPCIONES = [
  { valor: 100, etiqueta: "Mortal / Catastrófico (M)", valor_nc: 100, significado: "Muerte(s)." },
  { valor: 60, etiqueta: "Muy Grave (MG)", valor_nc: 60, significado: "Lesiones o enfermedades graves irreparables (incapacidad permanente parcial o invalidez)." },
  { valor: 25, etiqueta: "Grave (G)", valor_nc: 25, significado: "Lesiones o enfermedades con incapacidad laboral temporal (ILT)." },
  { valor: 10, etiqueta: "Leve (L)", valor_nc: 10, significado: "Lesiones o enfermedades que no requieren incapacidad." },
];

function interpretarNP(np) {
  if (np >= 24) return "MA";
  if (np >= 10) return "A";
  if (np >= 6) return "M";
  return "B";
}

function interpretarNPTexto(np) {
  if (np >= 24) return "Muy Alto";
  if (np >= 10) return "Alto";
  if (np >= 6) return "Medio";
  return "Bajo";
}

function interpretarNR(nr) {
  if (nr >= 600) return "I";
  if (nr >= 150) return "II";
  if (nr >= 40) return "III";
  return "IV";
}

function interpretarNRTexto(nr) {
  if (nr >= 600) return "No Aceptable";
  if (nr >= 150) return "No Aceptable / Control Específico";
  if (nr >= 40) return "Aceptable Mejorable";
  return "Aceptable";
}

function aceptabilidad(nr) {
  if (nr >= 600) return "NO ACEPTABLE";
  if (nr >= 150) return "CON CONTROL ESPECÍFICO";
  if (nr >= 40) return "MEJORABLE";
  return "ACEPTABLE";
}

function colorNR(nr) {
  if (nr >= 600) return "nr-critico";
  if (nr >= 150) return "nr-alto";
  if (nr >= 40) return "nr-medio";
  return "nr-bajo";
}

const FILA_VACIA = {
  proceso: "",
  zona_lugar: "",
  actividades: "",
  tareas: "",
  rutinaria: "SI",
  clasificacion_peligro: "FISICO",
  descripcion_peligro: "",
  riesgo: "",
  efectos_posibles: "",
  fuente: "",
  medio: "",
  individuo: "",
  nd: 0,
  ne: 1,
  nc: 10,
  expuestos_hombres: 0,
  expuestos_mujeres: 0,
  expuestos_gestantes: 0,
  peor_consecuencia: "",
  eliminacion: "",
  control_ingenieria: "",
  sustitucion: "",
  senalizacion_admin: "",
  epp: "",
  responsable: "",
  fecha_proyectada: "",
  fecha_ejecucion: "",
  evidencias: "",
  realizado: "NO",
};

export default function MatrizIPERForm({ onGuardar, onGuardarAvances, initialData, editMode }) {
  const [filas, setFilas] = useState(initialData ? [initialData] : [{ ...FILA_VACIA }]);
  const [errores, setErrores] = useState({});

  const agregarFila = () => {
    setFilas([...filas, { ...FILA_VACIA }]);
  };

  const eliminarFila = (index) => {
    if (filas.length <= 1) return;
    setFilas(filas.filter((_, i) => i !== index));
  };

  const actualizarFila = (index, campo, valor) => {
    const nuevasFilas = [...filas];
    nuevasFilas[index] = { ...nuevasFilas[index], [campo]: valor };
    setFilas(nuevasFilas);

    if (errores[index]) {
      const nuevosErrores = { ...errores };
      delete nuevosErrores[index];
      setErrores(nuevosErrores);
    }
  };

  const calcularNP = (nd, ne) => nd * ne;
  const calcularNR = (np, nc) => np * nc;

  const resumenFilas = useMemo(() => {
    return filas.map((f) => {
      const np = calcularNP(f.nd, f.ne);
      const nr = calcularNR(np, f.nc);
      return {
        np,
        nr,
        interpNP: interpretarNPTexto(np),
        interpNR: interpretarNRTexto(nr),
        acept: aceptabilidad(nr),
        claseNR: colorNR(nr),
      };
    });
  }, [filas]);

  const validar = () => {
    const errs = {};
    filas.forEach((f, i) => {
      const campos = [];
      if (!f.proceso.trim()) campos.push("proceso");
      if (!f.descripcion_peligro.trim()) campos.push("descripción del peligro");
      if (!f.efectos_posibles.trim()) campos.push("efectos posibles");
      if (campos.length > 0) errs[i] = campos;
    });
    setErrores(errs);
    return Object.keys(errs).length === 0;
  };

  const handleGuardar = () => {
    if (!validar()) {
      toastWarning("Advertencia", "Complete los campos obligatorios marcados en las filas con error.");
      return;
    }

    const datos = filas.map((f, i) => ({
      ...f,
      np: resumenFilas[i].np,
      nr: resumenFilas[i].nr,
      interpretacion_np: resumenFilas[i].interpNP,
      interpretacion_nr: resumenFilas[i].interpNR,
      aceptabilidad: resumenFilas[i].acept,
    }));

    if (onGuardar) onGuardar(datos);
    else toastWarning("Advertencia", "Formulario listo. Funcionalidad de guardado pendiente de conectar con backend.");
  };

  return (
    <div className="iper-form-container">
      <div className="iper-header">
        <h2>Matriz IPER - Identificación de Peligros, Evaluación y Valoración de Riesgos</h2>
        <p className="iper-subtitle">
          Metodología GTC 45 (Segunda actualización) — Decreto 1072 de 2015 — Resolución 0312 de 2019
        </p>
      </div>

      <div className="iper-filas">
        {filas.map((fila, index) => {
          const calc = resumenFilas[index];
          const tieneError = errores[index];

          return (
            <div key={index} className={`iper-fila-card ${tieneError ? "con-error" : ""}`}>
              <div className="iper-fila-header">
                <span className="iper-fila-numero">#{index + 1}</span>
                {tieneError && (
                  <span className="iper-fila-error">
                    <AlertTriangle size={14} /> Campos obligatorios: {errores[index].join(", ")}
                  </span>
                )}
                {filas.length > 1 && (
                  <button
                    type="button"
                    className="iper-btn-eliminar"
                    onClick={() => eliminarFila(index)}
                    title="Eliminar fila"
                  >
                    <Trash2 size={15} />
                  </button>
                )}
              </div>

              {/* SECCIÓN 1: CONTEXTO */}
              <fieldset className="iper-seccion">
                <legend>1. Contexto del Proceso</legend>
                <div className="iper-campos-grid">
                  <div className="iper-campo">
                    <label>Proceso *</label>
                    <input
                      type="text"
                      value={fila.proceso}
                      onChange={(e) => actualizarFila(index, "proceso", e.target.value)}
                      placeholder="Ej: Administrativo, Operativo"
                      className={tieneError?.includes("proceso") ? "campo-error" : ""}
                    />
                  </div>
                  <div className="iper-campo">
                    <label>Zona / Lugar</label>
                    <input
                      type="text"
                      value={fila.zona_lugar}
                      onChange={(e) => actualizarFila(index, "zona_lugar", e.target.value)}
                      placeholder="Ej: Sede Administrativa"
                    />
                  </div>
                  <div className="iper-campo">
                    <label>Actividades</label>
                    <input
                      type="text"
                      value={fila.actividades}
                      onChange={(e) => actualizarFila(index, "actividades", e.target.value)}
                      placeholder="Ej: Director Operativo"
                    />
                  </div>
                  <div className="iper-campo">
                    <label>Tareas</label>
                    <textarea
                      value={fila.tareas}
                      onChange={(e) => actualizarFila(index, "tareas", e.target.value)}
                      placeholder="Ej: Realizar informes, ingresar datos al sistema"
                      rows={2}
                    />
                  </div>
                  <div className="iper-campo">
                    <label>Rutinaria</label>
                    <select
                      value={fila.rutinaria}
                      onChange={(e) => actualizarFila(index, "rutinaria", e.target.value)}
                    >
                      <option value="SI">Sí</option>
                      <option value="NO">No</option>
                    </select>
                  </div>
                </div>
              </fieldset>

              {/* SECCIÓN 2: PELIGRO */}
              <fieldset className="iper-seccion">
                <legend>2. Identificación del Peligro</legend>
                <div className="iper-campos-grid">
                  <div className="iper-campo">
                    <label>Clasificación *</label>
                    <select
                      value={fila.clasificacion_peligro}
                      onChange={(e) => actualizarFila(index, "clasificacion_peligro", e.target.value)}
                    >
                      {CLASIFICACIONES_PELIGRO.map((c) => (
                        <option key={c} value={c}>
                          {CLASIFICACION_LABELS[c]}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="iper-campo span-2">
                    <label>Descripción del Peligro *</label>
                    <textarea
                      value={fila.descripcion_peligro}
                      onChange={(e) => actualizarFila(index, "descripcion_peligro", e.target.value)}
                      placeholder="Ej: Movimientos repetitivos al digitalizar, utilización del mouse"
                      rows={2}
                      className={tieneError?.includes("descripción del peligro") ? "campo-error" : ""}
                    />
                  </div>
                  <div className="iper-campo">
                    <label>Riesgo (Efecto)</label>
                    <input
                      type="text"
                      value={fila.riesgo}
                      onChange={(e) => actualizarFila(index, "riesgo", e.target.value)}
                      placeholder="Ej: Fatiga muscular"
                    />
                  </div>
                  <div className="iper-campo span-2">
                    <label>Efectos Posibles *</label>
                    <textarea
                      value={fila.efectos_posibles}
                      onChange={(e) => actualizarFila(index, "efectos_posibles", e.target.value)}
                      placeholder="Ej: Tendinitis, bursitis, síndrome del túnel carpiano"
                      rows={2}
                      className={tieneError?.includes("efectos posibles") ? "campo-error" : ""}
                    />
                  </div>
                </div>
              </fieldset>

              {/* SECCIÓN 3: CONTROLES EXISTENTES */}
              <fieldset className="iper-seccion">
                <legend>3. Controles Existentes</legend>
                <div className="iper-campos-grid tres">
                  <div className="iper-campo">
                    <label>Fuente</label>
                    <input
                      type="text"
                      value={fila.fuente}
                      onChange={(e) => actualizarFila(index, "fuente", e.target.value)}
                      placeholder="Ej: Ninguno"
                    />
                  </div>
                  <div className="iper-campo">
                    <label>Medio</label>
                    <input
                      type="text"
                      value={fila.medio}
                      onChange={(e) => actualizarFila(index, "medio", e.target.value)}
                      placeholder="Ej: Desinfección de áreas"
                    />
                  </div>
                  <div className="iper-campo">
                    <label>Individuo</label>
                    <input
                      type="text"
                      value={fila.individuo}
                      onChange={(e) => actualizarFila(index, "individuo", e.target.value)}
                      placeholder="Ej: Tapabocas"
                    />
                  </div>
                </div>
              </fieldset>

              {/* SECCIÓN 4: EVALUACIÓN GTC45 */}
              <fieldset className="iper-seccion seccion-valoracion">
                <legend>4. Evaluación del Riesgo (GTC 45)</legend>

                <div className="iper-campos-grid">
                  <div className="iper-campo">
                    <label>Nivel de Deficiencia (ND)</label>
                    <select
                      value={fila.nd}
                      onChange={(e) => actualizarFila(index, "nd", Number(e.target.value))}
                    >
                      {ND_OPCIONES.map((o) => (
                        <option key={o.valor} value={o.valor}>
                          {o.etiqueta} — Valor ND: {o.valor_nd}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="iper-campo">
                    <label>Nivel de Exposición (NE)</label>
                    <select
                      value={fila.ne}
                      onChange={(e) => actualizarFila(index, "ne", Number(e.target.value))}
                    >
                      {NE_OPCIONES.map((o) => (
                        <option key={o.valor} value={o.valor}>
                          {o.etiqueta} — Valor NE: {o.valor_ne}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="iper-campo">
                    <label>Nivel de Consecuencia (NC)</label>
                    <select
                      value={fila.nc}
                      onChange={(e) => actualizarFila(index, "nc", Number(e.target.value))}
                    >
                      {NC_OPCIONES.map((o) => (
                        <option key={o.valor} value={o.valor}>
                          {o.etiqueta} — Valor NC: {o.valor_nc}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="iper-calculos">
                  <div className="iper-calc-item">
                    <span className="calc-label">NP = ND × NE</span>
                    <span className="calc-valor">{fila.nd} × {fila.ne} = <strong>{calc.np}</strong></span>
                    <span className="calc-interp">({calc.interpNP})</span>
                  </div>
                  <div className="iper-calc-item">
                    <span className="calc-label">NR = NP × NC</span>
                    <span className="calc-valor">{calc.np} × {fila.nc} = <strong>{calc.nr}</strong></span>
                  </div>
                  <div className={`iper-calc-item resultado ${calc.claseNR}`}>
                    <span className="calc-label">Nivel de Riesgo</span>
                    <span className="calc-valor">
                      <strong>Nivel {interpretarNR(calc.nr)}</strong> — {calc.interpNR}
                    </span>
                  </div>
                  <div className={`iper-calc-item aceptabilidad ${calc.claseNR}`}>
                    <span className="calc-label">Aceptabilidad</span>
                    <span className="calc-valor"><strong>{calc.acept}</strong></span>
                  </div>
                </div>
              </fieldset>

              {/* SECCIÓN 5: CRITERIOS PARA ESTABLECER CONTROLES */}
              <fieldset className="iper-seccion">
                <legend>5. Criterios para Establecer Controles</legend>
                <div className="iper-campos-grid">
                  <div className="iper-campo">
                    <label>Nro. Expuestos Hombres</label>
                    <input
                      type="number"
                      min="0"
                      value={fila.expuestos_hombres}
                      onChange={(e) => actualizarFila(index, "expuestos_hombres", Number(e.target.value))}
                    />
                  </div>
                  <div className="iper-campo">
                    <label>Nro. Expuestos Mujeres</label>
                    <input
                      type="number"
                      min="0"
                      value={fila.expuestos_mujeres}
                      onChange={(e) => actualizarFila(index, "expuestos_mujeres", Number(e.target.value))}
                    />
                  </div>
                  <div className="iper-campo">
                    <label>Gestantes / Lactantes</label>
                    <input
                      type="number"
                      min="0"
                      value={fila.expuestos_gestantes}
                      onChange={(e) => actualizarFila(index, "expuestos_gestantes", Number(e.target.value))}
                    />
                  </div>
                  <div className="iper-campo span-2">
                    <label>Peor Consecuencia</label>
                    <input
                      type="text"
                      value={fila.peor_consecuencia}
                      onChange={(e) => actualizarFila(index, "peor_consecuencia", e.target.value)}
                      placeholder="Ej: Síndrome del túnel carpiano"
                    />
                  </div>
                </div>
              </fieldset>

              {/* SECCIÓN 6: MEDIDAS DE INTERVENCIÓN */}
              <fieldset className="iper-seccion">
                <legend>6. Medidas de Intervención (Jerarquía de Controles)</legend>
                <div className="iper-campos-grid">
                  <div className="iper-campo">
                    <label>Eliminación</label>
                    <textarea
                      value={fila.eliminacion}
                      onChange={(e) => actualizarFila(index, "eliminacion", e.target.value)}
                      placeholder="Ej: N.A"
                      rows={2}
                    />
                  </div>
                  <div className="iper-campo">
                    <label>Control de Ingeniería</label>
                    <textarea
                      value={fila.control_ingenieria}
                      onChange={(e) => actualizarFila(index, "control_ingenieria", e.target.value)}
                      placeholder="Ej: N.A"
                      rows={2}
                    />
                  </div>
                  <div className="iper-campo">
                    <label>Sustitución</label>
                    <textarea
                      value={fila.sustitucion}
                      onChange={(e) => actualizarFila(index, "sustitucion", e.target.value)}
                      placeholder="Ej: N.A"
                      rows={2}
                    />
                  </div>
                  <div className="iper-campo">
                    <label>Señalización / Controles Administrativos</label>
                    <textarea
                      value={fila.senalizacion_admin}
                      onChange={(e) => actualizarFila(index, "senalizacion_admin", e.target.value)}
                      placeholder="Ej: Ejercicios de estiramientos, pausas activas"
                      rows={2}
                    />
                  </div>
                  <div className="iper-campo">
                    <label>EPP</label>
                    <textarea
                      value={fila.epp}
                      onChange={(e) => actualizarFila(index, "epp", e.target.value)}
                      placeholder="Ej: Tapabocas, guantes"
                      rows={2}
                    />
                  </div>
                  <div className="iper-campo">
                    <label>Responsable</label>
                    <textarea
                      value={fila.responsable}
                      onChange={(e) => actualizarFila(index, "responsable", e.target.value)}
                      placeholder="Persona responsable de implementar las medidas"
                      rows={2}
                    />
                  </div>
                </div>
              </fieldset>

              {/* SECCIÓN 7: SEGUIMIENTO */}
              <fieldset className="iper-seccion">
                <legend>7. Seguimiento</legend>
                <div className="iper-campos-grid">
                  <div className="iper-campo">
                    <label>Fecha Proyectada</label>
                    <input
                      type="date"
                      value={fila.fecha_proyectada}
                      onChange={(e) => actualizarFila(index, "fecha_proyectada", e.target.value)}
                    />
                  </div>
                  <div className="iper-campo">
                    <label>Fecha de Ejecución</label>
                    <input
                      type="date"
                      value={fila.fecha_ejecucion}
                      onChange={(e) => actualizarFila(index, "fecha_ejecucion", e.target.value)}
                    />
                  </div>
                  <div className="iper-campo">
                    <label>Evidencias</label>
                    <textarea
                      value={fila.evidencias}
                      onChange={(e) => actualizarFila(index, "evidencias", e.target.value)}
                      placeholder="Registro de evidencias del seguimiento"
                      rows={2}
                    />
                  </div>
                  <div className="iper-campo">
                    <label>Realizado</label>
                    <select
                      value={fila.realizado}
                      onChange={(e) => actualizarFila(index, "realizado", e.target.value)}
                    >
                      <option value="NO">NO</option>
                      <option value="SI">SI</option>
                    </select>
                  </div>
                </div>
              </fieldset>
            </div>
          );
        })}
      </div>

      <div className="iper-acciones">
        <button type="button" className="iper-btn-agregar" onClick={agregarFila}>
          <Plus size={17} /> Agregar Fila
        </button>
        <div className="iper-acciones-right">
          {onGuardarAvances && (
            <button type="button" className="iper-btn-guardar-avances" onClick={() => {
              const datos = filas.map((f, i) => ({
                ...f,
                np: resumenFilas[i].np,
                nr: resumenFilas[i].nr,
                interpretacion_np: resumenFilas[i].interpNP,
                interpretacion_nr: resumenFilas[i].interpNR,
                aceptabilidad: resumenFilas[i].acept,
              }));
              onGuardarAvances(datos);
            }}>
              <Save size={17} /> Guardar Avances
            </button>
          )}
          <button type="button" className="iper-btn-guardar" onClick={handleGuardar}>
            <Save size={17} /> {editMode ? "Actualizar Fila" : "Guardar Matriz IPER"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// AUTOCOMPLETE CIIU — Búsqueda de actividades económicas
// CIIU Rev. 4 A.C. (Colombia)
// ============================================================

import { useCallback, useEffect, useRef, useState } from "react";
import { Search, X } from "lucide-react";
import { buscarCIIU } from "../../api/empresaSstApi";

const DEBOUNCE_MS = 300;
const MAX_RESULTADOS = 20;

export default function AutocompleteCIIU({ value = "", onChange, placeholder = "Ej: Actividades hospitalarias" }) {
  const [query, setQuery] = useState("");
  const [opciones, setOpciones] = useState([]);
  const [abierto, setAbierto] = useState(false);
  const [indiceActivo, setIndiceActivo] = useState(-1);
  const [cargando, setCargando] = useState(false);

  const wrapperRef = useRef(null);
  const inputRef = useRef(null);
  const debounceRef = useRef(null);
  const ignorarClickRef = useRef(false);

  const valorFormato = value || "";

  useEffect(() => {
    function handleClickOutside(e) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setAbierto(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const buscar = useCallback(async (termino) => {
    if (!termino || termino.trim().length < 1) {
      setOpciones([]);
      setAbierto(false);
      return;
    }
    try {
      setCargando(true);
      const resultados = await buscarCIIU(termino);
      setOpciones(resultados.slice(0, MAX_RESULTADOS));
      setAbierto(true);
      setIndiceActivo(-1);
    } catch {
      setOpciones([]);
    } finally {
      setCargando(false);
    }
  }, []);

  const handleChange = (e) => {
    const valor = e.target.value;
    setQuery(valor);

    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => buscar(valor), DEBOUNCE_MS);
  };

  const seleccionar = (item) => {
    ignorarClickRef.current = true;
    const texto = `${item.codigo} - ${item.descripcion}`;
    onChange(texto);
    setQuery("");
    setOpciones([]);
    setAbierto(false);
    setIndiceActivo(-1);
    setTimeout(() => { ignorarClickRef.current = false; }, 0);
  };

  const limpiar = () => {
    onChange("");
    setQuery("");
    setOpciones([]);
    setAbierto(false);
  };

  const handleKeyDown = (e) => {
    if (!abierto || opciones.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setIndiceActivo((prev) => (prev < opciones.length - 1 ? prev + 1 : 0));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setIndiceActivo((prev) => (prev > 0 ? prev - 1 : opciones.length - 1));
    } else if (e.key === "Enter" && indiceActivo >= 0) {
      e.preventDefault();
      seleccionar(opciones[indiceActivo]);
    } else if (e.key === "Escape") {
      setAbierto(false);
    }
  };

  return (
    <div className="ciiu-autocomplete-wrapper" ref={wrapperRef}>
      <div className="ciiu-autocomplete-input-wrap">
        <Search size={16} className="ciiu-autocomplete-icon" />
        <input
          ref={inputRef}
          type="text"
          className="ciiu-autocomplete-input"
          value={query}
          onChange={handleChange}
          onFocus={() => { if (opciones.length > 0) setAbierto(true); }}
          onKeyDown={handleKeyDown}
          placeholder={valorFormato || placeholder}
          autoComplete="off"
        />
        {valorFormato && (
          <button type="button" className="ciiu-autocomplete-clear" onClick={limpiar} title="Limpiar">
            <X size={14} />
          </button>
        )}
      </div>

      {valorFormato && (
        <div className="ciiu-autocomplete-selected">
          <span className="ciiu-autocomplete-selected-text">{valorFormato}</span>
        </div>
      )}

      {abierto && opciones.length > 0 && (
        <ul className="ciiu-autocomplete-dropdown">
          {cargando && <li className="ciiu-autocomplete-loading">Buscando...</li>}
          {!cargando && opciones.map((item, idx) => (
            <li
              key={item.codigo}
              className={`ciiu-autocomplete-option ${idx === indiceActivo ? "active" : ""}`}
              onMouseDown={(e) => { e.preventDefault(); seleccionar(item); }}
              onMouseEnter={() => setIndiceActivo(idx)}
            >
              <span className="ciiu-autocomplete-codigo">{item.codigo}</span>
              <span className="ciiu-autocomplete-desc">{item.descripcion}</span>
            </li>
          ))}
        </ul>
      )}

      {abierto && !cargando && query.length >= 1 && opciones.length === 0 && (
        <div className="ciiu-autocomplete-dropdown">
          <div className="ciiu-autocomplete-empty">No se encontraron resultados</div>
        </div>
      )}
    </div>
  );
}

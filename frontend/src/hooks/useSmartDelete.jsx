// ============================================================
// HOOK GLOBAL - ELIMINACIÓN INTELIGENTE ENTERPRISE
// ERP SST PRO ENTERPRISE
// FASE 37.2 — Framework Global de Eliminación Inteligente
// Archivo: frontend/src/hooks/useSmartDelete.jsx
// ============================================================

import { useCallback, useMemo, useState } from "react";
import { toastError } from "../utils/toast";

import EliminacionInteligenteModal from "../components/common/EliminacionInteligenteModal";
import {
  ejecutarEliminacionInteligente,
  inactivarRegistroInteligente,
  validarEliminacionInteligente,
} from "../api/smartDeleteApi";
import { getSmartDeleteConfig } from "../config/smartDeleteEntities";

const obtenerMensajeError = (error) => {
  return (
    error?.response?.data?.detail ||
    error?.response?.data?.message ||
    error?.message ||
    "No fue posible ejecutar la eliminación inteligente."
  );
};

/**
 * Hook reutilizable para eliminación inteligente.
 *
 * Uso recomendado:
 *
 * const smartDelete = useSmartDelete({
 *   entidad: "area",
 *   etiquetaEntidad: "área",
 *   getNombre: (area) => area.nombre,
 *   onSuccess: cargarAreas,
 * });
 *
 * <button onClick={() => smartDelete.open(area)}>Eliminar</button>
 * {smartDelete.modal}
 */
export default function useSmartDelete({
  entidad,
  etiquetaEntidad,
  idField,
  getNombre,
  onSuccess,
  onError,
  onBeforeOpen,
  onAfterClose,
} = {}) {
  const config = useMemo(() => getSmartDeleteConfig(entidad) || {}, [entidad]);

  const entidadApi = entidad || config.entidad;
  const etiqueta = etiquetaEntidad || config.etiqueta || "registro";
  const campoId = idField || config.idField || "id";
  const resolverNombre = getNombre || config.getNombre || ((item) => item?.nombre || "Registro seleccionado");

  const [abierto, setAbierto] = useState(false);
  const [registro, setRegistro] = useState(null);
  const [validacion, setValidacion] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [ejecutando, setEjecutando] = useState(false);
  const [error, setError] = useState(null);

  const cerrar = useCallback(() => {
    if (ejecutando) return;
    setAbierto(false);
    setRegistro(null);
    setValidacion(null);
    setError(null);
    if (typeof onAfterClose === "function") onAfterClose();
  }, [ejecutando, onAfterClose]);

  const open = useCallback(
    async (item) => {
      try {
        setError(null);
        setCargando(true);

        if (!entidadApi) {
          throw new Error("Entidad no configurada para eliminación inteligente.");
        }

        const registroId = item?.[campoId];
        if (!registroId) {
          throw new Error("El registro seleccionado no tiene ID válido.");
        }

        if (typeof onBeforeOpen === "function") {
          await onBeforeOpen(item);
        }

        const resultado = await validarEliminacionInteligente(entidadApi, registroId);
        setRegistro(item);
        setValidacion(resultado);
        setAbierto(true);
      } catch (err) {
        const mensaje = obtenerMensajeError(err);
        setError(mensaje);
        if (typeof onError === "function") onError(mensaje, err);
        else toastError("Error", mensaje);
      } finally {
        setCargando(false);
      }
    },
    [campoId, entidadApi, onBeforeOpen, onError]
  );

  const eliminar = useCallback(async () => {
    if (!registro) return;

    try {
      setEjecutando(true);
      const registroId = registro?.[campoId];
      await ejecutarEliminacionInteligente(entidadApi, registroId, "DELETE", true);
      cerrar();
      if (typeof onSuccess === "function") await onSuccess({ modo: "DELETE", registro });
    } catch (err) {
      const mensaje = obtenerMensajeError(err);
      setError(mensaje);
      if (typeof onError === "function") onError(mensaje, err);
      else toastError("Error", mensaje);
    } finally {
      setEjecutando(false);
    }
  }, [campoId, cerrar, entidadApi, onError, onSuccess, registro]);

  const inactivar = useCallback(async () => {
    if (!registro) return;

    try {
      setEjecutando(true);
      const registroId = registro?.[campoId];
      await inactivarRegistroInteligente(entidadApi, registroId);
      cerrar();
      if (typeof onSuccess === "function") await onSuccess({ modo: "INACTIVATE", registro });
    } catch (err) {
      const mensaje = obtenerMensajeError(err);
      setError(mensaje);
      if (typeof onError === "function") onError(mensaje, err);
      else toastError("Error", mensaje);
    } finally {
      setEjecutando(false);
    }
  }, [campoId, cerrar, entidadApi, onError, onSuccess, registro]);

  const registroNombre = useMemo(() => {
    if (!registro) return "Registro seleccionado";
    try {
      return resolverNombre(registro) || "Registro seleccionado";
    } catch {
      return registro?.nombre || "Registro seleccionado";
    }
  }, [registro, resolverNombre]);

  const modal = (
    <EliminacionInteligenteModal
      abierto={abierto}
      entidad={etiqueta}
      registroNombre={registroNombre}
      validacion={validacion}
      ejecutando={ejecutando}
      onCancelar={cerrar}
      onEliminar={eliminar}
      onInactivar={inactivar}
    />
  );

  return {
    abierto,
    registro,
    validacion,
    cargando,
    ejecutando,
    error,
    open,
    cerrar,
    eliminar,
    inactivar,
    modal,
  };
}

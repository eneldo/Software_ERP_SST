// ============================================================
// LOGIN PAGE - ERP SST PRO ENTERPRISE
// FASE HARDENING — Login real sin credenciales demo
// Archivo: frontend/src/pages/auth/LoginPage.jsx
// ============================================================

import React, { useMemo, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import {
  getCurrentUser,
  isAuthenticated,
  login,
} from "../../services/authService";
import {
  resolverDestinoIngreso,
  rutaInicialPorRol,
} from "../../constants/roles";
import "../../styles/login-enterprise.css";

function getErrorMessage(error) {
  const detail = error?.response?.data?.detail;

  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item) => item?.msg || item?.message || "Dato inválido")
      .join(". ");
  }

  if (error?.response?.status === 0 || error?.code === "ERR_NETWORK") {
    return "No se pudo conectar con el backend FastAPI.";
  }

  return "No fue posible iniciar sesión. Verifica tus credenciales.";
}

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const [form, setForm] = useState({ correo: "", password: "" });
  const [mostrarPassword, setMostrarPassword] = useState(false);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  const destinoSolicitado = useMemo(() => {
    return location.state?.from?.pathname || null;
  }, [location.state]);

  if (isAuthenticated()) {
    return <Navigate to={rutaInicialPorRol(getCurrentUser())} replace />;
  }

  const actualizarCampo = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const enviarLogin = async (event) => {
    event.preventDefault();
    setError("");

    const correo = form.correo.trim().toLowerCase();
    const password = form.password;

    if (!correo || !password) {
      setError("Digite el correo y la contraseña para continuar.");
      return;
    }

    try {
      setCargando(true);
      const sesion = await login({ correo, password });
      const destino = resolverDestinoIngreso(sesion?.usuario, destinoSolicitado);
      navigate(destino, { replace: true });
    } catch (err) {
      console.error("Error de autenticación", err);
      setError(getErrorMessage(err));
    } finally {
      setCargando(false);
    }
  };

  return (
    <main className="login-enterprise-shell">
      <section className="login-enterprise-card" aria-label="Inicio de sesión ERP SST">
        <div className="login-brand-mark">SST</div>

        <span className="login-eyebrow">ERP SST PRO Enterprise</span>

        <h1>Seguridad y Salud en el Trabajo</h1>

        <p>
          Acceso seguro al dashboard ejecutivo SST, auditorías, indicadores,
          documentación y validación documental empresarial.
        </p>

        <form className="login-enterprise-form" onSubmit={enviarLogin} noValidate>
          <label htmlFor="correo">Correo electrónico</label>
          <input
            id="correo"
            name="correo"
            type="email"
            autoComplete="username"
            placeholder="usuario@empresa.com"
            value={form.correo}
            onChange={actualizarCampo}
            disabled={cargando}
          />

          <label htmlFor="password">Contraseña</label>
          <div className="login-password-group">
            <input
              id="password"
              name="password"
              type={mostrarPassword ? "text" : "password"}
              autoComplete="current-password"
              placeholder="Digite su contraseña"
              value={form.password}
              onChange={actualizarCampo}
              disabled={cargando}
            />
            <button
              type="button"
              className="login-password-toggle"
              onClick={() => setMostrarPassword((prev) => !prev)}
              disabled={cargando}
            >
              {mostrarPassword ? "Ocultar" : "Ver"}
            </button>
          </div>

          {error && <div className="login-error" role="alert">{error}</div>}

          <button className="login-submit" type="submit" disabled={cargando}>
            {cargando ? "Validando acceso..." : "Ingresar al sistema"}
          </button>
        </form>

        <small className="login-security-note">
          Acceso restringido. Todos los intentos de inicio de sesión pueden ser auditados.
        </small>
      </section>
    </main>
  );
}

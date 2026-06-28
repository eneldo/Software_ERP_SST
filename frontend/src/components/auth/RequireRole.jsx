// ============================================================
// COMPONENTE: REQUIRE ROLE
// ERP SST PRO ENTERPRISE
// FASE HARDENING — Control visual de acceso por rol
// Archivo: frontend/src/components/auth/RequireRole.jsx
// ============================================================

import React from "react";
import { Navigate } from "react-router-dom";

function getStoredUser() {
  try {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  } catch (error) {
    return null;
  }
}

export default function RequireRole({ allowedRoles = [], children }) {
  const token = localStorage.getItem("access_token");
  const user = getStoredUser();
  const userRole = String(user?.rol || "").toUpperCase();
  const roles = allowedRoles.map((role) => String(role).toUpperCase());

  if (!token) {
    return <Navigate to="/" replace />;
  }

  if (!roles.includes(userRole)) {
    return <Navigate to="/admin/dashboard" replace />;
  }

  return children;
}

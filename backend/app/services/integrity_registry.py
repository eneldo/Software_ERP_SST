# ============================================================
# INTEGRITY REGISTRY ENTERPRISE - ERP SST PRO ENTERPRISE
# FASE 37.4 — Enterprise Core Framework
# Archivo: backend/app/services/integrity_registry.py
# ============================================================

from __future__ import annotations

from copy import deepcopy
from typing import Any

# -----------------------------------------------------------------------------
# Este archivo centraliza metadatos visuales y políticas del Framework de
# Integridad. No reemplaza el motor relation_guard.py; lo complementa para que
# nuevas entidades puedan integrarse con una configuración homogénea.
# -----------------------------------------------------------------------------

DEFAULT_DELETE_POLICY: dict[str, Any] = {
    "allow_physical_delete": True,
    "allow_inactivate": True,
    "prefer_trash": False,
    "trash_retention_days": 30,
    "requires_audit": True,
    "requires_confirmation": True,
    "legal_hold": False,
}

ENTITY_METADATA_REGISTRY: dict[str, dict[str, Any]] = {
    "empresa": {
        "label": "Empresa",
        "plural_label": "Empresas",
        "module": "Organización",
        "domain": "core",
        "icon": "building-2",
        "emoji": "🏢",
        "color": "blue",
        "severity": "LEGAL",
        "order": 10,
        "description": "Entidad raíz de la estructura empresarial del SG-SST.",
        "delete_policy": {"allow_physical_delete": False, "trash_retention_days": 90},
    },
    "sede": {
        "label": "Sede",
        "plural_label": "Sedes",
        "module": "Organización",
        "domain": "core",
        "icon": "map-pin",
        "emoji": "📍",
        "color": "indigo",
        "severity": "HIGH",
        "order": 20,
        "description": "Ubicación física o administrativa donde opera la empresa.",
        "delete_policy": {"allow_physical_delete": True, "trash_retention_days": 60},
    },
    "area": {
        "label": "Área",
        "plural_label": "Áreas",
        "module": "Organización",
        "domain": "core",
        "icon": "network",
        "emoji": "🧩",
        "color": "cyan",
        "severity": "HIGH",
        "order": 30,
        "description": "Área funcional relacionada con procesos, cargos y empleados.",
        "delete_policy": {"allow_physical_delete": True, "trash_retention_days": 60},
    },
    "cargo": {
        "label": "Cargo",
        "plural_label": "Cargos",
        "module": "Organización",
        "domain": "core",
        "icon": "briefcase",
        "emoji": "💼",
        "color": "violet",
        "severity": "HIGH",
        "order": 40,
        "description": "Cargo laboral asociado a empleados, riesgos, EPP y exámenes.",
        "delete_policy": {"allow_physical_delete": True, "trash_retention_days": 60},
    },
    "empleado": {
        "label": "Empleado",
        "plural_label": "Empleados",
        "module": "Organización",
        "domain": "people",
        "icon": "users",
        "emoji": "👤",
        "color": "emerald",
        "severity": "CRITICAL",
        "order": 50,
        "description": "Trabajador con trazabilidad médica, EPP, incidentes, firmas y reportes.",
        "delete_policy": {"allow_physical_delete": False, "trash_retention_days": 180},
    },
    "examen_medico": {
        "label": "Examen Médico",
        "plural_label": "Exámenes Médicos",
        "module": "Hacer",
        "domain": "medical",
        "icon": "stethoscope",
        "emoji": "🩺",
        "color": "sky",
        "severity": "LEGAL",
        "order": 110,
        "description": "Registro médico ocupacional con evidencia y trazabilidad legal.",
        "delete_policy": {"allow_physical_delete": True, "trash_retention_days": 180, "legal_hold": True},
    },
    "epp": {
        "label": "EPP",
        "plural_label": "EPP",
        "module": "Hacer",
        "domain": "operational",
        "icon": "hard-hat",
        "emoji": "🦺",
        "color": "amber",
        "severity": "HIGH",
        "order": 120,
        "description": "Elementos de protección personal y entregas asociadas.",
        "delete_policy": {"allow_physical_delete": True, "trash_retention_days": 90},
    },
    "inspeccion": {
        "label": "Inspección",
        "plural_label": "Inspecciones",
        "module": "Hacer",
        "domain": "operational",
        "icon": "search-check",
        "emoji": "🔎",
        "color": "orange",
        "severity": "HIGH",
        "order": 130,
        "description": "Inspección SST con hallazgos, evidencias y seguimientos.",
        "delete_policy": {"allow_physical_delete": False, "trash_retention_days": 180},
    },
    "capa": {
        "label": "CAPA",
        "plural_label": "CAPA",
        "module": "Actuar",
        "domain": "corrective_actions",
        "icon": "wrench",
        "emoji": "🛠️",
        "color": "red",
        "severity": "CRITICAL",
        "order": 140,
        "description": "Acciones correctivas, preventivas y de mejora con seguimiento.",
        "delete_policy": {"allow_physical_delete": False, "trash_retention_days": 180},
    },
    "incidente": {
        "label": "Incidente",
        "plural_label": "Incidentes",
        "module": "Hacer",
        "domain": "incident_management",
        "icon": "siren",
        "emoji": "🚑",
        "color": "rose",
        "severity": "LEGAL",
        "order": 150,
        "description": "Incidentes y accidentes con lesionados, testigos, investigación y CAPA.",
        "delete_policy": {"allow_physical_delete": False, "trash_retention_days": 365, "legal_hold": True},
    },
}

SEVERITY_SCALE: dict[str, dict[str, Any]] = {
    "LOW": {"label": "Bajo", "score": 1, "color": "green"},
    "MEDIUM": {"label": "Medio", "score": 2, "color": "yellow"},
    "HIGH": {"label": "Alto", "score": 3, "color": "orange"},
    "CRITICAL": {"label": "Crítico", "score": 4, "color": "red"},
    "LEGAL": {"label": "Legal", "score": 5, "color": "purple"},
    "AUDIT": {"label": "Auditoría", "score": 5, "color": "slate"},
}


def _merge_policy(policy: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_DELETE_POLICY)
    merged.update(policy or {})
    return merged


def get_entity_metadata(entity: str) -> dict[str, Any] | None:
    key = (entity or "").strip().lower()
    metadata = ENTITY_METADATA_REGISTRY.get(key)
    if not metadata:
        return None

    result = deepcopy(metadata)
    result["entity"] = key
    result["delete_policy"] = _merge_policy(result.get("delete_policy"))
    severity_key = str(result.get("severity") or "MEDIUM").upper()
    result["severity_meta"] = SEVERITY_SCALE.get(severity_key, SEVERITY_SCALE["MEDIUM"])
    return result


def get_all_entity_metadata() -> list[dict[str, Any]]:
    return sorted(
        [get_entity_metadata(entity) for entity in ENTITY_METADATA_REGISTRY.keys()],
        key=lambda item: int(item.get("order") or 999),
    )


def get_framework_metadata() -> dict[str, Any]:
    entities = get_all_entity_metadata()
    return {
        "name": "ERP SST PRO Enterprise Core Framework",
        "version": "37.4",
        "description": "Metadata central para Smart Delete, Smart Impact, Papelera futura, Auditoría e Integridad.",
        "features": {
            "smart_delete": True,
            "smart_impact": True,
            "smart_trash_ready": True,
            "smart_restore_ready": True,
            "smart_audit_ready": True,
            "configurable_policies": True,
        },
        "severity_scale": SEVERITY_SCALE,
        "default_delete_policy": DEFAULT_DELETE_POLICY,
        "entities_count": len(entities),
        "entities": entities,
    }

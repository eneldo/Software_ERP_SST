# ============================================================
# RELATION GUARD SERVICE - ERP SST PRO ENTERPRISE
# FASE 37.3 — Smart Delete Enterprise v2
# Archivo: backend/app/services/relation_guard.py
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass(frozen=True)
class RelationRule:
    table: str
    column: str
    label: str
    blocking: bool = True
    message_template: str | None = None

    # FASE 37.3 — metadatos visuales y filtros controlados.
    category: str = "general"
    icon: str = "database"
    severity: str = "MEDIUM"
    extra_where: str | None = None
    extra_params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EntityGuardConfig:
    entity: str
    table: str
    label: str
    primary_key: str = "id"
    inactive_column: str | None = "activo"
    rules: tuple[RelationRule, ...] = field(default_factory=tuple)


# ============================================================
# REGISTRO CENTRAL DE ENTIDADES PROTEGIDAS
# Para agregar un módulo nuevo:
# 1. Registrar la entidad.
# 2. Definir tabla, PK, columna de inactivación.
# 3. Agregar RelationRule por cada dependencia real.
# ============================================================
ENTITY_GUARD_REGISTRY: dict[str, EntityGuardConfig] = {
    "empresa": EntityGuardConfig(
        entity="empresa",
        table="empresas",
        label="Empresa",
        inactive_column="estado",
        rules=(
            RelationRule("sedes", "empresa_id", "Sedes", category="organizacion", icon="building", severity="HIGH"),
            RelationRule("areas", "empresa_id", "Áreas", category="organizacion", icon="network", severity="HIGH"),
            RelationRule("cargos", "empresa_id", "Cargos", category="organizacion", icon="briefcase", severity="HIGH"),
            RelationRule("empleados", "empresa_id", "Empleados", category="organizacion", icon="users", severity="CRITICAL"),
            RelationRule("usuarios", "empresa_id", "Usuarios", category="seguridad", icon="shield", severity="HIGH"),
            RelationRule("politicas_sst", "empresa_id", "Políticas SST", category="planear", icon="file-text", severity="MEDIUM"),
            RelationRule("objetivos_sst", "empresa_id", "Objetivos SST", category="planear", icon="target", severity="MEDIUM"),
            RelationRule("evaluaciones_iniciales_sst", "empresa_id", "Evaluaciones Iniciales SST", category="planear", icon="clipboard", severity="MEDIUM"),
            RelationRule("matriz_legal_sst", "empresa_id", "Matriz Legal SST", category="planear", icon="scale", severity="MEDIUM"),
            RelationRule("matriz_peligros_sst", "empresa_id", "Matriz de Peligros SST", category="planear", icon="alert-triangle", severity="HIGH"),
            RelationRule("plan_anual_sst", "empresa_id", "Plan Anual SST", category="planear", icon="calendar", severity="MEDIUM"),
            RelationRule("inspecciones_sst", "empresa_id", "Inspecciones SST", category="hacer", icon="search", severity="HIGH"),
            RelationRule("capas_sst", "empresa_id", "CAPA SST", category="actuar", icon="wrench", severity="HIGH"),
            RelationRule("incidentes_accidentes_sst", "empresa_id", "Incidentes / Accidentes SST", category="hacer", icon="siren", severity="CRITICAL"),
            RelationRule("biblioteca_documental", "empresa_id", "Biblioteca Documental", category="documental", icon="folder", severity="MEDIUM"),
        ),
    ),
    "sede": EntityGuardConfig(
        entity="sede",
        table="sedes",
        label="Sede",
        rules=(
            RelationRule("empleados", "sede_id", "Empleados", category="organizacion", icon="users", severity="CRITICAL"),
            RelationRule("usuarios", "sede_id", "Usuarios", category="seguridad", icon="shield", severity="HIGH"),
            RelationRule("evaluaciones_iniciales_sst", "sede_id", "Evaluaciones Iniciales SST", category="planear", icon="clipboard", severity="MEDIUM"),
            RelationRule("matriz_legal_sst", "sede_id", "Matriz Legal SST", category="planear", icon="scale", severity="MEDIUM"),
            RelationRule("matriz_peligros_sst", "sede_id", "Matriz de Peligros SST", category="planear", icon="alert-triangle", severity="HIGH"),
            RelationRule("plan_anual_sst", "sede_id", "Plan Anual SST", category="planear", icon="calendar", severity="MEDIUM"),
            # Estas tablas pueden no tener sede_id en todas las versiones. El motor valida existencia antes de contar.
            RelationRule("examenes_medicos", "sede_id", "Exámenes Médicos", category="hacer", icon="stethoscope", severity="MEDIUM"),
            RelationRule("epp_entregas", "sede_id", "Entregas de EPP", category="hacer", icon="hard-hat", severity="MEDIUM"),
            RelationRule("inspecciones_sst", "sede_id", "Inspecciones SST", category="hacer", icon="search", severity="HIGH"),
            RelationRule("capas_sst", "sede_id", "CAPA SST", category="actuar", icon="wrench", severity="HIGH"),
            RelationRule("incidentes_accidentes_sst", "sede_id", "Incidentes / Accidentes SST", category="hacer", icon="siren", severity="CRITICAL"),
            RelationRule("reportes_inseguridad_sst", "sede_id", "Reportes de Inseguridad SST", category="hacer", icon="megaphone", severity="MEDIUM"),
            RelationRule("biblioteca_documental", "sede_id", "Biblioteca Documental", category="documental", icon="folder", severity="MEDIUM"),
        ),
    ),
    "area": EntityGuardConfig(
        entity="area",
        table="areas",
        label="Área",
        rules=(
            RelationRule("empleados", "area_id", "Empleados", category="organizacion", icon="users", severity="CRITICAL"),
            RelationRule("cargos", "area_id", "Cargos", category="organizacion", icon="briefcase", severity="HIGH"),
            RelationRule("examenes_medicos", "area_id", "Exámenes Médicos", category="hacer", icon="stethoscope", severity="MEDIUM"),
            RelationRule("epp_entregas", "area_id", "Entregas de EPP", category="hacer", icon="hard-hat", severity="MEDIUM"),
            RelationRule("inspecciones_sst", "area_id", "Inspecciones SST", category="hacer", icon="search", severity="HIGH"),
            RelationRule("inspecciones_hallazgos_sst", "area_id", "Hallazgos de Inspecciones", category="verificar", icon="alert-circle", severity="HIGH"),
            RelationRule("capas_sst", "area_id", "CAPA SST", category="actuar", icon="wrench", severity="HIGH"),
            RelationRule("incidentes_accidentes_sst", "area_id", "Incidentes / Accidentes SST", category="hacer", icon="siren", severity="CRITICAL"),
            RelationRule("reportes_inseguridad_sst", "area_id", "Reportes de Inseguridad SST", category="hacer", icon="megaphone", severity="MEDIUM"),
        ),
    ),
    "cargo": EntityGuardConfig(
        entity="cargo",
        table="cargos",
        label="Cargo",
        rules=(
            RelationRule("empleados", "cargo_id", "Empleados", category="organizacion", icon="users", severity="CRITICAL"),
            RelationRule("examenes_medicos", "cargo_id", "Exámenes Médicos", category="hacer", icon="stethoscope", severity="MEDIUM"),
            RelationRule("epp_entregas", "cargo_id", "Entregas de EPP", category="hacer", icon="hard-hat", severity="MEDIUM"),
            RelationRule("capacitaciones_sst_asistentes", "cargo_id", "Asistentes de Capacitaciones", category="hacer", icon="graduation-cap", severity="MEDIUM"),
        ),
    ),
    "empleado": EntityGuardConfig(
        entity="empleado",
        table="empleados",
        label="Empleado",
        rules=(
            RelationRule("examenes_medicos", "empleado_id", "Exámenes Médicos", category="hacer", icon="stethoscope", severity="HIGH"),
            RelationRule("epp_entregas", "empleado_id", "Entregas de EPP", category="hacer", icon="hard-hat", severity="MEDIUM"),
            RelationRule("capacitaciones_sst_asistentes", "empleado_id", "Asistencias a Capacitaciones", category="hacer", icon="graduation-cap", severity="MEDIUM"),
            RelationRule("incidentes_lesionados_sst", "empleado_id", "Lesiones en Incidentes", category="hacer", icon="siren", severity="CRITICAL"),
            RelationRule("incidentes_testigos_sst", "empleado_id", "Testigos en Incidentes", category="hacer", icon="eye", severity="HIGH"),
            RelationRule("firmas_digitales_sst", "empleado_id", "Firmas Digitales SST", category="documental", icon="pen-tool", severity="MEDIUM"),
            RelationRule("reportes_inseguridad_sst", "empleado_id", "Reportes de Inseguridad SST", category="hacer", icon="megaphone", severity="MEDIUM"),
        ),
    ),
    "examen_medico": EntityGuardConfig(
        entity="examen_medico",
        table="examenes_medicos",
        label="Examen Médico",
        inactive_column="activo",
        rules=(
            # FASE 37.3 — evidencia específica del examen médico.
            # Cuenta solo archivos del módulo EXAMENES_MEDICOS asociados por referencia_id.
            RelationRule(
                "archivos_sst",
                "referencia_id",
                "Evidencias Médicas",
                blocking=True,
                category="evidencias",
                icon="paperclip",
                severity="HIGH",
                extra_where='AND "modulo" = :modulo_examen AND COALESCE("activo", TRUE) = TRUE',
                extra_params={"modulo_examen": "EXAMENES_MEDICOS"},
                message_template="El examen médico tiene {count} evidencia(s) médica(s) asociada(s).",
            ),
        ),
    ),
}


# ============================================================
# UTILIDADES SQL SEGURAS
# ============================================================
def _normalize_identifier(value: str) -> str:
    if not value or not value.replace("_", "").isalnum():
        raise ValueError(f"Identificador SQL inválido: {value!r}")
    return value


def table_exists(db: Session, table_name: str) -> bool:
    table_name = _normalize_identifier(table_name)
    sql = text("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = :table_name
        )
    """)
    return bool(db.execute(sql, {"table_name": table_name}).scalar())


def column_exists(db: Session, table_name: str, column_name: str) -> bool:
    table_name = _normalize_identifier(table_name)
    column_name = _normalize_identifier(column_name)
    sql = text("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = :table_name
              AND column_name = :column_name
        )
    """)
    return bool(db.execute(sql, {"table_name": table_name, "column_name": column_name}).scalar())


def record_exists(db: Session, *, table_name: str, primary_key: str, record_id: int) -> bool:
    table_name = _normalize_identifier(table_name)
    primary_key = _normalize_identifier(primary_key)

    if not table_exists(db, table_name) or not column_exists(db, table_name, primary_key):
        return False

    sql = text(f'SELECT EXISTS (SELECT 1 FROM "{table_name}" WHERE "{primary_key}" = :record_id)')
    return bool(db.execute(sql, {"record_id": record_id}).scalar())


def count_related_records(db: Session, *, rule: RelationRule, record_id: int) -> int:
    table_name = _normalize_identifier(rule.table)
    column_name = _normalize_identifier(rule.column)

    if not table_exists(db, table_name) or not column_exists(db, table_name, column_name):
        return 0

    params: dict[str, Any] = {"record_id": record_id, **dict(rule.extra_params or {})}
    extra_where = f" {rule.extra_where.strip()}" if rule.extra_where else ""
    sql = text(f'SELECT COUNT(*) FROM "{table_name}" WHERE "{column_name}" = :record_id{extra_where}')
    return int(db.execute(sql, params).scalar() or 0)


def get_registered_entities() -> list[dict[str, Any]]:
    return [
        {
            "entity": config.entity,
            "table": config.table,
            "label": config.label,
            "primary_key": config.primary_key,
            "rules_count": len(config.rules),
        }
        for config in ENTITY_GUARD_REGISTRY.values()
    ]


def get_entity_config(entity: str) -> EntityGuardConfig | None:
    return ENTITY_GUARD_REGISTRY.get((entity or "").strip().lower())


def _rule_message(config: EntityGuardConfig, rule: RelationRule, count: int) -> str:
    if rule.message_template:
        return rule.message_template.format(count=count, entity=config.label.lower(), label=rule.label)
    return (
        f"No se puede eliminar {config.label.lower()} porque tiene "
        f"{count} registro(s) relacionado(s) en {rule.label}."
    )


def _impact_level(total_records: int, blocking_records: int, blocking_rules: int) -> tuple[str, str]:
    if blocking_records >= 20 or blocking_rules >= 5:
        return "CRITICAL", "Crítico"
    if blocking_records >= 5 or blocking_rules >= 3:
        return "HIGH", "Alto"
    if blocking_records >= 1:
        return "MEDIUM", "Medio"
    if total_records >= 1:
        return "LOW", "Bajo"
    return "LOW", "Bajo"


def _build_impact_summary(matrix: list[dict[str, Any]], can_delete: bool) -> dict[str, Any]:
    total_related_records = sum(int(item.get("count") or 0) for item in matrix)
    total_blocking_records = sum(
        int(item.get("count") or 0)
        for item in matrix
        if item.get("blocking") and int(item.get("count") or 0) > 0
    )
    blocking_rules = sum(
        1
        for item in matrix
        if item.get("blocking") and int(item.get("count") or 0) > 0
    )
    non_blocking_rules = sum(
        1
        for item in matrix
        if not item.get("blocking") and int(item.get("count") or 0) > 0
    )
    level, label = _impact_level(total_related_records, total_blocking_records, blocking_rules)
    return {
        "total_rules": len(matrix),
        "total_related_records": total_related_records,
        "total_blocking_records": total_blocking_records,
        "blocking_rules": blocking_rules,
        "non_blocking_rules": non_blocking_rules,
        "impact_level": level,
        "impact_label": label,
        "recommended_action": "DELETE" if can_delete else "INACTIVATE",
        "can_delete": can_delete,
    }


def validate_delete_dependencies(db: Session, *, entity: str, record_id: int) -> dict[str, Any]:
    config = get_entity_config(entity)

    if not config:
        return {
            "entity": entity,
            "entity_id": record_id,
            "can_delete": False,
            "recommended_action": "REVIEW",
            "total_dependencies": 0,
            "blocking_dependencies": 0,
            "dependencies": [],
            "message": f"La entidad '{entity}' no está registrada en el motor de validación.",
            "meta": {"registered_entities": sorted(ENTITY_GUARD_REGISTRY.keys())},
            "impact_summary": _build_impact_summary([], False),
            "impact_matrix": [],
        }

    if record_id <= 0:
        return {
            "entity": config.entity,
            "entity_id": record_id,
            "can_delete": False,
            "recommended_action": "REVIEW",
            "total_dependencies": 0,
            "blocking_dependencies": 0,
            "dependencies": [],
            "message": "El ID del registro no es válido.",
            "meta": {"table": config.table},
            "impact_summary": _build_impact_summary([], False),
            "impact_matrix": [],
        }

    if not record_exists(db, table_name=config.table, primary_key=config.primary_key, record_id=record_id):
        return {
            "entity": config.entity,
            "entity_id": record_id,
            "can_delete": False,
            "recommended_action": "REVIEW",
            "total_dependencies": 0,
            "blocking_dependencies": 0,
            "dependencies": [],
            "message": f"{config.label} no encontrada.",
            "meta": {"table": config.table},
            "impact_summary": _build_impact_summary([], False),
            "impact_matrix": [],
        }

    dependencies: list[dict[str, Any]] = []
    impact_matrix: list[dict[str, Any]] = []

    for rule in config.rules:
        count = count_related_records(db, rule=rule, record_id=record_id)
        has_records = count > 0
        message = _rule_message(config, rule, count) if has_records else f"Sin registros relacionados en {rule.label}."

        matrix_item = {
            "table": rule.table,
            "column": rule.column,
            "label": rule.label,
            "count": count,
            "blocking": rule.blocking,
            "category": rule.category,
            "severity": rule.severity,
            "icon": rule.icon,
            "message": message,
            "has_records": has_records,
        }
        impact_matrix.append(matrix_item)

        # Compatibilidad: dependencies conserva solo las relaciones con registros.
        if count > 0:
            dependencies.append(matrix_item)

    blocking_count = sum(1 for item in dependencies if item["blocking"])
    can_delete = blocking_count == 0
    impact_summary = _build_impact_summary(impact_matrix, can_delete)

    if can_delete:
        message = f"{config.label} puede eliminarse de forma segura."
        recommended_action = "DELETE"
    else:
        message = (
            f"{config.label} no puede eliminarse porque tiene "
            f"{blocking_count} dependencia(s) bloqueante(s). "
            "Se recomienda inactivar para conservar trazabilidad."
        )
        recommended_action = "INACTIVATE"

    return {
        "entity": config.entity,
        "entity_id": record_id,
        "can_delete": can_delete,
        "recommended_action": recommended_action,
        "total_dependencies": len(dependencies),
        "blocking_dependencies": blocking_count,
        "dependencies": dependencies,
        "message": message,
        "impact_summary": impact_summary,
        "impact_matrix": impact_matrix,
        "meta": {
            "table": config.table,
            "primary_key": config.primary_key,
            "inactive_column": config.inactive_column,
            "impact_summary": impact_summary,
            "impact_matrix": impact_matrix,
        },
    }


# ============================================================
# ELIMINACIÓN INTELIGENTE
# ============================================================
def _sql_identifier(value: str) -> str:
    return _normalize_identifier(value)


def _delete_record(db: Session, *, table_name: str, primary_key: str, record_id: int) -> int:
    table_name = _sql_identifier(table_name)
    primary_key = _sql_identifier(primary_key)
    sql = text(f'DELETE FROM "{table_name}" WHERE "{primary_key}" = :record_id')
    result = db.execute(sql, {"record_id": record_id})
    return int(result.rowcount or 0)


def _inactivate_record(
    db: Session,
    *,
    table_name: str,
    primary_key: str,
    inactive_column: str,
    record_id: int,
) -> int:
    table_name = _sql_identifier(table_name)
    primary_key = _sql_identifier(primary_key)
    inactive_column = _sql_identifier(inactive_column)
    sql = text(
        f'UPDATE "{table_name}" '
        f'SET "{inactive_column}" = FALSE '
        f'WHERE "{primary_key}" = :record_id'
    )
    result = db.execute(sql, {"record_id": record_id})
    return int(result.rowcount or 0)


def _base_execution_payload(
    *,
    entity: str,
    record_id: int,
    action: str,
    message: str,
    success: bool = False,
    can_delete: bool = False,
    was_deleted: bool = False,
    was_inactivated: bool = False,
    recommended_action: str = "REVIEW",
    validation: dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validation = validation or {}
    return {
        "success": success,
        "entity": entity,
        "entity_id": record_id,
        "action": action,
        "can_delete": can_delete,
        "was_deleted": was_deleted,
        "was_inactivated": was_inactivated,
        "message": message,
        "recommended_action": recommended_action,
        "dependencies": validation.get("dependencies", []),
        "impact_summary": validation.get("impact_summary"),
        "impact_matrix": validation.get("impact_matrix", []),
        "meta": {**validation.get("meta", {}), **(meta or {})},
    }


def execute_smart_delete(
    db: Session,
    *,
    entity: str,
    record_id: int,
    mode: str = "AUTO",
    confirmed: bool = False,
) -> dict[str, Any]:
    """
    Ejecuta eliminación inteligente para una entidad registrada.

    Modos:
    - AUTO: elimina físicamente si no hay dependencias; si hay dependencias, inactiva.
    - DELETE: elimina físicamente solo si no hay dependencias bloqueantes.
    - INACTIVATE: inactiva si la entidad tiene columna de estado.
    """
    mode = (mode or "AUTO").strip().upper()
    if mode not in {"AUTO", "DELETE", "INACTIVATE"}:
        return _base_execution_payload(
            entity=entity,
            record_id=record_id,
            action="ERROR",
            message="Modo inválido. Use AUTO, DELETE o INACTIVATE.",
            meta={"mode": mode},
        )

    validation = validate_delete_dependencies(db, entity=entity, record_id=record_id)

    if not confirmed:
        return _base_execution_payload(
            entity=validation.get("entity", entity),
            record_id=record_id,
            action="CONFIRMATION_REQUIRED",
            message="Confirmación requerida antes de ejecutar la eliminación inteligente.",
            can_delete=bool(validation.get("can_delete", False)),
            recommended_action=validation.get("recommended_action", "REVIEW"),
            validation=validation,
            meta={"mode": mode, "use_confirmed_true": True},
        )

    config = get_entity_config(entity)
    if not config:
        return _base_execution_payload(
            entity=entity,
            record_id=record_id,
            action="ERROR",
            message=f"La entidad '{entity}' no está registrada en el motor de eliminación inteligente.",
            validation=validation,
            meta={"registered_entities": sorted(ENTITY_GUARD_REGISTRY.keys())},
        )

    dependencies = validation.get("dependencies", [])
    can_delete = bool(validation.get("can_delete", False))

    if validation.get("message", "").endswith("no encontrada."):
        return _base_execution_payload(
            entity=config.entity,
            record_id=record_id,
            action="NOT_FOUND",
            message=validation.get("message", f"{config.label} no encontrada."),
            validation=validation,
        )

    try:
        if mode == "INACTIVATE":
            if not config.inactive_column or not column_exists(db, config.table, config.inactive_column):
                return _base_execution_payload(
                    entity=config.entity,
                    record_id=record_id,
                    action="BLOCKED",
                    message=f"{config.label} no tiene columna de inactivación configurada.",
                    can_delete=can_delete,
                    recommended_action="REVIEW",
                    validation=validation,
                    meta={"mode": mode},
                )

            affected = _inactivate_record(
                db,
                table_name=config.table,
                primary_key=config.primary_key,
                inactive_column=config.inactive_column,
                record_id=record_id,
            )
            db.commit()
            return _base_execution_payload(
                entity=config.entity,
                record_id=record_id,
                action="INACTIVATE",
                success=affected > 0,
                can_delete=can_delete,
                was_inactivated=affected > 0,
                message=f"{config.label} inactivada correctamente." if affected else f"No se pudo inactivar {config.label.lower()}.",
                recommended_action="INACTIVATE",
                validation=validation,
                meta={"affected_rows": affected, "mode": mode},
            )

        if mode == "DELETE" and not can_delete:
            return _base_execution_payload(
                entity=config.entity,
                record_id=record_id,
                action="BLOCKED",
                message=validation.get("message", f"{config.label} no puede eliminarse."),
                can_delete=False,
                recommended_action="INACTIVATE" if config.inactive_column else "REVIEW",
                validation=validation,
                meta={"mode": mode},
            )

        if mode == "AUTO" and not can_delete:
            if config.inactive_column and column_exists(db, config.table, config.inactive_column):
                affected = _inactivate_record(
                    db,
                    table_name=config.table,
                    primary_key=config.primary_key,
                    inactive_column=config.inactive_column,
                    record_id=record_id,
                )
                db.commit()
                return _base_execution_payload(
                    entity=config.entity,
                    record_id=record_id,
                    action="INACTIVATE",
                    success=affected > 0,
                    can_delete=False,
                    was_inactivated=affected > 0,
                    message=(
                        f"{config.label} tiene dependencias y fue inactivada para conservar trazabilidad."
                        if affected
                        else f"{config.label} tiene dependencias y no pudo inactivarse."
                    ),
                    recommended_action="INACTIVATE",
                    validation=validation,
                    meta={"affected_rows": affected, "mode": mode},
                )

            return _base_execution_payload(
                entity=config.entity,
                record_id=record_id,
                action="BLOCKED",
                message=validation.get("message", f"{config.label} no puede eliminarse."),
                can_delete=False,
                recommended_action="REVIEW",
                validation=validation,
                meta={"mode": mode},
            )

        affected = _delete_record(
            db,
            table_name=config.table,
            primary_key=config.primary_key,
            record_id=record_id,
        )
        db.commit()
        return _base_execution_payload(
            entity=config.entity,
            record_id=record_id,
            action="DELETE",
            success=affected > 0,
            can_delete=True,
            was_deleted=affected > 0,
            message=f"{config.label} eliminada definitivamente de forma segura." if affected else f"No se pudo eliminar {config.label.lower()}.",
            recommended_action="DELETE",
            validation=validation,
            meta={"affected_rows": affected, "mode": mode},
        )
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        return _base_execution_payload(
            entity=config.entity,
            record_id=record_id,
            action="ERROR",
            message="No fue posible ejecutar la eliminación inteligente.",
            can_delete=can_delete,
            recommended_action="REVIEW",
            validation=validation,
            meta={"mode": mode, "error": str(exc)},
        )

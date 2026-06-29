# ============================================================
# RELATION GUARD SERVICE - ERP SST PRO ENTERPRISE
# FASE 37.1.1 — Motor Global de Validación de Relaciones
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


@dataclass(frozen=True)
class EntityGuardConfig:
    entity: str
    table: str
    label: str
    primary_key: str = "id"
    inactive_column: str | None = "activo"
    rules: tuple[RelationRule, ...] = field(default_factory=tuple)


ENTITY_GUARD_REGISTRY: dict[str, EntityGuardConfig] = {
    "empresa": EntityGuardConfig(
        entity="empresa",
        table="empresas",
        label="Empresa",
        inactive_column="estado",
        rules=(
            RelationRule("sedes", "empresa_id", "Sedes"),
            RelationRule("areas", "empresa_id", "Áreas"),
            RelationRule("cargos", "empresa_id", "Cargos"),
            RelationRule("empleados", "empresa_id", "Empleados"),
            RelationRule("usuarios", "empresa_id", "Usuarios"),
            RelationRule("politicas_sst", "empresa_id", "Políticas SST"),
            RelationRule("objetivos_sst", "empresa_id", "Objetivos SST"),
            RelationRule("evaluaciones_iniciales_sst", "empresa_id", "Evaluaciones Iniciales SST"),
            RelationRule("matriz_legal_sst", "empresa_id", "Matriz Legal SST"),
            RelationRule("matriz_peligros_sst", "empresa_id", "Matriz de Peligros SST"),
            RelationRule("plan_anual_sst", "empresa_id", "Plan Anual SST"),
            RelationRule("inspecciones_sst", "empresa_id", "Inspecciones SST"),
            RelationRule("capas_sst", "empresa_id", "CAPA SST"),
            RelationRule("incidentes_accidentes_sst", "empresa_id", "Incidentes / Accidentes SST"),
            RelationRule("biblioteca_documental", "empresa_id", "Biblioteca Documental"),
        ),
    ),
    "sede": EntityGuardConfig(
        entity="sede",
        table="sedes",
        label="Sede",
        rules=(
            RelationRule("empleados", "sede_id", "Empleados"),
            RelationRule("usuarios", "sede_id", "Usuarios"),
            RelationRule("evaluaciones_iniciales_sst", "sede_id", "Evaluaciones Iniciales SST"),
            RelationRule("matriz_legal_sst", "sede_id", "Matriz Legal SST"),
            RelationRule("matriz_peligros_sst", "sede_id", "Matriz de Peligros SST"),
            RelationRule("plan_anual_sst", "sede_id", "Plan Anual SST"),
            RelationRule("examenes_medicos", "sede_id", "Exámenes Médicos"),
            RelationRule("epp_entregas", "sede_id", "Entregas de EPP"),
            RelationRule("inspecciones_sst", "sede_id", "Inspecciones SST"),
            RelationRule("capas_sst", "sede_id", "CAPA SST"),
            RelationRule("incidentes_accidentes_sst", "sede_id", "Incidentes / Accidentes SST"),
            RelationRule("reportes_inseguridad_sst", "sede_id", "Reportes de Inseguridad SST"),
            RelationRule("biblioteca_documental", "sede_id", "Biblioteca Documental"),
        ),
    ),
    "area": EntityGuardConfig(
        entity="area",
        table="areas",
        label="Área",
        rules=(
            RelationRule("empleados", "area_id", "Empleados"),
            RelationRule("cargos", "area_id", "Cargos"),
            RelationRule("examenes_medicos", "area_id", "Exámenes Médicos"),
            RelationRule("epp_entregas", "area_id", "Entregas de EPP"),
            RelationRule("inspecciones_sst", "area_id", "Inspecciones SST"),
            RelationRule("inspecciones_hallazgos_sst", "area_id", "Hallazgos de Inspecciones"),
            RelationRule("capas_sst", "area_id", "CAPA SST"),
            RelationRule("incidentes_accidentes_sst", "area_id", "Incidentes / Accidentes SST"),
            RelationRule("reportes_inseguridad_sst", "area_id", "Reportes de Inseguridad SST"),
        ),
    ),
    "cargo": EntityGuardConfig(
        entity="cargo",
        table="cargos",
        label="Cargo",
        rules=(
            RelationRule("empleados", "cargo_id", "Empleados"),
            RelationRule("examenes_medicos", "cargo_id", "Exámenes Médicos"),
            RelationRule("epp_entregas", "cargo_id", "Entregas de EPP"),
            RelationRule("capacitaciones_sst_asistentes", "cargo_id", "Asistentes de Capacitaciones"),
        ),
    ),
    "empleado": EntityGuardConfig(
        entity="empleado",
        table="empleados",
        label="Empleado",
        rules=(
            RelationRule("examenes_medicos", "empleado_id", "Exámenes Médicos"),
            RelationRule("epp_entregas", "empleado_id", "Entregas de EPP"),
            RelationRule("capacitaciones_sst_asistentes", "empleado_id", "Asistencias a Capacitaciones"),
            RelationRule("incidentes_lesionados_sst", "empleado_id", "Lesiones en Incidentes"),
            RelationRule("incidentes_testigos_sst", "empleado_id", "Testigos en Incidentes"),
            RelationRule("firmas_digitales_sst", "empleado_id", "Firmas Digitales SST"),
            RelationRule("reportes_inseguridad_sst", "empleado_id", "Reportes de Inseguridad SST"),
        ),
    ),
    # ========================================================
    # FASE 37.2.2.B — Exámenes Médicos SST
    # Módulo operativo asociado a empleados.
    #
    # Nota Enterprise:
    # Las evidencias médicas se almacenan en archivos_sst con módulo
    # EXAMENES_MEDICOS y referencia_id genérico. Como el motor actual
    # valida relaciones simples tabla/columna, no se bloquea por
    # archivos_sst para evitar falsos positivos con otros módulos.
    # La gestión de evidencias conserva su flujo propio.
    # ========================================================
    "examen_medico": EntityGuardConfig(
        entity="examen_medico",
        table="examenes_medicos",
        label="Examen Médico",
        inactive_column="activo",
        rules=(),
    ),

}


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


def count_related_records(db: Session, *, table_name: str, column_name: str, record_id: int) -> int:
    table_name = _normalize_identifier(table_name)
    column_name = _normalize_identifier(column_name)

    if not table_exists(db, table_name) or not column_exists(db, table_name, column_name):
        return 0

    sql = text(f'SELECT COUNT(*) FROM "{table_name}" WHERE "{column_name}" = :record_id')
    return int(db.execute(sql, {"record_id": record_id}).scalar() or 0)


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
        }

    dependencies: list[dict[str, Any]] = []

    for rule in config.rules:
        count = count_related_records(
            db,
            table_name=rule.table,
            column_name=rule.column,
            record_id=record_id,
        )

        if count <= 0:
            continue

        message = rule.message_template or (
            f"No se puede eliminar {config.label.lower()} porque tiene "
            f"{count} registro(s) relacionado(s) en {rule.label}."
        )

        dependencies.append(
            {
                "table": rule.table,
                "column": rule.column,
                "label": rule.label,
                "count": count,
                "blocking": rule.blocking,
                "message": message,
            }
        )

    blocking_count = sum(1 for item in dependencies if item["blocking"])
    can_delete = blocking_count == 0

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
        "meta": {
            "table": config.table,
            "primary_key": config.primary_key,
            "inactive_column": config.inactive_column,
        },
    }


# ============================================================
# FASE 37.1.2 — Backend de Eliminación Inteligente
# ============================================================

def _sql_identifier(value: str) -> str:
    """Devuelve un identificador SQL seguro ya validado."""
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

    Nunca elimina físicamente registros con dependencias bloqueantes.
    """
    mode = (mode or "AUTO").strip().upper()
    if mode not in {"AUTO", "DELETE", "INACTIVATE"}:
        return {
            "success": False,
            "entity": entity,
            "entity_id": record_id,
            "action": "ERROR",
            "can_delete": False,
            "was_deleted": False,
            "was_inactivated": False,
            "message": "Modo inválido. Use AUTO, DELETE o INACTIVATE.",
            "recommended_action": "REVIEW",
            "dependencies": [],
            "meta": {"mode": mode},
        }

    if not confirmed:
        validation = validate_delete_dependencies(db, entity=entity, record_id=record_id)
        validation_dependencies = validation.get("dependencies", [])
        return {
            "success": False,
            "entity": validation.get("entity", entity),
            "entity_id": record_id,
            "action": "CONFIRMATION_REQUIRED",
            "can_delete": bool(validation.get("can_delete", False)),
            "was_deleted": False,
            "was_inactivated": False,
            "message": "Confirmación requerida antes de ejecutar la eliminación inteligente.",
            "recommended_action": validation.get("recommended_action", "REVIEW"),
            "dependencies": validation_dependencies,
            "meta": {
                **validation.get("meta", {}),
                "mode": mode,
                "use_confirmed_true": True,
            },
        }

    config = get_entity_config(entity)
    if not config:
        return {
            "success": False,
            "entity": entity,
            "entity_id": record_id,
            "action": "ERROR",
            "can_delete": False,
            "was_deleted": False,
            "was_inactivated": False,
            "message": f"La entidad '{entity}' no está registrada en el motor de eliminación inteligente.",
            "recommended_action": "REVIEW",
            "dependencies": [],
            "meta": {"registered_entities": sorted(ENTITY_GUARD_REGISTRY.keys())},
        }

    validation = validate_delete_dependencies(db, entity=config.entity, record_id=record_id)
    dependencies = validation.get("dependencies", [])
    can_delete = bool(validation.get("can_delete", False))

    if validation.get("message", "").endswith("no encontrada."):
        return {
            "success": False,
            "entity": config.entity,
            "entity_id": record_id,
            "action": "NOT_FOUND",
            "can_delete": False,
            "was_deleted": False,
            "was_inactivated": False,
            "message": validation.get("message", f"{config.label} no encontrada."),
            "recommended_action": "REVIEW",
            "dependencies": dependencies,
            "meta": validation.get("meta", {}),
        }

    try:
        # Modo INACTIVATE siempre intenta inactivar, aunque no tenga dependencias.
        if mode == "INACTIVATE":
            if not config.inactive_column or not column_exists(db, config.table, config.inactive_column):
                return {
                    "success": False,
                    "entity": config.entity,
                    "entity_id": record_id,
                    "action": "BLOCKED",
                    "can_delete": can_delete,
                    "was_deleted": False,
                    "was_inactivated": False,
                    "message": f"{config.label} no tiene columna de inactivación configurada.",
                    "recommended_action": "REVIEW",
                    "dependencies": dependencies,
                    "meta": validation.get("meta", {}),
                }

            affected = _inactivate_record(
                db,
                table_name=config.table,
                primary_key=config.primary_key,
                inactive_column=config.inactive_column,
                record_id=record_id,
            )
            db.commit()
            return {
                "success": affected > 0,
                "entity": config.entity,
                "entity_id": record_id,
                "action": "INACTIVATE",
                "can_delete": can_delete,
                "was_deleted": False,
                "was_inactivated": affected > 0,
                "message": f"{config.label} inactivada correctamente." if affected else f"No se pudo inactivar {config.label.lower()}.",
                "recommended_action": "INACTIVATE",
                "dependencies": dependencies,
                "meta": {**validation.get("meta", {}), "affected_rows": affected, "mode": mode},
            }

        # DELETE solo permite eliminación física si no hay dependencias bloqueantes.
        if mode == "DELETE" and not can_delete:
            return {
                "success": False,
                "entity": config.entity,
                "entity_id": record_id,
                "action": "BLOCKED",
                "can_delete": False,
                "was_deleted": False,
                "was_inactivated": False,
                "message": validation.get("message", f"{config.label} no puede eliminarse."),
                "recommended_action": "INACTIVATE" if config.inactive_column else "REVIEW",
                "dependencies": dependencies,
                "meta": {**validation.get("meta", {}), "mode": mode},
            }

        # AUTO: si hay dependencias, se inactiva.
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
                return {
                    "success": affected > 0,
                    "entity": config.entity,
                    "entity_id": record_id,
                    "action": "INACTIVATE",
                    "can_delete": False,
                    "was_deleted": False,
                    "was_inactivated": affected > 0,
                    "message": (
                        f"{config.label} tiene dependencias y fue inactivada para conservar trazabilidad."
                        if affected
                        else f"{config.label} tiene dependencias y no pudo inactivarse."
                    ),
                    "recommended_action": "INACTIVATE",
                    "dependencies": dependencies,
                    "meta": {**validation.get("meta", {}), "affected_rows": affected, "mode": mode},
                }

            return {
                "success": False,
                "entity": config.entity,
                "entity_id": record_id,
                "action": "BLOCKED",
                "can_delete": False,
                "was_deleted": False,
                "was_inactivated": False,
                "message": validation.get("message", f"{config.label} no puede eliminarse."),
                "recommended_action": "REVIEW",
                "dependencies": dependencies,
                "meta": {**validation.get("meta", {}), "mode": mode},
            }

        # Sin dependencias: eliminación física segura.
        affected = _delete_record(
            db,
            table_name=config.table,
            primary_key=config.primary_key,
            record_id=record_id,
        )
        db.commit()
        return {
            "success": affected > 0,
            "entity": config.entity,
            "entity_id": record_id,
            "action": "DELETE",
            "can_delete": True,
            "was_deleted": affected > 0,
            "was_inactivated": False,
            "message": f"{config.label} eliminada definitivamente de forma segura." if affected else f"No se pudo eliminar {config.label.lower()}.",
            "recommended_action": "DELETE",
            "dependencies": dependencies,
            "meta": {**validation.get("meta", {}), "affected_rows": affected, "mode": mode},
        }
    except Exception as exc:  # noqa: BLE001 - se controla rollback y respuesta segura
        db.rollback()
        return {
            "success": False,
            "entity": config.entity,
            "entity_id": record_id,
            "action": "ERROR",
            "can_delete": can_delete,
            "was_deleted": False,
            "was_inactivated": False,
            "message": "No fue posible ejecutar la eliminación inteligente.",
            "recommended_action": "REVIEW",
            "dependencies": dependencies,
            "meta": {
                **validation.get("meta", {}),
                "mode": mode,
                "error": str(exc),
            },
        }

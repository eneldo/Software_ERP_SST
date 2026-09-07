"""H-027: Índices de performance para queries multi-tenant

Revision ID: d9e0f1a2b3c4
Revises: c8d9e0f1a2b3
Create Date: 2026-09-06
"""

from alembic import op
import sqlalchemy as sa

revision = "d9e0f1a2b3c4"
down_revision = "c8d9e0f1a2b3"
branch_labels = None
depends_on = None


def _add_index_if_missing(table: str, index_name: str, columns: list[str]) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_indexes = {idx["name"] for idx in inspector.get_indexes(table)}
    if index_name not in existing_indexes:
        col_objects = [sa.Column(c) for c in columns]
        op.create_index(index_name, table, columns)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    # Composite indexes: (empresa_id, activo) — highest impact for multi-tenant
    composite_empresa_activo = [
        ("empleados", "ix_empleados_empresa_activo"),
        ("capacitaciones_sst", "ix_capacitaciones_empresa_activo"),
        ("biblioteca_documental", "ix_biblioteca_empresa_activo"),
        ("auditorias_sst", "ix_auditorias_empresa_activo"),
        ("planes_mejoramiento_sst", "ix_pm_empresa_activo"),
        ("planes_anuales_sst", "ix_pa_empresa_activo"),
        ("politicas_sst", "ix_politicas_empresa_activo"),
        ("objetivos_sst", "ix_objetivos_empresa_activo"),
        ("matrices_iper", "ix_iper_empresa_activo"),
        ("matrices_legales_sst", "ix_legal_empresa_activo"),
        ("matrices_peligros_sst", "ix_peligros_empresa_activo"),
        ("evaluaciones_iniciales_sst", "ix_eval_ini_empresa_activo"),
        ("evaluaciones_kirkpatrick_sst", "ix_kirkpatrick_empresa_activo"),
        ("archivos_sst", "ix_archivos_empresa_activo"),
        ("revisiones_direccion_sst", "ix_rev_dir_empresa_activo"),
    ]
    for table, idx_name in composite_empresa_activo:
        if table in tables:
            _add_index_if_missing(table, idx_name, ["empresa_id", "activo"])

    # Index on estado for key workflow tables
    estado_indexes = [
        ("capacitaciones_sst", "ix_capacitaciones_estado"),
        ("auditorias_sst", "ix_auditorias_estado"),
        ("planes_mejoramiento_sst", "ix_pm_estado"),
        ("planes_anuales_sst", "ix_pa_estado"),
        ("politicas_sst", "ix_politicas_estado"),
        ("objetivos_sst", "ix_objetivos_estado"),
        ("matrices_peligros_sst", "ix_peligros_estado"),
        ("evaluaciones_iniciales_sst", "ix_eval_ini_estado"),
        ("biblioteca_documental", "ix_biblioteca_estado"),
    ]
    for table, idx_name in estado_indexes:
        if table in tables:
            _add_index_if_missing(table, idx_name, ["estado"])

    # Index on critical fecha_* columns
    fecha_indexes = [
        ("empleados", "ix_empleados_fecha_ingreso", ["fecha_ingreso"]),
        ("capacitaciones_sst", "ix_capacitaciones_fecha_prog", ["fecha_programada"]),
        ("auditorias_sst", "ix_auditorias_fecha_prog", ["fecha_programada"]),
        ("planes_mejoramiento_sst", "ix_pm_fecha_compromiso", ["fecha_compromiso"]),
        ("matrices_legales_sst", "ix_legal_fecha_venc", ["fecha_vencimiento"]),
        ("matrices_peligros_sst", "ix_peligros_fecha_venc", ["fecha_vencimiento"]),
    ]
    for table, idx_name, cols in fecha_indexes:
        if table in tables:
            _add_index_if_missing(table, idx_name, cols)


def downgrade() -> None:
    indexes_to_drop = [
        ("empleados", "ix_empleados_empresa_activo"),
        ("capacitaciones_sst", "ix_capacitaciones_empresa_activo"),
        ("biblioteca_documental", "ix_biblioteca_empresa_activo"),
        ("auditorias_sst", "ix_auditorias_empresa_activo"),
        ("planes_mejoramiento_sst", "ix_pm_empresa_activo"),
        ("planes_anuales_sst", "ix_pa_empresa_activo"),
        ("politicas_sst", "ix_politicas_empresa_activo"),
        ("objetivos_sst", "ix_objetivos_empresa_activo"),
        ("matrices_iper", "ix_iper_empresa_activo"),
        ("matrices_legales_sst", "ix_legal_empresa_activo"),
        ("matrices_peligros_sst", "ix_peligros_empresa_activo"),
        ("evaluaciones_iniciales_sst", "ix_eval_ini_empresa_activo"),
        ("evaluaciones_kirkpatrick_sst", "ix_kirkpatrick_empresa_activo"),
        ("archivos_sst", "ix_archivos_empresa_activo"),
        ("revisiones_direccion_sst", "ix_rev_dir_empresa_activo"),
        ("capacitaciones_sst", "ix_capacitaciones_estado"),
        ("auditorias_sst", "ix_auditorias_estado"),
        ("planes_mejoramiento_sst", "ix_pm_estado"),
        ("planes_anuales_sst", "ix_pa_estado"),
        ("politicas_sst", "ix_politicas_estado"),
        ("objetivos_sst", "ix_objetivos_estado"),
        ("matrices_peligros_sst", "ix_peligros_estado"),
        ("evaluaciones_iniciales_sst", "ix_eval_ini_estado"),
        ("biblioteca_documental", "ix_biblioteca_estado"),
        ("empleados", "ix_empleados_fecha_ingreso"),
        ("capacitaciones_sst", "ix_capacitaciones_fecha_prog"),
        ("auditorias_sst", "ix_auditorias_fecha_prog"),
        ("planes_mejoramiento_sst", "ix_pm_fecha_compromiso"),
        ("matrices_legales_sst", "ix_legal_fecha_venc"),
        ("matrices_peligros_sst", "ix_peligros_fecha_venc"),
    ]
    for table, idx_name in indexes_to_drop:
        try:
            op.drop_index(idx_name, table_name=table)
        except Exception:
            pass

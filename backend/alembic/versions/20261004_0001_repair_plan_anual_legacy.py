"""Repara asociaciones legacy del Plan Anual de forma auditable.

Revision ID: m5n6o7p8q9r0
Revises: l4m5n6o7p8q9
Create Date: 2026-10-04
"""

from alembic import op
import sqlalchemy as sa


revision = "m5n6o7p8q9r0"
down_revision = "l4m5n6o7p8q9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("plan_anual_sst") or not inspector.has_table(
        "plan_anual_cabecera"
    ):
        return
    columnas = {
        columna["name"] for columna in inspector.get_columns("plan_anual_sst")
    }
    requeridas = {
        "id",
        "empresa_id",
        "vigencia",
        "plan_anual_cabecera_id",
        "activo",
        "observaciones",
    }
    if not requeridas.issubset(columnas):
        return

    bind.execute(
        sa.text(
            """
            UPDATE plan_anual_sst AS actividad
            SET plan_anual_cabecera_id = cabecera.id
            FROM plan_anual_cabecera AS cabecera
            WHERE (
                    actividad.plan_anual_cabecera_id IS NULL
                    OR NOT EXISTS (
                        SELECT 1
                        FROM plan_anual_cabecera AS actual
                        WHERE actual.id = actividad.plan_anual_cabecera_id
                          AND actual.empresa_id = actividad.empresa_id
                          AND actual.vigencia = actividad.vigencia
                    )
                  )
              AND actividad.empresa_id = cabecera.empresa_id
              AND actividad.vigencia ~ '^[0-9]{4}$'
              AND actividad.vigencia = cabecera.vigencia
              AND cabecera.activo = TRUE
              AND (
                  SELECT COUNT(*)
                  FROM plan_anual_cabecera AS candidata
                  WHERE candidata.empresa_id = actividad.empresa_id
                    AND candidata.vigencia = actividad.vigencia
                    AND candidata.activo = TRUE
              ) = 1
            """
        )
    )
    bind.execute(
        sa.text(
            """
            UPDATE plan_anual_sst
            SET activo = FALSE,
                observaciones = CONCAT_WS(
                    E'\n',
                    NULLIF(observaciones, ''),
                    '[MIGRACION m5n6o7p8q9r0] Actividad legacy desactivada: no fue posible asociarla de forma inequívoca a una cabecera y vigencia activa.'
                )
            WHERE plan_anual_cabecera_id IS NULL
              AND activo = TRUE
            """
        )
    )


def downgrade() -> None:
    raise RuntimeError(
        "Migracion irreversible: no es seguro distinguir asociaciones reparadas de asociaciones preexistentes ni reactivar actividades ambiguas."
    )

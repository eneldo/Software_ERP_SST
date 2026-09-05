"""add origen tracking to improvement plans

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6
Create Date: 2026-09-04 21:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "f2a3b4c5d6e7"
down_revision = "e1f2a3b4c5d6"
branch_labels = None
depends_on = None


def _agregar_si_falta(tabla: str, columna: sa.Column) -> None:
    existentes = {item["name"] for item in sa.inspect(op.get_bind()).get_columns(tabla)}
    if columna.name not in existentes:
        op.add_column(tabla, columna)


def upgrade() -> None:
    _agregar_si_falta(
        "planes_mejoramiento_sst",
        sa.Column("origen_hallazgo", sa.String(40), nullable=True, server_default="OTRO"),
    )
    _agregar_si_falta(
        "planes_mejoramiento_sst",
        sa.Column("origen_id", sa.Integer(), nullable=True),
    )
    inspector = sa.inspect(op.get_bind())
    indices = {item["name"] for item in inspector.get_indexes("planes_mejoramiento_sst")}
    if "ix_plan_mejora_origen" not in indices:
        op.create_index(
            "ix_plan_mejora_origen",
            "planes_mejoramiento_sst",
            ["origen_hallazgo", "origen_id"],
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    indices = {item["name"] for item in inspector.get_indexes("planes_mejoramiento_sst")}
    if "ix_plan_mejora_origen" in indices:
        op.drop_index("ix_plan_mejora_origen", table_name="planes_mejoramiento_sst")
    columnas = {item["name"] for item in inspector.get_columns("planes_mejoramiento_sst")}
    for nombre in ("origen_id", "origen_hallazgo"):
        if nombre in columnas:
            op.drop_column("planes_mejoramiento_sst", nombre)

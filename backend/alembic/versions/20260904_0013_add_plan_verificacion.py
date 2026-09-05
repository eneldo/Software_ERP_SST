"""add verification tracking to improvement plans

Revision ID: a3b4c5d6e7f8
Revises: f2a3b4c5d6e7
Create Date: 2026-09-04 22:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "a3b4c5d6e7f8"
down_revision = "f2a3b4c5d6e7"
branch_labels = None
depends_on = None


def _agregar_si_falta(tabla: str, columna: sa.Column) -> None:
    existentes = {item["name"] for item in sa.inspect(op.get_bind()).get_columns(tabla)}
    if columna.name not in existentes:
        op.add_column(tabla, columna)


def upgrade() -> None:
    _agregar_si_falta(
        "planes_mejoramiento_sst",
        sa.Column("verificado_por", sa.Integer(), nullable=True),
    )
    _agregar_si_falta(
        "planes_mejoramiento_sst",
        sa.Column("fecha_verificacion", sa.Date(), nullable=True),
    )
    _agregar_si_falta(
        "planes_mejoramiento_sst",
        sa.Column("resultado_verificacion", sa.String(30), nullable=True),
    )


def downgrade() -> None:
    columnas = {item["name"] for item in sa.inspect(op.get_bind()).get_columns("planes_mejoramiento_sst")}
    for nombre in ("resultado_verificacion", "fecha_verificacion", "verificado_por"):
        if nombre in columnas:
            op.drop_column("planes_mejoramiento_sst", nombre)

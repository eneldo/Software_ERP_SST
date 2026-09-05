"""iper: rename observaciones to responsable, add seguimiento fields

Revision ID: 0001_iper_seguimiento
Revises: 1640ada3d38b
Create Date: 2026-08-31 00:00:00.000000+00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_iper_seguimiento"
down_revision = "1640ada3d38b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    columnas = {item["name"] for item in sa.inspect(op.get_bind()).get_columns("matriz_iper")}
    if "observaciones" in columnas and "responsable" not in columnas:
        op.alter_column("matriz_iper", "observaciones", new_column_name="responsable")

    columnas = {item["name"] for item in sa.inspect(op.get_bind()).get_columns("matriz_iper")}
    nuevas = (
        sa.Column("fecha_proyectada", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fecha_ejecucion", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evidencias", sa.Text(), nullable=True),
        sa.Column("realizado", sa.String(5), server_default="NO"),
    )
    for columna in nuevas:
        if columna.name not in columnas:
            op.add_column("matriz_iper", columna)


def downgrade() -> None:
    columnas = {item["name"] for item in sa.inspect(op.get_bind()).get_columns("matriz_iper")}
    for nombre in ("realizado", "evidencias", "fecha_ejecucion", "fecha_proyectada"):
        if nombre in columnas:
            op.drop_column("matriz_iper", nombre)

    columnas = {item["name"] for item in sa.inspect(op.get_bind()).get_columns("matriz_iper")}
    if "responsable" in columnas and "observaciones" not in columnas:
        op.alter_column("matriz_iper", "responsable", new_column_name="observaciones")

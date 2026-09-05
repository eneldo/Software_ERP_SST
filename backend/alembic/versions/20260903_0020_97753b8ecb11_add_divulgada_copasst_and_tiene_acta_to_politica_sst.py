"""add_divulgada_copasst_and_tiene_acta_to_politica_sst

Revision ID: 97753b8ecb11
Revises: 0003_perfil_sociodemo
Create Date: 2026-09-03 00:20:05.993743+00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = '97753b8ecb11'
down_revision = '0003_perfil_sociodemo'
branch_labels = None
depends_on = None


def upgrade() -> None:
    columnas = {item["name"] for item in sa.inspect(op.get_bind()).get_columns("politicas_sst")}
    if "divulgada_copasst" not in columnas:
        op.add_column('politicas_sst', sa.Column('divulgada_copasst', sa.Boolean(), nullable=False, server_default=sa.false()))
    if "tiene_acta_divulgacion" not in columnas:
        op.add_column('politicas_sst', sa.Column('tiene_acta_divulgacion', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    columnas = {item["name"] for item in sa.inspect(op.get_bind()).get_columns("politicas_sst")}
    for nombre in ("tiene_acta_divulgacion", "divulgada_copasst"):
        if nombre in columnas:
            op.drop_column('politicas_sst', nombre)

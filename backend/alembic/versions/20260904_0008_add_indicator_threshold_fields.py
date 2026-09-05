"""add configurable semaforo thresholds to indicators

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-09-04 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'b8c9d0e1f2a3'
down_revision = 'a7b8c9d0e1f2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    columnas = {item["name"] for item in sa.inspect(op.get_bind()).get_columns("indicadores_sst")}
    for nombre, valor in (("umbral_verde", "90"), ("umbral_amarillo", "70"), ("umbral_naranja", "50")):
        if nombre not in columnas:
            op.add_column('indicadores_sst', sa.Column(nombre, sa.Numeric(5, 2), nullable=True, server_default=valor))


def downgrade() -> None:
    columnas = {item["name"] for item in sa.inspect(op.get_bind()).get_columns("indicadores_sst")}
    for nombre in ('umbral_naranja', 'umbral_amarillo', 'umbral_verde'):
        if nombre in columnas:
            op.drop_column('indicadores_sst', nombre)

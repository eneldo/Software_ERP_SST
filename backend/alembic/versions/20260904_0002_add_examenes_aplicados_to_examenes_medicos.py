"""add examenes_aplicados to examenes_medicos

Revision ID: b2c3d4e5f6a7
Revises: c1d2e3f4a5b6
Create Date: 2026-09-04 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'b2c3d4e5f6a7'
down_revision = 'c1d2e3f4a5b6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    columnas = {item["name"] for item in sa.inspect(op.get_bind()).get_columns("examenes_medicos")}
    if "examenes_aplicados" not in columnas:
        op.add_column(
            'examenes_medicos',
            sa.Column('examenes_aplicados', sa.Text(), nullable=True),
        )


def downgrade() -> None:
    columnas = {item["name"] for item in sa.inspect(op.get_bind()).get_columns("examenes_medicos")}
    if "examenes_aplicados" in columnas:
        op.drop_column('examenes_medicos', 'examenes_aplicados')

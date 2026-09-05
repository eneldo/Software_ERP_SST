"""add resolucion 2646 fields to sociodemographic profile

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-09-04 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'a7b8c9d0e1f2'
down_revision = 'f6a7b8c9d0e1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    columnas = {item["name"] for item in sa.inspect(op.get_bind()).get_columns("empleado_perfil_sociodemografico")}
    nuevas = (
        sa.Column('grupo_sanguineo', sa.String(10), nullable=True),
        sa.Column('discapacidad', sa.Boolean(), default=False),
        sa.Column('tipo_discapacidad', sa.String(100), nullable=True),
        sa.Column('porcentaje_discapacidad', sa.Integer(), nullable=True),
        sa.Column('tiene_hijos', sa.Boolean(), default=False),
        sa.Column('num_hijos', sa.Integer(), default=0),
        sa.Column('areas_formacion', sa.JSON(), nullable=True),
    )
    for columna in nuevas:
        if columna.name not in columnas:
            op.add_column('empleado_perfil_sociodemografico', columna)


def downgrade() -> None:
    columnas = {item["name"] for item in sa.inspect(op.get_bind()).get_columns("empleado_perfil_sociodemografico")}
    for nombre in ('areas_formacion', 'num_hijos', 'tiene_hijos', 'porcentaje_discapacidad', 'tipo_discapacidad', 'discapacidad', 'grupo_sanguineo'):
        if nombre in columnas:
            op.drop_column('empleado_perfil_sociodemografico', nombre)

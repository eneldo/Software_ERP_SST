"""Agrega campos demográficos al perfil sociodemográfico del empleado.

Revision ID: 0002_empleado_demografico
Revises: 0001_cargo_epp
Create Date: 2026-09-02 14:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_empleado_demografico"
down_revision = "0001_cargo_epp"
branch_labels = None
depends_on = None


def _column_exists(table: str, column: str, bind) -> bool:
    columns = [c["name"] for c in sa.inspect(bind).get_columns(table)]
    return column in columns


def upgrade() -> None:
    bind = op.get_bind()
    table = "empleados"
    columns_to_add = [
        ("genero", sa.String(20)),
        ("grupo_etnico", sa.String(50)),
        ("discapacidad", sa.String(50)),
        ("rango_edad", sa.String(20)),
        ("nivel_escolaridad", sa.String(50)),
        ("estado_civil", sa.String(20)),
        ("tipo_sangre", sa.String(5)),
    ]
    for col_name, col_type in columns_to_add:
        if not _column_exists(table, col_name, bind):
            op.add_column(table, sa.Column(col_name, col_type, nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    table = "empleados"
    for col_name in ["tipo_sangre", "estado_civil", "nivel_escolaridad", "rango_edad", "discapacidad", "grupo_etnico", "genero"]:
        if _column_exists(table, col_name, bind):
            op.drop_column(table, col_name)

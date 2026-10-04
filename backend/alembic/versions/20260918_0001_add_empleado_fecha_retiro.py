"""Agrega fecha de retiro al empleado.

Revision ID: l4m5n6o7p8q9
Revises: k3l4m5n6o7p8
Create Date: 2026-09-18
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "l4m5n6o7p8q9"
down_revision: Union[str, Sequence[str], None] = "k3l4m5n6o7p8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _columnas_empleados() -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table("empleados"):
        return set()
    return {column["name"] for column in inspector.get_columns("empleados")}


def upgrade() -> None:
    if "fecha_retiro" not in _columnas_empleados():
        op.add_column("empleados", sa.Column("fecha_retiro", sa.Date(), nullable=True))


def downgrade() -> None:
    if "fecha_retiro" in _columnas_empleados():
        op.drop_column("empleados", "fecha_retiro")

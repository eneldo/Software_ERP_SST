"""create parametrizable Res.0312 criteria table

Revision ID: b4c5d6e7f8a9
Revises: a3b4c5d6e7f8
Create Date: 2026-09-04 23:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "b4c5d6e7f8a9"
down_revision = "a3b4c5d6e7f8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if "estandares_minimos_criterios" in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        "estandares_minimos_criterios",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("tipo_estandares", sa.String(10), nullable=False, index=True),
        sa.Column("estandar", sa.String(180), nullable=False),
        sa.Column("numeral", sa.String(30), nullable=False, index=True),
        sa.Column("criterio", sa.Text(), nullable=False),
        sa.Column("puntaje", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("version_norma", sa.String(30), nullable=False, server_default="0312-2019"),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true(), index=True),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.UniqueConstraint(
            "tipo_estandares", "numeral", "version_norma",
            name="uq_estandar_criterio",
        ),
    )


def downgrade() -> None:
    if "estandares_minimos_criterios" in sa.inspect(op.get_bind()).get_table_names():
        op.drop_table("estandares_minimos_criterios")

"""Agrega personalización visual y marca corporativa.

Revision ID: 0002_apariencia
Revises: 0001_initial_schema
Create Date: 2026-07-20 19:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_apariencia"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if "apariencia_sistema" in sa.inspect(bind).get_table_names():
        return
    op.create_table(
        "apariencia_sistema",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("logo_data_url", sa.Text(), nullable=True),
        sa.Column("color_primario", sa.String(7), nullable=False, server_default="#2563EB"),
        sa.Column("color_secundario", sa.String(7), nullable=False, server_default="#1E40AF"),
        sa.Column("color_menu_inicio", sa.String(7), nullable=False, server_default="#0F172A"),
        sa.Column("color_menu_fin", sa.String(7), nullable=False, server_default="#1E3A8A"),
        sa.Column("tipografia", sa.String(50), nullable=False, server_default="Inter"),
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_apariencia_sistema_id", "apariencia_sistema", ["id"])


def downgrade() -> None:
    bind = op.get_bind()
    if "apariencia_sistema" not in sa.inspect(bind).get_table_names():
        return
    op.drop_index("ix_apariencia_sistema_id", table_name="apariencia_sistema")
    op.drop_table("apariencia_sistema")

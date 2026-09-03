"""Crea la asociación entre cargos y el catálogo EPP.

Revision ID: 0001_cargo_epp
Revises: 6c49b648f263
Create Date: 2026-09-02 11:30:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_cargo_epp"
down_revision = "6c49b648f263"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if "cargo_epp_catalogo" in sa.inspect(bind).get_table_names():
        return
    op.create_table(
        "cargo_epp_catalogo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("cargo_id", sa.Integer(), nullable=False),
        sa.Column("epp_id", sa.Integer(), nullable=False),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["cargo_id"], ["cargos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["epp_id"], ["epp_catalogo.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("cargo_id", "epp_id", name="uq_cargo_epp_catalogo"),
    )
    op.create_index("ix_cargo_epp_catalogo_id", "cargo_epp_catalogo", ["id"])
    op.create_index("ix_cargo_epp_catalogo_empresa_id", "cargo_epp_catalogo", ["empresa_id"])
    op.create_index("ix_cargo_epp_catalogo_cargo_id", "cargo_epp_catalogo", ["cargo_id"])
    op.create_index("ix_cargo_epp_catalogo_epp_id", "cargo_epp_catalogo", ["epp_id"])


def downgrade() -> None:
    bind = op.get_bind()
    if "cargo_epp_catalogo" not in sa.inspect(bind).get_table_names():
        return
    op.drop_index("ix_cargo_epp_catalogo_epp_id", table_name="cargo_epp_catalogo")
    op.drop_index("ix_cargo_epp_catalogo_cargo_id", table_name="cargo_epp_catalogo")
    op.drop_index("ix_cargo_epp_catalogo_empresa_id", table_name="cargo_epp_catalogo")
    op.drop_index("ix_cargo_epp_catalogo_id", table_name="cargo_epp_catalogo")
    op.drop_table("cargo_epp_catalogo")

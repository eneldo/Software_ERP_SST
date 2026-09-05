"""add_tipo_politica_to_politicas_sst

Revision ID: c5d6e7f8a9b0
Revises: b4c5d6e7f8a9
Create Date: 2026-09-05
"""
from alembic import op
import sqlalchemy as sa

revision = "c5d6e7f8a9b0"
down_revision = "b4c5d6e7f8a9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    tables = {t for t in inspector.get_table_names()}
    if "politicas_sst" not in tables:
        return

    columns = {col["name"] for col in inspector.get_columns("politicas_sst")}

    if "tipo_politica" not in columns:
        op.add_column(
            "politicas_sst",
            sa.Column("tipo_politica", sa.String(50), nullable=False, server_default="POLITICA_SST"),
        )
        op.create_index("ix_politicas_sst_tipo_politica", "politicas_sst", ["tipo_politica"])

    existing_indexes = {idx["name"] for idx in inspector.get_indexes("politicas_sst")}
    if "uq_politica_empresa_tipo_version" not in existing_indexes:
        op.create_unique_constraint(
            "uq_politica_empresa_tipo_version",
            "politicas_sst",
            ["empresa_id", "tipo_politica", "version"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    tables = {t for t in inspector.get_table_names()}
    if "politicas_sst" not in tables:
        return

    existing_constraints = {
        c["name"] for c in inspector.get_unique_constraints("politicas_sst")
    }
    if "uq_politica_empresa_tipo_version" in existing_constraints:
        op.drop_constraint("uq_politica_empresa_tipo_version", "politicas_sst", type_="unique")

    columns = {col["name"] for col in inspector.get_columns("politicas_sst")}
    if "tipo_politica" in columns:
        op.drop_index("ix_politicas_sst_tipo_politica", "politicas_sst")
        op.drop_column("politicas_sst", "tipo_politica")

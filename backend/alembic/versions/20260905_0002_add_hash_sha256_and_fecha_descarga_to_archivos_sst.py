"""add_hash_sha256_and_fecha_descarga_to_archivos_sst

Revision ID: d6e7f8a9b0c1
Revises: c5d6e7f8a9b0
Create Date: 2026-09-05
"""
from alembic import op
import sqlalchemy as sa

revision = "d6e7f8a9b0c1"
down_revision = "c5d6e7f8a9b0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    tables = {t for t in inspector.get_table_names()}
    if "archivos_sst" not in tables:
        return

    columns = {col["name"] for col in inspector.get_columns("archivos_sst")}

    if "hash_sha256" not in columns:
        op.add_column(
            "archivos_sst",
            sa.Column("hash_sha256", sa.String(64), nullable=True),
        )
        op.create_index("ix_archivos_sst_hash_sha256", "archivos_sst", ["hash_sha256"])

    if "fecha_descarga" not in columns:
        op.add_column(
            "archivos_sst",
            sa.Column("fecha_descarga", sa.DateTime(timezone=True), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    tables = {t for t in inspector.get_table_names()}
    if "archivos_sst" not in tables:
        return

    columns = {col["name"] for col in inspector.get_columns("archivos_sst")}

    if "fecha_descarga" in columns:
        op.drop_column("archivos_sst", "fecha_descarga")

    if "hash_sha256" in columns:
        op.drop_index("ix_archivos_sst_hash_sha256", "archivos_sst")
        op.drop_column("archivos_sst", "hash_sha256")

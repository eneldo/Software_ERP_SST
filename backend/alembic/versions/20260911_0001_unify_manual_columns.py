"""Unificación columnas agregadas manualmente: responsable_id, tipo_politica, hash_sha256, fecha_descarga

Revision ID: i1j2k3l4m5n6
Revises: h8i9j0k1l2m3
Create Date: 2026-09-11
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision = "i1j2k3l4m5n6"
down_revision = "h8i9j0k1l2m3"
branch_labels = None
depends_on = None


def _column_exists(bind, table: str, column: str) -> bool:
    inspector = sa.inspect(bind)
    if table not in inspector.get_table_names():
        return False
    columns = {c["name"] for c in inspector.get_columns(table)}
    return column in columns


def upgrade() -> None:
    bind = op.get_bind()

    # 1. planes_mejoramiento_sst.responsable_id
    if not _column_exists(bind, "planes_mejoramiento_sst", "responsable_id"):
        op.add_column(
            "planes_mejoramiento_sst",
            sa.Column("responsable_id", sa.Integer(), nullable=True),
        )
        op.create_foreign_key(
            "fk_planes_mejoramiento_responsable",
            "planes_mejoramiento_sst",
            "usuarios",
            ["responsable_id"],
            ["id"],
            ondelete="SET NULL",
        )

    # 2. politicas_sst.tipo_politica
    if not _column_exists(bind, "politicas_sst", "tipo_politica"):
        op.add_column(
            "politicas_sst",
            sa.Column("tipo_politica", sa.String(50), nullable=True),
        )

    # 3. archivos_sst.hash_sha256
    if not _column_exists(bind, "archivos_sst", "hash_sha256"):
        op.add_column(
            "archivos_sst",
            sa.Column("hash_sha256", sa.String(64), nullable=True),
        )

    # 4. archivos_sst.fecha_descarga
    if not _column_exists(bind, "archivos_sst", "fecha_descarga"):
        op.add_column(
            "archivos_sst",
            sa.Column("fecha_descarga", sa.DateTime(timezone=True), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()

    if _column_exists(bind, "archivos_sst", "fecha_descarga"):
        op.drop_column("archivos_sst", "fecha_descarga")

    if _column_exists(bind, "archivos_sst", "hash_sha256"):
        op.drop_column("archivos_sst", "hash_sha256")

    if _column_exists(bind, "politicas_sst", "tipo_politica"):
        op.drop_column("politicas_sst", "tipo_politica")

    if _column_exists(bind, "planes_mejoramiento_sst", "responsable_id"):
        op.drop_constraint("fk_planes_mejoramiento_responsable", "planes_mejoramiento_sst")
        op.drop_column("planes_mejoramiento_sst", "responsable_id")

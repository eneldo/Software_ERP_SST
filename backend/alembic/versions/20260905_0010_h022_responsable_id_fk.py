"""H-022: Add responsable_id FK to plan mejoramiento

Revision ID: 20260905_0010
Revises: 20260905_0009
Create Date: 2026-09-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "20260905_0010"
down_revision = "20260905_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = inspect(conn)

    if "planes_mejoramiento_sst" not in insp.get_table_names():
        return

    columns = {c["name"] for c in insp.get_columns("planes_mejoramiento_sst")}

    if "responsable_id" not in columns:
        op.add_column(
            "planes_mejoramiento_sst",
            sa.Column("responsable_id", sa.Integer, sa.ForeignKey("usuarios.id"), nullable=True),
        )


def downgrade() -> None:
    op.drop_constraint("fk_planes_mejoramiento_responsable_id_usuarios", "planes_mejoramiento_sst", if_exists=True)
    op.drop_column("planes_mejoramiento_sst", "responsable_id")

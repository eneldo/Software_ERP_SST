"""H-014: Add tipo_capacitacion and riesgo_asociado to capacitaciones_sst

Revision ID: e7f8a9b0c1d2
Revises: b1c2d3e4f5a6
Create Date: 2026-09-05 00:02:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "e7f8a9b0c1d2"
down_revision = "b1c2d3e4f5a6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "capacitaciones_sst" in inspector.get_table_names():
        columns = {col["name"] for col in inspector.get_columns("capacitaciones_sst")}

        if "tipo_capacitacion" not in columns:
            op.add_column(
                "capacitaciones_sst",
                sa.Column(
                    "tipo_capacitacion",
                    sa.String(80),
                    nullable=False,
                    server_default="CAPACITACION_GENERAL",
                ),
            )
            op.create_index(
                "ix_capacitaciones_sst_tipo_capacitacion",
                "capacitaciones_sst",
                ["tipo_capacitacion"],
            )

        if "riesgo_asociado" not in columns:
            op.add_column(
                "capacitaciones_sst",
                sa.Column("riesgo_asociado", sa.String(255), nullable=True),
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "capacitaciones_sst" in inspector.get_table_names():
        columns = {col["name"] for col in inspector.get_columns("capacitaciones_sst")}

        if "riesgo_asociado" in columns:
            op.drop_column("capacitaciones_sst", "riesgo_asociado")

        if "tipo_capacitacion" in columns:
            op.drop_index("ix_capacitaciones_sst_tipo_capacitacion", "capacitaciones_sst")
            op.drop_column("capacitaciones_sst", "tipo_capacitacion")

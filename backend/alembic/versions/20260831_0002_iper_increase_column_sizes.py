"""iper: increase interpretacion column sizes

Revision ID: 0002_iper_column_sizes
Revises: 0001_iper_seguimiento
Create Date: 2026-08-31 00:01:00.000000+00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_iper_column_sizes"
down_revision = "0001_iper_seguimiento"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "matriz_iper", "interpretacion_np",
        existing_type=sa.String(30),
        type_=sa.String(50),
    )
    op.alter_column(
        "matriz_iper", "interpretacion_nr",
        existing_type=sa.String(30),
        type_=sa.String(80),
    )


def downgrade() -> None:
    op.alter_column(
        "matriz_iper", "interpretacion_np",
        existing_type=sa.String(50),
        type_=sa.String(30),
    )
    op.alter_column(
        "matriz_iper", "interpretacion_nr",
        existing_type=sa.String(80),
        type_=sa.String(30),
    )

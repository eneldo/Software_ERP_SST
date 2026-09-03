"""add nivel_riesgo to matriz_iper

Revision ID: 6c49b648f263
Revises: 0002_iper_column_sizes
Create Date: 2026-08-31 22:39:08.021534+00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = '6c49b648f263'
down_revision = '0002_iper_column_sizes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('matriz_iper', sa.Column('nivel_riesgo', sa.String(length=10), nullable=True))


def downgrade() -> None:
    op.drop_column('matriz_iper', 'nivel_riesgo')

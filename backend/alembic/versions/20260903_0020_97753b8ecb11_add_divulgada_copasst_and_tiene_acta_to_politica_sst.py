"""add_divulgada_copasst_and_tiene_acta_to_politica_sst

Revision ID: 97753b8ecb11
Revises: 0003_perfil_sociodemo
Create Date: 2026-09-03 00:20:05.993743+00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = '97753b8ecb11'
down_revision = '0003_perfil_sociodemo'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('politicas_sst', sa.Column('divulgada_copasst', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('politicas_sst', sa.Column('tiene_acta_divulgacion', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column('politicas_sst', 'tiene_acta_divulgacion')
    op.drop_column('politicas_sst', 'divulgada_copasst')
"""increase cargo exposicion to 700

Revision ID: c1d2e3f4a5b6
Revises: 97753b8ecb11
Create Date: 2026-09-04 10:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'c1d2e3f4a5b6'
down_revision = '97753b8ecb11'
branch_labels = None
depends_on = None


def upgrade() -> None:
    columna = next(item for item in sa.inspect(op.get_bind()).get_columns("cargos") if item["name"] == "exposicion")
    if getattr(columna["type"], "length", None) != 700:
        op.alter_column(
            'cargos',
            'exposicion',
            existing_type=columna["type"],
            type_=sa.String(700),
            existing_nullable=True,
        )


def downgrade() -> None:
    op.alter_column(
        'cargos',
        'exposicion',
        existing_type=sa.String(700),
        type_=sa.String(80),
        existing_nullable=True,
    )

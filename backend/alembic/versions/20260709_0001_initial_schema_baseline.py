"""Initial schema baseline.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-09 00:00:00

Esta revision formaliza el esquema actual del ERP SST PRO en Alembic.
En bases existentes, `create_all(checkfirst=True)` conserva las tablas ya
presentes y permite marcar el baseline con `alembic stamp head` cuando aplique.
"""

from __future__ import annotations

from alembic import op

from app.database import Base
from app.models import import_all_models


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    import_all_models()
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, checkfirst=True)


def downgrade() -> None:
    import_all_models()
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind, checkfirst=True)

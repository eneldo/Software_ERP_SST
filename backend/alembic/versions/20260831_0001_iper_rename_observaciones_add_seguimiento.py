"""iper: rename observaciones to responsable, add seguimiento fields

Revision ID: 0001_iper_seguimiento
Revises: 1640ada3d38b
Create Date: 2026-08-31 00:00:00.000000+00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_iper_seguimiento"
down_revision = "1640ada3d38b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Renombrar observaciones -> responsable
    op.alter_column("matriz_iper", "observaciones", new_column_name="responsable")

    # Agregar campos de seguimiento
    op.add_column("matriz_iper", sa.Column("fecha_proyectada", sa.DateTime(timezone=True), nullable=True))
    op.add_column("matriz_iper", sa.Column("fecha_ejecucion", sa.DateTime(timezone=True), nullable=True))
    op.add_column("matriz_iper", sa.Column("evidencias", sa.Text(), nullable=True))
    op.add_column("matriz_iper", sa.Column("realizado", sa.String(5), server_default="NO"))


def downgrade() -> None:
    op.drop_column("matriz_iper", "realizado")
    op.drop_column("matriz_iper", "evidencias")
    op.drop_column("matriz_iper", "fecha_ejecucion")
    op.drop_column("matriz_iper", "fecha_proyectada")

    # Renombrar responsable -> observaciones
    op.alter_column("matriz_iper", "responsable", new_column_name="observaciones")

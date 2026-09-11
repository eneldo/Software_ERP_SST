"""
Normaliza requiere_vigilancia_medica en cargos.

Revision ID: k3l4m5n6o7p8
Revises: j2k3l4m5n6o7
Create Date: 2026-09-11

- Convierte valores NULL existentes a FALSE.
- Establece DEFAULT FALSE.
- Establece NOT NULL.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "k3l4m5n6o7p8"
down_revision: Union[str, Sequence[str], None] = "j2k3l4m5n6o7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Corregir registros históricos antes de aplicar NOT NULL.
    op.execute(
        """
        UPDATE cargos
        SET requiere_vigilancia_medica = FALSE
        WHERE requiere_vigilancia_medica IS NULL
        """
    )

    op.alter_column(
        "cargos",
        "requiere_vigilancia_medica",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.text("false"),
    )


def downgrade() -> None:
    op.alter_column(
        "cargos",
        "requiere_vigilancia_medica",
        existing_type=sa.Boolean(),
        nullable=True,
        server_default=None,
    )
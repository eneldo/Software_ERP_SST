"""H-017: Create estandares_minimos_historial table

Revision ID: e2f3a4b5c6d7
Revises: f8a9b0c1d2e3
Create Date: 2026-09-05 00:04:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "e2f3a4b5c6d7"
down_revision = "f8a9b0c1d2e3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "estandares_minimos_historial" not in inspector.get_table_names():
        op.create_table(
            "estandares_minimos_historial",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column(
                "estandar_criterio_id",
                sa.Integer(),
                sa.ForeignKey("estandares_minimos_criterios.id", ondelete="CASCADE"),
                nullable=False,
                index=True,
            ),
            sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=True, index=True),
            sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
            sa.Column("tipo_cambio", sa.String(50), nullable=False, index=True),
            sa.Column("descripcion_cambio", sa.Text(), nullable=False),
            sa.Column("valor_anterior", sa.Text(), nullable=True),
            sa.Column("valor_nuevo", sa.Text(), nullable=True),
            sa.Column("activo", sa.Boolean(), server_default="true"),
            sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "estandares_minimos_historial" in inspector.get_table_names():
        op.drop_table("estandares_minimos_historial")

"""H-020: Create plantillas_notificaciones_sst table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-09-05 00:05:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "plantillas_notificaciones_sst" not in inspector.get_table_names():
        op.create_table(
            "plantillas_notificaciones_sst",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=True, index=True),
            sa.Column("codigo", sa.String(80), nullable=False, index=True),
            sa.Column("nombre", sa.String(255), nullable=False),
            sa.Column("modulo", sa.String(80), nullable=False, index=True),
            sa.Column("tipo_evento", sa.String(80), nullable=False, index=True),
            sa.Column("asunto", sa.String(500), nullable=False),
            sa.Column("cuerpo_html", sa.Text(), nullable=False),
            sa.Column("cuerpo_plano", sa.Text(), nullable=True),
            sa.Column("canal_sistema", sa.Boolean(), server_default="true"),
            sa.Column("canal_email", sa.Boolean(), server_default="false"),
            sa.Column("canal_whatsapp", sa.Boolean(), server_default="false"),
            sa.Column("prioridad_default", sa.String(40), server_default="MEDIA"),
            sa.Column("variables_disponibles", sa.Text(), nullable=True),
            sa.Column("activo", sa.Boolean(), server_default="true"),
            sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "plantillas_notificaciones_sst" in inspector.get_table_names():
        op.drop_table("plantillas_notificaciones_sst")

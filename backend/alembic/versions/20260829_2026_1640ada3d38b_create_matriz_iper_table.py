"""create matriz_iper table

Revision ID: 1640ada3d38b
Revises: 0002_apariencia
Create Date: 2026-08-29 20:26:29.792242+00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "1640ada3d38b"
down_revision = "0002_apariencia"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "matriz_iper",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "empresa_id",
            sa.Integer(),
            sa.ForeignKey("empresas.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "usuario_id",
            sa.Integer(),
            sa.ForeignKey("usuarios.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # 1. Contexto
        sa.Column("proceso", sa.String(200), nullable=False),
        sa.Column("zona_lugar", sa.String(255), nullable=True),
        sa.Column("actividades", sa.String(255), nullable=True),
        sa.Column("tareas", sa.Text(), nullable=True),
        sa.Column("rutinaria", sa.String(5), server_default="SI"),
        # 2. Peligro
        sa.Column("clasificacion_peligro", sa.String(50), nullable=False),
        sa.Column("descripcion_peligro", sa.Text(), nullable=False),
        sa.Column("riesgo", sa.String(300), nullable=True),
        sa.Column("efectos_posibles", sa.Text(), nullable=False),
        # 3. Controles existentes
        sa.Column("fuente", sa.String(300), nullable=True),
        sa.Column("medio", sa.String(300), nullable=True),
        sa.Column("individuo", sa.String(300), nullable=True),
        # 4. Evaluación GTC45
        sa.Column("nd", sa.Integer(), server_default="0"),
        sa.Column("ne", sa.Integer(), server_default="1"),
        sa.Column("np", sa.Integer(), server_default="0"),
        sa.Column("interpretacion_np", sa.String(30), nullable=True),
        sa.Column("nc", sa.Integer(), server_default="10"),
        sa.Column("nr", sa.Integer(), server_default="0"),
        sa.Column("interpretacion_nr", sa.String(30), nullable=True),
        sa.Column("aceptabilidad", sa.String(50), nullable=True),
        # 5. Criterios
        sa.Column("expuestos_hombres", sa.Integer(), server_default="0"),
        sa.Column("expuestos_mujeres", sa.Integer(), server_default="0"),
        sa.Column("expuestos_gestantes", sa.Integer(), server_default="0"),
        sa.Column("peor_consecuencia", sa.String(300), nullable=True),
        # 6. Medidas de intervención
        sa.Column("eliminacion", sa.Text(), nullable=True),
        sa.Column("control_ingenieria", sa.Text(), nullable=True),
        sa.Column("sustitucion", sa.Text(), nullable=True),
        sa.Column("senalizacion_admin", sa.Text(), nullable=True),
        sa.Column("epp", sa.Text(), nullable=True),
        # Control
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.Column("activo", sa.Boolean(), server_default="true"),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "fecha_actualizacion",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("matriz_iper")

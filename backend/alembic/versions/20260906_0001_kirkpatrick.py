"""H-026: Evaluación Kirkpatrick SST - 4 niveles

Revision ID: c8d9e0f1a2b3
Revises: 20260905_0010
Create Date: 2026-09-06
"""

from alembic import op
import sqlalchemy as sa

revision = "c8d9e0f1a2b3"
down_revision = "20260905_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = {t for t in inspector.get_table_names()}

    if "evaluaciones_kirkpatrick_sst" not in tables:
        op.create_table(
            "evaluaciones_kirkpatrick_sst",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("capacitacion_id", sa.Integer(), sa.ForeignKey("capacitaciones_sst.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("empleado_id", sa.Integer(), sa.ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True, index=True),
            sa.Column("nivel1_satisfaccion", sa.Integer(), nullable=True),
            sa.Column("nivel1_comentario", sa.Text(), nullable=True),
            sa.Column("nivel2_puntuacion_pre", sa.Numeric(5, 2), nullable=True),
            sa.Column("nivel2_puntuacion_post", sa.Numeric(5, 2), nullable=True),
            sa.Column("nivel2_aprobado", sa.Boolean(), default=False),
            sa.Column("nivel3_observacion_30d", sa.Text(), nullable=True),
            sa.Column("nivel3_observacion_60d", sa.Text(), nullable=True),
            sa.Column("nivel3_observacion_90d", sa.Text(), nullable=True),
            sa.Column("nivel3_aplicacion_pct", sa.Numeric(5, 2), nullable=True),
            sa.Column("nivel4_indicador", sa.String(255), nullable=True),
            sa.Column("nivel4_valor_antes", sa.Numeric(10, 2), nullable=True),
            sa.Column("nivel4_valor_despues", sa.Numeric(10, 2), nullable=True),
            sa.Column("nivel4_impacto", sa.Text(), nullable=True),
            sa.Column("responsable_seguimiento", sa.String(255), nullable=True),
            sa.Column("estado", sa.String(50), default="PENDIENTE"),
            sa.Column("activo", sa.Boolean(), default=True),
            sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = {t for t in inspector.get_table_names()}
    if "evaluaciones_kirkpatrick_sst" in tables:
        op.drop_table("evaluaciones_kirkpatrick_sst")

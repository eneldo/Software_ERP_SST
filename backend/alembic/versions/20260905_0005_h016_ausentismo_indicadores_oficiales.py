"""H-016: Add jornada_laboral_diaria to empleados + ausentismo_sst table

Revision ID: f8a9b0c1d2e3
Revises: e7f8a9b0c1d2
Create Date: 2026-09-05 00:03:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "f8a9b0c1d2e3"
down_revision = "e7f8a9b0c1d2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # H-016: jornada_laboral_diaria on empleados
    if "empleados" in inspector.get_table_names():
        columns = {col["name"] for col in inspector.get_columns("empleados")}
        if "jornada_laboral_diaria" not in columns:
            op.add_column(
                "empleados",
                sa.Column(
                    "jornada_laboral_diaria",
                    sa.Integer(),
                    nullable=False,
                    server_default="8",
                ),
            )

    # H-016: ausentismo_sst table
    if "ausentismo_sst" not in inspector.get_table_names():
        op.create_table(
            "ausentismo_sst",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("empleado_id", sa.Integer(), sa.ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True, index=True),
            sa.Column("usuario_registro_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
            sa.Column("tipo_ausentismo", sa.String(80), nullable=False, index=True),
            sa.Column("fecha_inicio", sa.Date(), nullable=False, index=True),
            sa.Column("fecha_fin", sa.Date(), nullable=True),
            sa.Column("dias_ausentismo", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("diagnostico", sa.String(255), nullable=True),
            sa.Column("clase_riesgo", sa.String(50), nullable=True),
            sa.Column("observaciones", sa.Text(), nullable=True),
            sa.Column("activo", sa.Boolean(), server_default="true"),
            sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "ausentismo_sst" in inspector.get_table_names():
        op.drop_table("ausentismo_sst")

    if "empleados" in inspector.get_table_names():
        columns = {col["name"] for col in inspector.get_columns("empleados")}
        if "jornada_laboral_diaria" in columns:
            op.drop_column("empleados", "jornada_laboral_diaria")

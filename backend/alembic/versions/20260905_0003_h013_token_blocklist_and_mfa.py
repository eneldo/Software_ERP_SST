"""H-013a+b: token_blocklist + mfa columns

Revision ID: d6e7f8a9b0c1
Revises: c5d6e7f8a9b0
Create Date: 2026-09-05 00:01:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "d6e7f8a9b0c1"
down_revision = "c5d6e7f8a9b0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # H-013a: Token blocklist
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "token_blocklist" not in inspector.get_table_names():
        op.create_table(
            "token_blocklist",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("jti", sa.String(36), nullable=False, unique=True, index=True),
            sa.Column("token_type", sa.String(20), nullable=False, server_default="access"),
            sa.Column("usuario_id", sa.Integer(), nullable=True, index=True),
            sa.Column("empresa_id", sa.Integer(), nullable=True),
            sa.Column("motivo", sa.String(100), nullable=True),
            sa.Column("bloqueado_por", sa.Integer(), nullable=True),
            sa.Column("exp", sa.DateTime(timezone=True), nullable=False, index=True),
            sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Index("ix_token_blocklist_jti_type", "jti", "token_type"),
        )

    # H-013b: MFA columns on usuarios
    if "usuarios" in inspector.get_table_names():
        columns = {col["name"] for col in inspector.get_columns("usuarios")}
        if "mfa_secret" not in columns:
            op.add_column("usuarios", sa.Column("mfa_secret", sa.String(64), nullable=True))
        if "mfa_enabled" not in columns:
            op.add_column("usuarios", sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default="false"))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "usuarios" in inspector.get_table_names():
        columns = {col["name"] for col in inspector.get_columns("usuarios")}
        if "mfa_enabled" in columns:
            op.drop_column("usuarios", "mfa_enabled")
        if "mfa_secret" in columns:
            op.drop_column("usuarios", "mfa_secret")

    if "token_blocklist" in inspector.get_table_names():
        op.drop_table("token_blocklist")

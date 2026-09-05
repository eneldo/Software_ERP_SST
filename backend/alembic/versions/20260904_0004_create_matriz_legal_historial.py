"""create matriz_legal_historial table

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-09-04 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'd4e5f6a7b8c9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    if 'matriz_legal_historial' in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        'matriz_legal_historial',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('matriz_legal_id', sa.Integer(), sa.ForeignKey('matriz_legal_sst.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('empresa_id', sa.Integer(), sa.ForeignKey('empresas.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True),
        sa.Column('tipo_cambio', sa.String(50), nullable=False),
        sa.Column('descripcion_cambio', sa.Text(), nullable=False),
        sa.Column('valor_anterior', sa.Text(), nullable=True),
        sa.Column('valor_nuevo', sa.Text(), nullable=True),
        sa.Column('norma_anterior', sa.String(255), nullable=True),
        sa.Column('estado_norma_anterior', sa.String(80), nullable=True),
        sa.Column('estado_norma_nuevo', sa.String(80), nullable=True),
        sa.Column('motivo', sa.Text(), nullable=True),
        sa.Column('fecha_efectiva', sa.Date(), nullable=True),
        sa.Column('activo', sa.Boolean(), default=True),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    if 'matriz_legal_historial' in sa.inspect(op.get_bind()).get_table_names():
        op.drop_table('matriz_legal_historial')

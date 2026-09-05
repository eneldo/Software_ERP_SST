"""create comites_sst tables

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-09-04 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'e5f6a7b8c9d0'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    if 'comites_sst' in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        'comites_sst',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('empresa_id', sa.Integer(), sa.ForeignKey('empresas.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True),
        sa.Column('tipo_comite', sa.String(50), nullable=False, index=True),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('fecha_constitucion', sa.Date(), nullable=True),
        sa.Column('fecha_fin_periodo', sa.Date(), nullable=True),
        sa.Column('vigente', sa.Boolean(), default=True, index=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('activo', sa.Boolean(), default=True),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        'comites_integrantes_sst',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('comite_id', sa.Integer(), sa.ForeignKey('comites_sst.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('empresa_id', sa.Integer(), sa.ForeignKey('empresas.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('empleado_id', sa.Integer(), sa.ForeignKey('empleados.id', ondelete='SET NULL'), nullable=True),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('documento', sa.String(80), nullable=True),
        sa.Column('cargo', sa.String(255), nullable=True),
        sa.Column('rol_comite', sa.String(100), nullable=False),
        sa.Column('representa', sa.String(100), nullable=True),
        sa.Column('fecha_eleccion', sa.Date(), nullable=True),
        sa.Column('fecha_fin_cargo', sa.Date(), nullable=True),
        sa.Column('activo', sa.Boolean(), default=True),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        'comites_reuniones_sst',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('comite_id', sa.Integer(), sa.ForeignKey('comites_sst.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('empresa_id', sa.Integer(), sa.ForeignKey('empresas.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True),
        sa.Column('numero_reunion', sa.Integer(), nullable=False),
        sa.Column('fecha_reunion', sa.Date(), nullable=False, index=True),
        sa.Column('hora_inicio', sa.String(20), nullable=True),
        sa.Column('hora_fin', sa.String(20), nullable=True),
        sa.Column('lugar', sa.String(255), nullable=True),
        sa.Column('tema', sa.Text(), nullable=True),
        sa.Column('acuerdos', sa.Text(), nullable=True),
        sa.Column('compromisos', sa.Text(), nullable=True),
        sa.Column('total_asistentes', sa.Integer(), default=0),
        sa.Column('asistentes_ids', sa.Text(), nullable=True),
        sa.Column('acta_url', sa.String(500), nullable=True),
        sa.Column('acta_archivo_id', sa.Integer(), sa.ForeignKey('archivos_sst.id', ondelete='SET NULL'), nullable=True),
        sa.Column('estado', sa.String(50), default='PROGRAMADA', index=True),
        sa.Column('activo', sa.Boolean(), default=True),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    if 'comites_sst' not in sa.inspect(op.get_bind()).get_table_names():
        return
    op.drop_table('comites_reuniones_sst')
    op.drop_table('comites_integrantes_sst')
    op.drop_table('comites_sst')

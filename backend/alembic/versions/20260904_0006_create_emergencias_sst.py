"""create emergencias_sst tables

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-09-04 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'f6a7b8c9d0e1'
down_revision = 'e5f6a7b8c9d0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    if 'brigadas_emergencia' in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        'brigadas_emergencia',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('empresa_id', sa.Integer(), sa.ForeignKey('empresas.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('tipo_brigada', sa.String(100), nullable=False, index=True),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('fecha_conformacion', sa.Date(), nullable=True),
        sa.Column('activo', sa.Boolean(), default=True),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        'brigadas_integrantes_sst',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('brigada_id', sa.Integer(), sa.ForeignKey('brigadas_emergencia.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('empresa_id', sa.Integer(), sa.ForeignKey('empresas.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('empleado_id', sa.Integer(), sa.ForeignKey('empleados.id', ondelete='SET NULL'), nullable=True),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('documento', sa.String(80), nullable=True),
        sa.Column('cargo', sa.String(255), nullable=True),
        sa.Column('rol_brigada', sa.String(100), nullable=False),
        sa.Column('telefono', sa.String(80), nullable=True),
        sa.Column('activo', sa.Boolean(), default=True),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        'simulacros_emergencia',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('empresa_id', sa.Integer(), sa.ForeignKey('empresas.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True),
        sa.Column('codigo', sa.String(80), nullable=False, index=True),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('tipo_emergencia', sa.String(100), nullable=False, index=True),
        sa.Column('fecha_programada', sa.Date(), nullable=False, index=True),
        sa.Column('fecha_ejecutada', sa.Date(), nullable=True),
        sa.Column('hora_inicio', sa.String(20), nullable=True),
        sa.Column('hora_fin', sa.String(20), nullable=True),
        sa.Column('lugar', sa.String(255), nullable=True),
        sa.Column('total_participantes', sa.Integer(), default=0),
        sa.Column('tiempo_respuesta_minutos', sa.Integer(), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('resultado', sa.String(100), nullable=True),
        sa.Column('recomendaciones', sa.Text(), nullable=True),
        sa.Column('plan_mejora', sa.Text(), nullable=True),
        sa.Column('estado', sa.String(50), default='PROGRAMADO', index=True),
        sa.Column('evidencia_url', sa.String(500), nullable=True),
        sa.Column('archivo_id', sa.Integer(), sa.ForeignKey('archivos_sst.id', ondelete='SET NULL'), nullable=True),
        sa.Column('activo', sa.Boolean(), default=True),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        'amenazas_emergencia',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('empresa_id', sa.Integer(), sa.ForeignKey('empresas.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('tipo_amenaza', sa.String(100), nullable=False, index=True),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('probabilidad', sa.String(50), nullable=True),
        sa.Column('impacto', sa.String(50), nullable=True),
        sa.Column('nivel_riesgo', sa.String(50), nullable=True),
        sa.Column('medidas_prevencion', sa.Text(), nullable=True),
        sa.Column('medidas_control', sa.Text(), nullable=True),
        sa.Column('activo', sa.Boolean(), default=True),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        'inspecciones_emergencia',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('empresa_id', sa.Integer(), sa.ForeignKey('empresas.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True),
        sa.Column('codigo', sa.String(80), nullable=False, index=True),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('tipo_inspeccion', sa.String(100), nullable=False, index=True),
        sa.Column('fecha_inspeccion', sa.Date(), nullable=False, index=True),
        sa.Column('lugar', sa.String(255), nullable=True),
        sa.Column('estado_equipo', sa.String(50), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('hallazgos', sa.Text(), nullable=True),
        sa.Column('acciones_correctivas', sa.Text(), nullable=True),
        sa.Column('estado', sa.String(50), default='REALIZADA', index=True),
        sa.Column('evidencia_url', sa.String(500), nullable=True),
        sa.Column('archivo_id', sa.Integer(), sa.ForeignKey('archivos_sst.id', ondelete='SET NULL'), nullable=True),
        sa.Column('activo', sa.Boolean(), default=True),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    if 'brigadas_emergencia' not in sa.inspect(op.get_bind()).get_table_names():
        return
    op.drop_table('inspecciones_emergencia')
    op.drop_table('amenazas_emergencia')
    op.drop_table('simulacros_emergencia')
    op.drop_table('brigadas_integrantes_sst')
    op.drop_table('brigadas_emergencia')

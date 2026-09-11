"""Módulo Informe de Gestión SG-SST - 9 tablas nuevas

Revision ID: g3h4i5j6k7l8
Revises: 20260906_0002
Create Date: 2026-09-06
"""

from alembic import op
import sqlalchemy as sa

revision = "g3h4i5j6k7l8"
down_revision = "d9e0f1a2b3c4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = {t for t in inspector.get_table_names()}

    if "informes_gestion_sgsst" not in tables:
        op.create_table(
            "informes_gestion_sgsst",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True),
            sa.Column("responsable_sst_usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True),
            sa.Column("aprobado_por_usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
            sa.Column("sede_id", sa.Integer(), sa.ForeignKey("sedes.id", ondelete="SET NULL"), nullable=True, index=True),
            sa.Column("codigo", sa.String(50), unique=True, nullable=False, index=True),
            sa.Column("titulo", sa.String(255), nullable=False, server_default="INFORME ANUAL DE GESTIÓN SG-SST"),
            sa.Column("anio", sa.Integer(), nullable=False, index=True),
            sa.Column("periodo_evaluado", sa.String(100), nullable=True),
            sa.Column("fecha_inicio_periodo", sa.Date(), nullable=True),
            sa.Column("fecha_fin_periodo", sa.Date(), nullable=True),
            sa.Column("responsable_sst_nombre", sa.String(255), nullable=True),
            sa.Column("representante_legal_nombre", sa.String(255), nullable=True),
            sa.Column("version", sa.Integer(), default=1),
            sa.Column("estado", sa.String(50), default="BORRADOR", index=True),
            sa.Column("resumen_ejecutivo", sa.Text(), nullable=True),
            sa.Column("datos_consolidados", sa.JSON(), nullable=True),
            sa.Column("cumplimiento_global", sa.Numeric(5, 2), nullable=True),
            sa.Column("cumplimiento_plan_anual", sa.Numeric(5, 2), nullable=True),
            sa.Column("cumplimiento_estandares", sa.Numeric(5, 2), nullable=True),
            sa.Column("total_secciones", sa.Integer(), default=0),
            sa.Column("total_evidencias", sa.Integer(), default=0),
            sa.Column("total_recomendaciones", sa.Integer(), default=0),
            sa.Column("fecha_generacion", sa.DateTime(timezone=True), nullable=True),
            sa.Column("fecha_presentacion", sa.DateTime(timezone=True), nullable=True),
            sa.Column("fecha_aprobacion", sa.DateTime(timezone=True), nullable=True),
            sa.Column("fecha_cierre", sa.DateTime(timezone=True), nullable=True),
            sa.Column("codigo_documental", sa.String(100), nullable=True),
            sa.Column("hash_final_sha256", sa.String(128), nullable=True),
            sa.Column("activo", sa.Boolean(), default=True),
            sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if "informes_gestion_versiones" not in tables:
        op.create_table(
            "informes_gestion_versiones",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("informe_id", sa.Integer(), sa.ForeignKey("informes_gestion_sgsst.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("version_numero", sa.Integer(), nullable=False),
            sa.Column("estado_anterior", sa.String(50), nullable=True),
            sa.Column("estado_nuevo", sa.String(50), nullable=False),
            sa.Column("datos_snapshot", sa.JSON(), nullable=True),
            sa.Column("motivo_cambio", sa.Text(), nullable=True),
            sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
            sa.Column("activo", sa.Boolean(), default=True),
            sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if "informes_gestion_secciones" not in tables:
        op.create_table(
            "informes_gestion_secciones",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("informe_id", sa.Integer(), sa.ForeignKey("informes_gestion_sgsst.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("codigo_seccion", sa.String(50), nullable=False, index=True),
            sa.Column("nombre_seccion", sa.String(255), nullable=False),
            sa.Column("orden", sa.Integer(), default=0),
            sa.Column("datos_seccion", sa.JSON(), nullable=True),
            sa.Column("estado_seccion", sa.String(50), default="PENDIENTE"),
            sa.Column("observaciones", sa.Text(), nullable=True),
            sa.Column("activo", sa.Boolean(), default=True),
            sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if "informes_gestion_evidencias" not in tables:
        op.create_table(
            "informes_gestion_evidencias",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("informe_id", sa.Integer(), sa.ForeignKey("informes_gestion_sgsst.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("codigo_seccion", sa.String(50), nullable=True),
            sa.Column("nombre", sa.String(255), nullable=False),
            sa.Column("tipo_archivo", sa.String(50), nullable=False),
            sa.Column("tamano_bytes", sa.Integer(), nullable=True),
            sa.Column("hash_archivo", sa.String(128), nullable=True),
            sa.Column("archivo_url", sa.String(500), nullable=True),
            sa.Column("archivo_nombre_original", sa.String(255), nullable=True),
            sa.Column("modulo_origen", sa.String(100), nullable=True),
            sa.Column("registro_origen_id", sa.Integer(), nullable=True),
            sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
            sa.Column("activo", sa.Boolean(), default=True),
            sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if "informes_gestion_recomendaciones" not in tables:
        op.create_table(
            "informes_gestion_recomendaciones",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("informe_id", sa.Integer(), sa.ForeignKey("informes_gestion_sgsst.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("hallazgo", sa.Text(), nullable=False),
            sa.Column("riesgo", sa.Text(), nullable=True),
            sa.Column("recomendacion", sa.Text(), nullable=False),
            sa.Column("prioridad", sa.String(50), default="MEDIA"),
            sa.Column("accion_propuesta", sa.Text(), nullable=True),
            sa.Column("responsable_sugerido", sa.String(255), nullable=True),
            sa.Column("recursos_requeridos", sa.Text(), nullable=True),
            sa.Column("fecha_recomendada", sa.Date(), nullable=True),
            sa.Column("estado", sa.String(50), default="PENDIENTE"),
            sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
            sa.Column("activo", sa.Boolean(), default=True),
            sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if "informes_gestion_aprobaciones" not in tables:
        op.create_table(
            "informes_gestion_aprobaciones",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("informe_id", sa.Integer(), sa.ForeignKey("informes_gestion_sgsst.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
            sa.Column("tipo_accion", sa.String(50), nullable=False),
            sa.Column("resultado", sa.String(50), nullable=False),
            sa.Column("observaciones", sa.Text(), nullable=True),
            sa.Column("comentarios", sa.Text(), nullable=True),
            sa.Column("hash_firma", sa.String(128), nullable=True),
            sa.Column("activo", sa.Boolean(), default=True),
            sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if "rendiciones_cuentas" not in tables:
        op.create_table(
            "rendiciones_cuentas",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("informe_id", sa.Integer(), sa.ForeignKey("informes_gestion_sgsst.id", ondelete="CASCADE"), nullable=True, index=True),
            sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True),
            sa.Column("persona_nombre", sa.String(255), nullable=False),
            sa.Column("cargo", sa.String(255), nullable=True),
            sa.Column("rol_sgsst", sa.String(100), nullable=True),
            sa.Column("responsabilidad_asignada", sa.Text(), nullable=False),
            sa.Column("actividades", sa.Text(), nullable=True),
            sa.Column("meta", sa.Text(), nullable=True),
            sa.Column("resultado", sa.Text(), nullable=True),
            sa.Column("porcentaje_cumplimiento", sa.Numeric(5, 2), nullable=True),
            sa.Column("estado", sa.String(50), default="BORRADOR"),
            sa.Column("dificultades", sa.Text(), nullable=True),
            sa.Column("actividades_pendientes", sa.Text(), nullable=True),
            sa.Column("compromisos", sa.Text(), nullable=True),
            sa.Column("acciones_mejora", sa.Text(), nullable=True),
            sa.Column("fecha_evaluacion", sa.Date(), nullable=True),
            sa.Column("observaciones", sa.Text(), nullable=True),
            sa.Column("activo", sa.Boolean(), default=True),
            sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if "rendiciones_cuentas_responsabilidades" not in tables:
        op.create_table(
            "rendiciones_cuentas_responsabilidades",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("rendicion_id", sa.Integer(), sa.ForeignKey("rendiciones_cuentas.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("responsabilidad", sa.String(255), nullable=False),
            sa.Column("descripcion", sa.Text(), nullable=True),
            sa.Column("actividades_ejecutadas", sa.Text(), nullable=True),
            sa.Column("meta", sa.Text(), nullable=True),
            sa.Column("resultado_obtenido", sa.Text(), nullable=True),
            sa.Column("porcentaje_cumplimiento", sa.Numeric(5, 2), nullable=True),
            sa.Column("estado", sa.String(50), default="PENDIENTE"),
            sa.Column("evidencias", sa.Text(), nullable=True),
            sa.Column("fecha_cumplimiento", sa.Date(), nullable=True),
            sa.Column("activo", sa.Boolean(), default=True),
            sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = {t for t in inspector.get_table_names()}

    for table in [
        "rendiciones_cuentas_responsabilidades",
        "rendiciones_cuentas",
        "informes_gestion_aprobaciones",
        "informes_gestion_recomendaciones",
        "informes_gestion_evidencias",
        "informes_gestion_secciones",
        "informes_gestion_versiones",
        "informes_gestion_sgsst",
    ]:
        if table in tables:
            op.drop_table(table)

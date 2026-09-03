"""Crea la tabla de perfil sociodemográfico completo del empleado.

Revision ID: 0003_empleado_perfil_sociodemografico
Revises: 0002_empleado_demografico
Create Date: 2026-09-02 15:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_perfil_sociodemo"
down_revision = "0002_empleado_demografico"
branch_labels = None
depends_on = None


def _table_exists(bind, name: str) -> bool:
    return name in sa.inspect(bind).get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    if _table_exists(bind, "empleado_perfil_sociodemografico"):
        return

    op.create_table(
        "empleado_perfil_sociodemografico",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("empleado_id", sa.Integer(), nullable=False),
        # 1. Identificación
        sa.Column("nombres_completos", sa.String(255), nullable=True),
        sa.Column("tipo_documento", sa.String(20), nullable=True),
        sa.Column("numero_documento", sa.String(50), nullable=True),
        sa.Column("libreta_militar", sa.String(50), nullable=True),
        sa.Column("fecha_nacimiento", sa.Date(), nullable=True),
        sa.Column("lugar_nacimiento", sa.String(255), nullable=True),
        sa.Column("edad", sa.Integer(), nullable=True),
        sa.Column("raza_pertenencia_etnica", sa.String(100), nullable=True),
        sa.Column("telefono_celular", sa.String(50), nullable=True),
        # 2. Sociodemográficas
        sa.Column("estado_civil", sa.String(50), nullable=True),
        sa.Column("conyuge_nombre", sa.String(255), nullable=True),
        sa.Column("conyuge_ocupacion", sa.String(255), nullable=True),
        sa.Column("conyuge_edad", sa.Integer(), nullable=True),
        sa.Column("conyuge_celular", sa.String(50), nullable=True),
        sa.Column("numero_dependientes", sa.Integer(), nullable=True),
        sa.Column("hijos", sa.JSON(), nullable=True),
        # 3. Vivienda
        sa.Column("direccion_residencia", sa.String(500), nullable=True),
        sa.Column("barrio", sa.String(255), nullable=True),
        sa.Column("ciudad_municipio", sa.String(255), nullable=True),
        sa.Column("estrato_socioeconomico", sa.Integer(), nullable=True),
        sa.Column("tipo_vivienda", sa.String(50), nullable=True),
        sa.Column("servicios_vivienda", sa.JSON(), nullable=True),
        sa.Column("medio_transporte", sa.String(100), nullable=True),
        sa.Column("medio_transporte_otro", sa.String(255), nullable=True),
        sa.Column("tiempo_desplazamiento", sa.String(50), nullable=True),
        # 4. Laboral y formación
        sa.Column("cargo_actual", sa.String(255), nullable=True),
        sa.Column("area_departamento", sa.String(255), nullable=True),
        sa.Column("sede_centro_trabajo", sa.String(255), nullable=True),
        sa.Column("tipo_contrato", sa.String(100), nullable=True),
        sa.Column("tiempo_laborado", sa.String(100), nullable=True),
        sa.Column("antiguedad_cargo", sa.String(50), nullable=True),
        sa.Column("ultima_empresa", sa.String(255), nullable=True),
        sa.Column("nivel_escolaridad", sa.String(100), nullable=True),
        sa.Column("detalle_titulos", sa.String(500), nullable=True),
        # 5. Salud y hábitos
        sa.Column("eps_actual", sa.String(255), nullable=True),
        sa.Column("fondo_pensiones", sa.String(255), nullable=True),
        sa.Column("tipo_rh", sa.String(10), nullable=True),
        sa.Column("diagnostico_previo", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("diagnostico_detalle", sa.String(500), nullable=True),
        sa.Column("actividad_fisica", sa.String(10), nullable=True),
        sa.Column("consumo_cigarrillo", sa.String(50), nullable=True),
        sa.Column("consumo_alcohol", sa.String(50), nullable=True),
        sa.Column("talla_camisa", sa.String(10), nullable=True),
        sa.Column("talla_pantalon", sa.String(10), nullable=True),
        sa.Column("talla_chaqueta", sa.String(10), nullable=True),
        sa.Column("talla_overol", sa.String(10), nullable=True),
        sa.Column("talla_calzado", sa.String(10), nullable=True),
        # 6. Referencias
        sa.Column("referencia_1_nombre", sa.String(255), nullable=True),
        sa.Column("referencia_1_ocupacion", sa.String(255), nullable=True),
        sa.Column("referencia_1_telefono", sa.String(50), nullable=True),
        sa.Column("referencia_2_nombre", sa.String(255), nullable=True),
        sa.Column("referencia_2_ocupacion", sa.String(255), nullable=True),
        sa.Column("referencia_2_telefono", sa.String(50), nullable=True),
        # 7. Consentimiento
        sa.Column("consentimiento_informado", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("fecha_firma", sa.Date(), nullable=True),
        # Metadatos
        sa.Column("completado", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("fuente", sa.String(50), server_default=sa.text("'MANUAL'")),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["empleado_id"], ["empleados.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("empleado_id", name="uq_empleado_perfil_sociodemografico"),
    )
    op.create_index("ix_perfil_sociodemografico_id", "empleado_perfil_sociodemografico", ["id"])
    op.create_index("ix_perfil_sociodemografico_empresa_id", "empleado_perfil_sociodemografico", ["empresa_id"])
    op.create_index("ix_perfil_sociodemografico_empleado_id", "empleado_perfil_sociodemografico", ["empleado_id"])


def downgrade() -> None:
    bind = op.get_bind()
    if not _table_exists(bind, "empleado_perfil_sociodemografico"):
        return
    op.drop_index("ix_perfil_sociodemografico_empleado_id", table_name="empleado_perfil_sociodemografico")
    op.drop_index("ix_perfil_sociodemografico_empresa_id", table_name="empleado_perfil_sociodemografico")
    op.drop_index("ix_perfil_sociodemografico_id", table_name="empleado_perfil_sociodemografico")
    op.drop_table("empleado_perfil_sociodemografico")

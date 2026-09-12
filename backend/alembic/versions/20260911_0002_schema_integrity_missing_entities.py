"""
Corrección de integridad del esquema productivo.

Revision ID: j2k3l4m5n6o7
Revises: i1j2k3l4m5n6
Create Date: 2026-09-11

Corrige diferencias detectadas entre SQLAlchemy metadata
y PostgreSQL después del hardening de producción.

Crea:
- examenes_evaluacion_catalogo
- tipos_evaluacion_medica
- profesiograma
- profesiograma_evaluacion
- push_subscriptions

Agrega:
- cargos.requiere_vigilancia_medica
- cargos.riesgos_asociados
- epp_catalogo.ficha_tecnica_url
- epp_catalogo.ficha_tecnica_nombre
- epp_catalogo.ficha_tecnica_archivo_id
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# ------------------------------------------------------------------
# Alembic identifiers
# ------------------------------------------------------------------

revision: str = "j2k3l4m5n6o7"
down_revision: Union[str, Sequence[str], None] = "i1j2k3l4m5n6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(bind, table: str, column: str) -> bool:
    inspector = sa.inspect(bind)
    if table not in inspector.get_table_names():
        return False
    columns = {c["name"] for c in inspector.get_columns(table)}
    return column in columns


def _table_exists(bind, table: str) -> bool:
    inspector = sa.inspect(bind)
    return table in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()

    # ==============================================================
    # 1. CARGOS
    # ==============================================================

    if not _column_exists(bind, "cargos", "requiere_vigilancia_medica"):
        op.add_column(
            "cargos",
            sa.Column(
                "requiere_vigilancia_medica",
                sa.Boolean(),
                nullable=True,
            ),
        )

        op.create_index(
            "ix_cargos_requiere_vigilancia_medica",
            "cargos",
            ["requiere_vigilancia_medica"],
            unique=False,
        )

    if not _column_exists(bind, "cargos", "riesgos_asociados"):
        op.add_column(
            "cargos",
            sa.Column(
                "riesgos_asociados",
                sa.String(length=700),
                nullable=True,
            ),
        )

    # ==============================================================
    # 2. EPP CATALOGO
    # ==============================================================

    if not _column_exists(bind, "epp_catalogo", "ficha_tecnica_url"):
        op.add_column(
            "epp_catalogo",
            sa.Column(
                "ficha_tecnica_url",
                sa.String(length=500),
                nullable=True,
            ),
        )

    if not _column_exists(bind, "epp_catalogo", "ficha_tecnica_nombre"):
        op.add_column(
            "epp_catalogo",
            sa.Column(
                "ficha_tecnica_nombre",
                sa.String(length=255),
                nullable=True,
            ),
        )

    if not _column_exists(bind, "epp_catalogo", "ficha_tecnica_archivo_id"):
        op.add_column(
            "epp_catalogo",
            sa.Column(
                "ficha_tecnica_archivo_id",
                sa.Integer(),
                nullable=True,
            ),
        )

        op.create_foreign_key(
            "fk_epp_catalogo_ficha_tecnica_archivo_id_archivos_sst",
            "epp_catalogo",
            "archivos_sst",
            ["ficha_tecnica_archivo_id"],
            ["id"],
        )

    # ==============================================================
    # 3. TIPOS DE EVALUACION MEDICA
    # ==============================================================

    if not _table_exists(bind, "tipos_evaluacion_medica"):
        op.create_table(
            "tipos_evaluacion_medica",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("codigo", sa.String(length=50), nullable=False),
            sa.Column("nombre", sa.String(length=150), nullable=False),
            sa.Column("descripcion", sa.Text(), nullable=True),
            sa.Column("activo", sa.Boolean(), nullable=False),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.PrimaryKeyConstraint("id"),
        )

        op.create_index(
            "ix_tipos_evaluacion_medica_codigo",
            "tipos_evaluacion_medica",
            ["codigo"],
            unique=True,
        )

        op.create_index(
            "ix_tipos_evaluacion_medica_id",
            "tipos_evaluacion_medica",
            ["id"],
            unique=False,
        )

    # ==============================================================
    # 4. EXAMENES POR EVALUACION - CATALOGO
    # ==============================================================

    if not _table_exists(bind, "examenes_evaluacion_catalogo"):
        op.create_table(
            "examenes_evaluacion_catalogo",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("codigo", sa.String(length=50), nullable=False),
            sa.Column("nombre", sa.String(length=200), nullable=False),
            sa.Column("descripcion", sa.Text(), nullable=True),
            sa.Column("activo", sa.Boolean(), nullable=False),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.PrimaryKeyConstraint("id"),
        )

        op.create_index(
            "ix_examenes_evaluacion_catalogo_codigo",
            "examenes_evaluacion_catalogo",
            ["codigo"],
            unique=True,
        )

        op.create_index(
            "ix_examenes_evaluacion_catalogo_id",
            "examenes_evaluacion_catalogo",
            ["id"],
            unique=False,
        )

    # ==============================================================
    # 5. PROFESIOGRAMA
    # ==============================================================

    if not _table_exists(bind, "profesiograma"):
        op.create_table(
            "profesiograma",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("cargo_id", sa.Integer(), nullable=False),
            sa.Column("empresa_id", sa.Integer(), nullable=False),
            sa.Column("riesgos_asociados", sa.Text(), nullable=True),
            sa.Column("activo", sa.Boolean(), nullable=False),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.Column(
                "fecha_actualizacion",
                sa.DateTime(),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.ForeignKeyConstraint(
                ["cargo_id"],
                ["cargos.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["empresa_id"],
                ["empresas.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
        )

        op.create_index(
            "ix_profesiograma_cargo_id",
            "profesiograma",
            ["cargo_id"],
            unique=True,
        )

        op.create_index(
            "ix_profesiograma_empresa_id",
            "profesiograma",
            ["empresa_id"],
            unique=False,
        )

        op.create_index(
            "ix_profesiograma_id",
            "profesiograma",
            ["id"],
            unique=False,
        )

    # ==============================================================
    # 6. PROFESIOGRAMA - EVALUACIONES
    # ==============================================================

    if not _table_exists(bind, "profesiograma_evaluacion"):
        op.create_table(
            "profesiograma_evaluacion",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("profesiograma_id", sa.Integer(), nullable=False),
            sa.Column("tipo_evaluacion_id", sa.Integer(), nullable=False),
            sa.Column("examenes_requeridos", sa.Text(), nullable=True),
            sa.Column("activo", sa.Boolean(), nullable=False),
            sa.ForeignKeyConstraint(
                ["profesiograma_id"],
                ["profesiograma.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["tipo_evaluacion_id"],
                ["tipos_evaluacion_medica.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "profesiograma_id",
                "tipo_evaluacion_id",
                name="uq_profesiograma_tipo_eval",
            ),
        )

        op.create_index(
            "ix_profesiograma_evaluacion_id",
            "profesiograma_evaluacion",
            ["id"],
            unique=False,
        )

        op.create_index(
            "ix_profesiograma_evaluacion_profesiograma_id",
            "profesiograma_evaluacion",
            ["profesiograma_id"],
            unique=False,
        )

    # ==============================================================
    # 7. PUSH SUBSCRIPTIONS
    # ==============================================================

    if not _table_exists(bind, "push_subscriptions"):
        op.create_table(
            "push_subscriptions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("empresa_id", sa.Integer(), nullable=False),
            sa.Column("usuario_id", sa.Integer(), nullable=False),
            sa.Column("endpoint", sa.Text(), nullable=False),
            sa.Column("p256dh", sa.Text(), nullable=False),
            sa.Column("auth", sa.Text(), nullable=False),
            sa.Column("activo", sa.Boolean(), nullable=False),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.Column(
                "fecha_actualizacion",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
            sa.ForeignKeyConstraint(
                ["empresa_id"],
                ["empresas.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["usuario_id"],
                ["usuarios.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("endpoint"),
        )

        op.create_index(
            "ix_push_subscriptions_activo",
            "push_subscriptions",
            ["activo"],
            unique=False,
        )

        op.create_index(
            "ix_push_subscriptions_empresa_id",
            "push_subscriptions",
            ["empresa_id"],
            unique=False,
        )

        op.create_index(
            "ix_push_subscriptions_id",
            "push_subscriptions",
            ["id"],
            unique=False,
        )

        op.create_index(
            "ix_push_subscriptions_usuario_id",
            "push_subscriptions",
            ["usuario_id"],
            unique=False,
        )


def downgrade() -> None:
    # ==============================================================
    # PUSH SUBSCRIPTIONS
    # ==============================================================

    op.drop_index(
        "ix_push_subscriptions_usuario_id",
        table_name="push_subscriptions",
    )
    op.drop_index(
        "ix_push_subscriptions_id",
        table_name="push_subscriptions",
    )
    op.drop_index(
        "ix_push_subscriptions_empresa_id",
        table_name="push_subscriptions",
    )
    op.drop_index(
        "ix_push_subscriptions_activo",
        table_name="push_subscriptions",
    )
    op.drop_table("push_subscriptions")

    # ==============================================================
    # PROFESIOGRAMA EVALUACION
    # ==============================================================

    op.drop_index(
        "ix_profesiograma_evaluacion_profesiograma_id",
        table_name="profesiograma_evaluacion",
    )
    op.drop_index(
        "ix_profesiograma_evaluacion_id",
        table_name="profesiograma_evaluacion",
    )
    op.drop_table("profesiograma_evaluacion")

    # ==============================================================
    # PROFESIOGRAMA
    # ==============================================================

    op.drop_index(
        "ix_profesiograma_id",
        table_name="profesiograma",
    )
    op.drop_index(
        "ix_profesiograma_empresa_id",
        table_name="profesiograma",
    )
    op.drop_index(
        "ix_profesiograma_cargo_id",
        table_name="profesiograma",
    )
    op.drop_table("profesiograma")

    # ==============================================================
    # CATALOGOS MEDICOS
    # ==============================================================

    op.drop_index(
        "ix_examenes_evaluacion_catalogo_id",
        table_name="examenes_evaluacion_catalogo",
    )
    op.drop_index(
        "ix_examenes_evaluacion_catalogo_codigo",
        table_name="examenes_evaluacion_catalogo",
    )
    op.drop_table("examenes_evaluacion_catalogo")

    op.drop_index(
        "ix_tipos_evaluacion_medica_id",
        table_name="tipos_evaluacion_medica",
    )
    op.drop_index(
        "ix_tipos_evaluacion_medica_codigo",
        table_name="tipos_evaluacion_medica",
    )
    op.drop_table("tipos_evaluacion_medica")

    # ==============================================================
    # EPP CATALOGO
    # ==============================================================

    op.drop_constraint(
        "fk_epp_catalogo_ficha_tecnica_archivo_id_archivos_sst",
        "epp_catalogo",
        type_="foreignkey",
    )

    op.drop_column(
        "epp_catalogo",
        "ficha_tecnica_archivo_id",
    )
    op.drop_column(
        "epp_catalogo",
        "ficha_tecnica_nombre",
    )
    op.drop_column(
        "epp_catalogo",
        "ficha_tecnica_url",
    )

    # ==============================================================
    # CARGOS
    # ==============================================================

    op.drop_column(
        "cargos",
        "riesgos_asociados",
    )

    op.drop_index(
        "ix_cargos_requiere_vigilancia_medica",
        table_name="cargos",
    )

    op.drop_column(
        "cargos",
        "requiere_vigilancia_medica",
    )
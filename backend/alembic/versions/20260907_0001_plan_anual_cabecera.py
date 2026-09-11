"""Plan Anual Cabecera - Nueva tabla + FK en actividades + migración datos

Revision ID: h8i9j0k1l2m3
Revises: g3h4i5j6k7l8
Create Date: 2026-09-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision = "h8i9j0k1l2m3"
down_revision = "g3h4i5j6k7l8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = {t for t in inspector.get_table_names()}
    columns_plan_anual = {c["name"] for c in inspector.get_columns("plan_anual_sst")} if "plan_anual_sst" in tables else set()

    # 1. Crear tabla plan_anual_cabecera
    if "plan_anual_cabecera" not in tables:
        op.create_table(
            "plan_anual_cabecera",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
            sa.Column("vigencia", sa.String(4), nullable=False, index=True),
            sa.Column("alcance", sa.Text(), nullable=True),
            sa.Column("objetivo_general", sa.Text(), nullable=True),
            sa.Column("meta_general", sa.Text(), nullable=True),
            sa.Column("representante_legal_nombre", sa.String(255), nullable=True),
            sa.Column("representante_legal_cargo", sa.String(255), nullable=True),
            sa.Column("responsable_sst_nombre", sa.String(255), nullable=True),
            sa.Column("responsable_sst_cargo", sa.String(255), nullable=True),
            sa.Column("activo", sa.Boolean(), default=True, nullable=False),
            sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
            sa.UniqueConstraint("empresa_id", "vigencia", name="uq_plan_anual_cabecera_empresa_vigencia"),
        )

    # 2. Agregar columna plan_anual_cabecera_id a plan_anual_sst
    if "plan_anual_cabecera_id" not in columns_plan_anual:
        op.add_column("plan_anual_sst", sa.Column("plan_anual_cabecera_id", sa.Integer(), sa.ForeignKey("plan_anual_cabecera.id", ondelete="CASCADE"), nullable=True, index=True))

    # 3. Migrar datos existentes: crear cabeceras por (empresa_id, vigencia) y vincular actividades
    # Solo migrar si la tabla tiene las columnas antiguas (vigencia, alcance, objetivo_general, etc.)
    old_columns = {"vigencia", "alcance", "objetivo_general", "representante_legal_nombre", "representante_legal_cargo", "responsable_sst_nombre", "responsable_sst_cargo"}
    if "plan_anual_sst" in tables and old_columns.issubset(columns_plan_anual):
        # Obtener combinaciones únicas de empresa_id y vigencia
        result = bind.execute(text("""
            SELECT DISTINCT empresa_id, COALESCE(vigencia, EXTRACT(YEAR FROM fecha_creacion)::text) as vigencia
            FROM plan_anual_sst
            WHERE activo = true
        """))
        
        for row in result:
            empresa_id, vigencia = row
            # Verificar si ya existe cabecera para esta empresa/vigencia
            exists = bind.execute(text("""
                SELECT id FROM plan_anual_cabecera 
                WHERE empresa_id = :empresa_id AND vigencia = :vigencia
            """), {"empresa_id": empresa_id, "vigencia": vigencia}).fetchone()
            
            if not exists:
                # Crear cabecera
                cabecera_result = bind.execute(text("""
                    INSERT INTO plan_anual_cabecera (empresa_id, vigencia, alcance, objetivo_general, meta_general, activo, fecha_creacion, fecha_actualizacion)
                    VALUES (:empresa_id, :vigencia, :alcance, :objetivo_general, :meta_general, true, NOW(), NOW())
                    RETURNING id
                """), {
                    "empresa_id": empresa_id,
                    "vigencia": vigencia,
                    "alcance": "Alcance general del SG-SST para la vigencia " + vigencia,
                    "objetivo_general": "Mejorar continuamente el desempeño en SST",
                    "meta_general": "Cumplir 100% de actividades programadas",
                })
                cabecera_id = cabecera_result.scalar()
            else:
                cabecera_id = exists[0]
            
            # Vincular actividades a la cabecera
            bind.execute(text("""
                UPDATE plan_anual_sst 
                SET plan_anual_cabecera_id = :cabecera_id
                WHERE empresa_id = :empresa_id 
                AND (plan_anual_cabecera_id IS NULL)
                AND activo = true
            """), {"cabecera_id": cabecera_id, "empresa_id": empresa_id})


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = {t for t in inspector.get_table_names()}
    columns_plan_anual = {c["name"] for c in inspector.get_columns("plan_anual_sst")} if "plan_anual_sst" in tables else set()

    # Eliminar FK y columna
    if "plan_anual_cabecera_id" in columns_plan_anual:
        # Buscar nombre de la FK
        fks = inspector.get_foreign_keys("plan_anual_sst")
        for fk in fks:
            if "plan_anual_cabecera_id" in fk["constrained_columns"]:
                op.drop_constraint(fk["name"], "plan_anual_sst", type_="foreignkey")
                break
        op.drop_column("plan_anual_sst", "plan_anual_cabecera_id")

    # Eliminar tabla cabecera
    if "plan_anual_cabecera" in tables:
        op.drop_table("plan_anual_cabecera")
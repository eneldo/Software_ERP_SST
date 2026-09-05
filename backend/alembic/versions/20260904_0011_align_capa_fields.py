"""align CAPA model with corrective measures schemas

Revision ID: e1f2a3b4c5d6
Revises: d0e1f2a3b4c5
Create Date: 2026-09-04 20:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "e1f2a3b4c5d6"
down_revision = "d0e1f2a3b4c5"
branch_labels = None
depends_on = None


def _agregar_si_falta(tabla: str, columna: sa.Column) -> None:
    existentes = {item["name"] for item in sa.inspect(op.get_bind()).get_columns(tabla)}
    if columna.name not in existentes:
        op.add_column(tabla, columna)


def upgrade() -> None:
    _agregar_si_falta("capas_sst", sa.Column("ishikawa_json", sa.Text(), nullable=True))
    _agregar_si_falta("capas_sst", sa.Column("costo_estimado", sa.Numeric(14, 2), nullable=False, server_default="0"))
    _agregar_si_falta("capas_sst", sa.Column("costo_real", sa.Numeric(14, 2), nullable=False, server_default="0"))
    _agregar_si_falta("capas_sst", sa.Column("requiere_aprobacion", sa.Boolean(), nullable=False, server_default=sa.false()))
    _agregar_si_falta("capas_sst", sa.Column("aprobada_por", sa.Integer(), nullable=True))
    _agregar_si_falta("capas_sst", sa.Column("fecha_aprobacion", sa.DateTime(timezone=True), nullable=True))
    columnas = {item["name"] for item in sa.inspect(op.get_bind()).get_columns("capas_sst")}
    claves = sa.inspect(op.get_bind()).get_foreign_keys("capas_sst")
    tiene_fk_aprobador = any(fk["constrained_columns"] == ["aprobada_por"] for fk in claves)
    if "aprobada_por" in columnas and not tiene_fk_aprobador:
        op.create_foreign_key(
            "fk_capas_sst_aprobada_por_usuarios",
            "capas_sst",
            "usuarios",
            ["aprobada_por"],
            ["id"],
            ondelete="SET NULL",
        )
    _agregar_si_falta("capas_seguimientos_sst", sa.Column("proxima_accion", sa.Text(), nullable=True))
    _agregar_si_falta("capas_seguimientos_sst", sa.Column("fecha_proximo_seguimiento", sa.Date(), nullable=True))


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    seguimiento = {item["name"] for item in inspector.get_columns("capas_seguimientos_sst")}
    for nombre in ("fecha_proximo_seguimiento", "proxima_accion"):
        if nombre in seguimiento:
            op.drop_column("capas_seguimientos_sst", nombre)
    capas = {item["name"] for item in inspector.get_columns("capas_sst")}
    claves = {fk["name"] for fk in inspector.get_foreign_keys("capas_sst")}
    if "fk_capas_sst_aprobada_por_usuarios" in claves:
        op.drop_constraint("fk_capas_sst_aprobada_por_usuarios", "capas_sst", type_="foreignkey")
    for nombre in (
        "fecha_aprobacion",
        "aprobada_por",
        "requiere_aprobacion",
        "costo_real",
        "costo_estimado",
        "ishikawa_json",
    ):
        if nombre in capas:
            op.drop_column("capas_sst", nombre)

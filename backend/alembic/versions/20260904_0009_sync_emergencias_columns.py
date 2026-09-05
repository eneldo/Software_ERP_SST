"""sync emergency evidence and findings columns

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-09-04 18:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "c9d0e1f2a3b4"
down_revision = "b8c9d0e1f2a3"
branch_labels = None
depends_on = None


def _columnas(tabla: str) -> set[str]:
    return {columna["name"] for columna in sa.inspect(op.get_bind()).get_columns(tabla)}


def _eliminar_fk_archivo(tabla: str) -> None:
    for clave in sa.inspect(op.get_bind()).get_foreign_keys(tabla):
        if clave.get("constrained_columns") == ["archivo_id"] and clave.get("name"):
            op.drop_constraint(clave["name"], tabla, type_="foreignkey")
            return


def upgrade() -> None:
    tablas = sa.inspect(op.get_bind()).get_table_names()
    if "simulacros_emergencia" in tablas:
        existentes = _columnas("simulacros_emergencia")
        if "observaciones" not in existentes:
            op.add_column("simulacros_emergencia", sa.Column("observaciones", sa.Text(), nullable=True))
        if "evidencia_url" not in existentes:
            op.add_column("simulacros_emergencia", sa.Column("evidencia_url", sa.String(500), nullable=True))
        if "archivo_id" not in existentes:
            op.add_column("simulacros_emergencia", sa.Column("archivo_id", sa.Integer(), nullable=True))
            op.create_foreign_key(
                "fk_simulacros_emergencia_archivo_id",
                "simulacros_emergencia",
                "archivos_sst",
                ["archivo_id"],
                ["id"],
                ondelete="SET NULL",
            )

    if "inspecciones_emergencia" in tablas:
        existentes = _columnas("inspecciones_emergencia")
        for nombre in ("hallazgos", "acciones_correctivas"):
            if nombre not in existentes:
                op.add_column("inspecciones_emergencia", sa.Column(nombre, sa.Text(), nullable=True))
        if "evidencia_url" not in existentes:
            op.add_column("inspecciones_emergencia", sa.Column("evidencia_url", sa.String(500), nullable=True))
        if "archivo_id" not in existentes:
            op.add_column("inspecciones_emergencia", sa.Column("archivo_id", sa.Integer(), nullable=True))
            op.create_foreign_key(
                "fk_inspecciones_emergencia_archivo_id",
                "inspecciones_emergencia",
                "archivos_sst",
                ["archivo_id"],
                ["id"],
                ondelete="SET NULL",
            )


def downgrade() -> None:
    tablas = sa.inspect(op.get_bind()).get_table_names()
    if "inspecciones_emergencia" in tablas:
        existentes = _columnas("inspecciones_emergencia")
        if "archivo_id" in existentes:
            _eliminar_fk_archivo("inspecciones_emergencia")
            op.drop_column("inspecciones_emergencia", "archivo_id")
        for nombre in ("evidencia_url", "acciones_correctivas", "hallazgos"):
            if nombre in existentes:
                op.drop_column("inspecciones_emergencia", nombre)

    if "simulacros_emergencia" in tablas:
        existentes = _columnas("simulacros_emergencia")
        if "archivo_id" in existentes:
            _eliminar_fk_archivo("simulacros_emergencia")
            op.drop_column("simulacros_emergencia", "archivo_id")
        for nombre in ("evidencia_url", "observaciones"):
            if nombre in existentes:
                op.drop_column("simulacros_emergencia", nombre)

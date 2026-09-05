"""complete company and job profile fields

Revision ID: d0e1f2a3b4c5
Revises: c9d0e1f2a3b4
Create Date: 2026-09-04 19:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "d0e1f2a3b4c5"
down_revision = "c9d0e1f2a3b4"
branch_labels = None
depends_on = None


def _agregar_si_falta(tabla: str, columna: sa.Column) -> None:
    existentes = {item["name"] for item in sa.inspect(op.get_bind()).get_columns(tabla)}
    if columna.name not in existentes:
        op.add_column(tabla, columna)


def upgrade() -> None:
    _agregar_si_falta("empresas", sa.Column("digito_verificacion", sa.String(1), nullable=True))
    _agregar_si_falta("empresas", sa.Column("responsable_sst", sa.String(255), nullable=True))
    for nombre, longitud in (
        ("funciones", 2000),
        ("responsabilidades", 2000),
        ("habilidades", 1000),
        ("requisitos_tecnicos", 1000),
        ("requisitos_fisicos", 1000),
        ("requisitos_mentales", 1000),
    ):
        _agregar_si_falta("cargos", sa.Column(nombre, sa.String(longitud), nullable=True))


def downgrade() -> None:
    columnas_cargo = {item["name"] for item in sa.inspect(op.get_bind()).get_columns("cargos")}
    for nombre in (
        "requisitos_mentales",
        "requisitos_fisicos",
        "requisitos_tecnicos",
        "habilidades",
        "responsabilidades",
        "funciones",
    ):
        if nombre in columnas_cargo:
            op.drop_column("cargos", nombre)
    columnas_empresa = {item["name"] for item in sa.inspect(op.get_bind()).get_columns("empresas")}
    for nombre in ("responsable_sst", "digito_verificacion"):
        if nombre in columnas_empresa:
            op.drop_column("empresas", nombre)

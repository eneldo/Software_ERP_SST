"""H-011: Evaluación psicosocial + Historia clínica ocupacional

Revision ID: 20260905_0009
Revises: 20260905_0008
Create Date: 2026-09-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "20260905_0009"
down_revision = "20260905_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = inspect(conn)

    # ── Tabla evaluaciones psicosociales ─────────────────────
    if "evaluaciones_psicosociales_sst" not in insp.get_table_names():
        op.create_table(
            "evaluaciones_psicosociales_sst",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("empresa_id", sa.Integer, sa.ForeignKey("empresas.id"), nullable=False, index=True),
            sa.Column("empleado_id", sa.Integer, sa.ForeignKey("empleados.id"), nullable=False, index=True),
            sa.Column("fecha_evaluacion", sa.DateTime, nullable=False, server_default=sa.func.now()),
            sa.Column("periodo", sa.String(20), nullable=True),
            sa.Column("evaluador", sa.String(200), nullable=True),
            sa.Column("puntaje_total", sa.Float, nullable=True),
            sa.Column("nivel_riesgo", sa.String(30), nullable=True),
            sa.Column("conclusiones", sa.Text, nullable=True),
            sa.Column("recomendaciones", sa.Text, nullable=True),
            sa.Column("activo", sa.Boolean, nullable=False, server_default=sa.text("true")),
            sa.Column("fecha_creacion", sa.DateTime, server_default=sa.func.now()),
            sa.Column("fecha_actualizacion", sa.DateTime, server_default=sa.func.now()),
        )

    # ── Tabla factores psicosociales ─────────────────────────
    if "factores_psicosociales_sst" not in insp.get_table_names():
        op.create_table(
            "factores_psicosociales_sst",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("evaluacion_id", sa.Integer, sa.ForeignKey("evaluaciones_psicosociales_sst.id"), nullable=False, index=True),
            sa.Column("factor", sa.String(100), nullable=False),
            sa.Column("dominio", sa.String(50), nullable=True),
            sa.Column("puntuacion", sa.Float, nullable=True),
            sa.Column("nivel_riesgo", sa.String(30), nullable=True),
            sa.Column("observacion", sa.Text, nullable=True),
            sa.Column("activo", sa.Boolean, nullable=False, server_default=sa.text("true")),
            sa.Column("fecha_creacion", sa.DateTime, server_default=sa.func.now()),
        )

    # ── Tabla historia clínica ocupacional ────────────────────
    if "historias_clinicas_ocupacionales" not in insp.get_table_names():
        op.create_table(
            "historias_clinicas_ocupacionales",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("empresa_id", sa.Integer, sa.ForeignKey("empresas.id"), nullable=False, index=True),
            sa.Column("empleado_id", sa.Integer, sa.ForeignKey("empleados.id"), nullable=False, index=True),
            sa.Column("examen_medico_id", sa.Integer, sa.ForeignKey("examenes_medicos.id"), nullable=True, index=True),
            sa.Column("fecha_elaboracion", sa.DateTime, nullable=False, server_default=sa.func.now()),
            sa.Column("medico_cargo", sa.String(200), nullable=True),
            sa.Column("profesiograma_id", sa.Integer, nullable=True),
            sa.Column("motivo_consulta", sa.Text, nullable=True),
            sa.Column("antecedentes_personales", sa.Text, nullable=True),
            sa.Column("antecedentes_familiares", sa.Text, nullable=True),
            sa.Column("antecedentes_ocupacionales", sa.Text, nullable=True),
            sa.Column("antecedentes_patologicos", sa.Text, nullable=True),
            sa.Column("revision_cabeza", sa.Text, nullable=True),
            sa.Column("revision_ojos", sa.Text, nullable=True),
            sa.Column("revision_oidos", sa.Text, nullable=True),
            sa.Column("revision_nariz", sa.Text, nullable=True),
            sa.Column("revision_garganta", sa.Text, nullable=True),
            sa.Column("revision_cardiovascular", sa.Text, nullable=True),
            sa.Column("revision_respiratorio", sa.Text, nullable=True),
            sa.Column("revision_digestivo", sa.Text, nullable=True),
            sa.Column("revision_genitourinario", sa.Text, nullable=True),
            sa.Column("revision_musculoesqueletico", sa.Text, nullable=True),
            sa.Column("revision_neurologico", sa.Text, nullable=True),
            sa.Column("revision_piel", sa.Text, nullable=True),
            sa.Column("revision_psiquiatrico", sa.Text, nullable=True),
            sa.Column("signos_vitales", sa.Text, nullable=True),
            sa.Column("examen_fisico_general", sa.Text, nullable=True),
            sa.Column("examen_cabeza_cuello", sa.Text, nullable=True),
            sa.Column("examen_torax", sa.Text, nullable=True),
            sa.Column("examen_abdomen", sa.Text, nullable=True),
            sa.Column("examen_extremidades", sa.Text, nullable=True),
            sa.Column("examen_neurologico", sa.Text, nullable=True),
            sa.Column("cargo_actual", sa.String(200), nullable=True),
            sa.Column("fecha_ingreso", sa.DateTime, nullable=True),
            sa.Column("tiempo_exposicion", sa.String(50), nullable=True),
            sa.Column("factores_riesgo", sa.Text, nullable=True),
            sa.Column("controles_expuestos", sa.Text, nullable=True),
            sa.Column("elementos_proteccion", sa.Text, nullable=True),
            sa.Column("diagnostico", sa.Text, nullable=True),
            sa.Column("cie10", sa.String(20), nullable=True),
            sa.Column("plan_accion", sa.Text, nullable=True),
            sa.Column("concepto_medico", sa.Text, nullable=True),
            sa.Column("aptitud", sa.String(50), nullable=True),
            sa.Column("restricciones_laborales", sa.Text, nullable=True),
            sa.Column("recomendaciones", sa.Text, nullable=True),
            sa.Column("proximo_control", sa.DateTime, nullable=True),
            sa.Column("observaciones_seguimiento", sa.Text, nullable=True),
            sa.Column("consentimiento_obtenido", sa.Boolean, nullable=False, server_default=sa.text("false")),
            sa.Column("fecha_consentimiento", sa.DateTime, nullable=True),
            sa.Column("activo", sa.Boolean, nullable=False, server_default=sa.text("true")),
            sa.Column("fecha_creacion", sa.DateTime, server_default=sa.func.now()),
            sa.Column("fecha_actualizacion", sa.DateTime, server_default=sa.func.now()),
        )


def downgrade() -> None:
    op.drop_table("historias_clinicas_ocupacionales", if_exists=True)
    op.drop_table("factores_psicosociales_sst", if_exists=True)
    op.drop_table("evaluaciones_psicosociales_sst", if_exists=True)

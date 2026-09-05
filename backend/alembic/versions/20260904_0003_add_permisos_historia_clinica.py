"""add permisos historia clinica y concepto medico

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-09-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO permisos (codigo, nombre, modulo, descripcion, activo, fecha_creacion)
        VALUES 
            ('HISTORIA_CLINICA_ACCEDER', 'Acceder historia clinica', 'MEDICINA_LABORAL', 
             'Permite acceder a informacion clinica detallada (restricciones, observaciones, diagnosticos). Solo personal medico autorizado.', 
             true, NOW()),
            ('CONCEPTO_MEDICO_VER', 'Ver concepto medico', 'MEDICINA_LABORAL', 
             'Permite ver el concepto de aptitud (APTO/NO_APTO) sin acceso a detalle clinico.', 
             true, NOW())
        ON CONFLICT (codigo) DO NOTHING;
    """)


def downgrade() -> None:
    op.execute("DELETE FROM permisos WHERE codigo IN ('HISTORIA_CLINICA_ACCEDER', 'CONCEPTO_MEDICO_VER');")

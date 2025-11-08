"""Eliminar campos de la tabla vacunacion

Revision ID: aa0a1981a48a
Revises: 001
Create Date: 2025-11-08
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'aa0a1981a48a'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('vacunacion', 'nombre_animal')
    op.drop_column('vacunacion', 'fecha_inicio')
    op.drop_column('vacunacion', 'fecha_fin')


def downgrade():
    op.add_column('vacunacion', sa.Column('nombre_animal', sa.String(50)))
    op.add_column('vacunacion', sa.Column('fecha_inicio', sa.DateTime))
    op.add_column('vacunacion', sa.Column('fecha_fin', sa.DateTime))

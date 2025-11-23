"""Agregar campos de baja lógica para ganado

Revision ID: 002_baja_ganado
Revises: aa0a1981a48a
Create Date: 2025-01-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '002_baja_ganado'
down_revision = 'aa0a1981a48a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ganado', sa.Column('estado_baja', sa.Enum('activo', 'dado_de_baja', name='estado_baja'), nullable=False, server_default='activo'))
    op.add_column('ganado', sa.Column('causa_baja', sa.String(length=255), nullable=True))
    op.add_column('ganado', sa.Column('fecha_baja', sa.Date(), nullable=True))
    op.add_column('ganado', sa.Column('observaciones_baja', sa.Text(), nullable=True))
    
    # Actualizar registros existentes
    op.execute("UPDATE ganado SET estado_baja = 'activo' WHERE estado_baja IS NULL")


def downgrade():
    op.drop_column('ganado', 'observaciones_baja')
    op.drop_column('ganado', 'fecha_baja')
    op.drop_column('ganado', 'causa_baja')
    op.drop_column('ganado', 'estado_baja')


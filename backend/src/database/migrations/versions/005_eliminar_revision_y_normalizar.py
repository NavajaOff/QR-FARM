"""Eliminar tabla revision y normalizar a 3FN

Revision ID: 005_eliminar_revision_y_normalizar
Revises: 004_multi_tenant
Create Date: 2025-12-04
"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005_eliminar_revision'
down_revision: str = '004_multi_tenant'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Elimina la tabla revision y el campo id_revision de ganado."""
    # Primero eliminar la foreign key constraint si existe
    try:
        op.drop_constraint('ganado_ibfk_3', 'ganado', type_='foreignkey')
    except Exception:
        # La constraint puede no existir o tener otro nombre
        pass
    
    # Eliminar el índice de id_revision si existe
    try:
        op.drop_index('id_revision', table_name='ganado')
    except Exception:
        # El índice puede no existir
        pass
    
    # Eliminar la columna id_revision de la tabla ganado
    try:
        op.drop_column('ganado', 'id_revision')
    except Exception:
        # La columna puede no existir
        pass
    
    # Eliminar la tabla revision
    try:
        op.drop_table('revision')
    except Exception:
        # La tabla puede no existir
        pass


def downgrade() -> None:
    """Revierte los cambios, recreando la tabla revision y el campo id_revision."""
    # Recrear la tabla revision
    op.create_table(
        'revision',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('control', sa.DateTime),
        sa.Column('visita', sa.DateTime),
        sa.Column('tenant_id', sa.Integer, sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=True)
    )
    
    # Recrear la columna id_revision en ganado
    op.add_column('ganado', sa.Column('id_revision', sa.Integer, nullable=True))
    
    # Recrear el índice
    op.create_index('id_revision', 'ganado', ['id_revision'])
    
    # Recrear la foreign key
    op.create_foreign_key('ganado_ibfk_3', 'ganado', 'revision', ['id_revision'], ['id'])


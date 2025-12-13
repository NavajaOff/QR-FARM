"""Crear tabla historial_cambios para auditoría de cambios.

Revision ID: 011_crear_historial_cambios
Revises: 010_agregar_cargos
Create Date: 2025-01-XX
"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '011_crear_historial_cambios'
down_revision: str | Sequence[str] | None = '010_agregar_cargos'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _crear_tabla_historial_cambios(inspector: sa.Inspector) -> None:
    """Crea la tabla historial_cambios si no existe."""
    tables = inspector.get_table_names()
    if 'historial_cambios' not in tables:
        op.create_table(
            'historial_cambios',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
            sa.Column('tenant_id', sa.Integer, sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=True),
            sa.Column('usuario_id', sa.Integer, sa.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True),
            sa.Column('entidad_tipo', sa.String(50), nullable=False),
            sa.Column('entidad_id', sa.Integer, nullable=True),
            sa.Column('accion', sa.String(50), nullable=False),
            sa.Column('datos_anteriores', sa.JSON, nullable=True),
            sa.Column('datos_nuevos', sa.JSON, nullable=True),
            sa.Column('descripcion', sa.Text, nullable=True),
            sa.Column('fecha_cambio', sa.DateTime, server_default=sa.func.current_timestamp(), nullable=False),
            sa.Index('idx_historial_tenant', 'tenant_id'),
            sa.Index('idx_historial_usuario', 'usuario_id'),
            sa.Index('idx_historial_entidad', 'entidad_tipo', 'entidad_id'),
            sa.Index('idx_historial_fecha', 'fecha_cambio')
        )


def upgrade() -> None:
    """Crear tabla historial_cambios."""
    inspector = sa.inspect(op.get_bind())
    _crear_tabla_historial_cambios(inspector)


def downgrade() -> None:
    """Revertir cambios."""
    inspector = sa.inspect(op.get_bind())
    
    # Eliminar tabla historial_cambios
    if 'historial_cambios' in inspector.get_table_names():
        op.drop_table('historial_cambios')

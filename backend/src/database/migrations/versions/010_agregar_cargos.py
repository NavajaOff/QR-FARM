"""Agregar tabla cargos y campo cargo_id a personas.

Revision ID: 010_agregar_cargos
Revises: 009_make_expires_at_nullable
Create Date: 2025-01-XX
"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '010_agregar_cargos'
down_revision: str | Sequence[str] | None = '009_make_expires_at_nullable'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _crear_tabla_cargos(inspector: sa.Inspector) -> None:
    """Crea la tabla cargos si no existe."""
    tables = inspector.get_table_names()
    if 'cargos' not in tables:
        op.create_table(
            'cargos',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
            sa.Column('nombre_cargo', sa.String(100), nullable=False, unique=True),
            sa.Column('descripcion', sa.Text, nullable=True)
        )
        
        # Insertar cargos por defecto
        op.execute("""
            INSERT INTO cargos (id, nombre_cargo, descripcion) VALUES
            (1, 'vaquero', 'Encargado del cuidado del ganado'),
            (2, 'ordeñador', 'Encargado del proceso de ordeño'),
            (3, 'capataz', 'Supervisor de las actividades de la finca')
            ON DUPLICATE KEY UPDATE nombre_cargo = VALUES(nombre_cargo)
        """)


def _agregar_cargo_id_a_personas(inspector: sa.Inspector) -> None:
    """Agrega cargo_id a la tabla personas si no existe."""
    if 'personas' not in inspector.get_table_names():
        return
    
    columns = [col['name'] for col in inspector.get_columns('personas')]
    
    if 'cargo_id' not in columns:
        op.add_column('personas', sa.Column('cargo_id', sa.Integer,
                                           sa.ForeignKey('cargos.id', ondelete='SET NULL'),
                                           nullable=True))


def upgrade() -> None:
    """Agregar tabla cargos y campo cargo_id a personas."""
    inspector = sa.inspect(op.get_bind())
    _crear_tabla_cargos(inspector)
    _agregar_cargo_id_a_personas(inspector)


def downgrade() -> None:
    """Revertir cambios."""
    inspector = sa.inspect(op.get_bind())
    
    # Eliminar campo cargo_id de personas
    if 'personas' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('personas')]
        if 'cargo_id' in columns:
            op.drop_column('personas', 'cargo_id')
    
    # Eliminar tabla cargos
    if 'cargos' in inspector.get_table_names():
        op.drop_table('cargos')

"""Sincronizar esquema con dump SQL actual

Revision ID: dfd51ca3cf7f
Revises: c10aea45c417
Create Date: 2025-12-05

Esta migración sincroniza el esquema de la base de datos con el dump SQL actual,
agregando constraints y eliminando columnas que no están en el dump.
"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy import types


# revision identifiers, used by Alembic.
revision: str = 'dfd51ca3cf7f'
down_revision: str = 'c10aea45c417'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _agregar_constraint_unique_personas(inspector: sa.Inspector) -> None:
    """Agrega constraint UNIQUE en personas(email, telefono) si no existe."""
    try:
        personas_constraints = inspector.get_unique_constraints('personas')
        constraint_exists = any(
            constraint['name'] == 'email' and 
            set(constraint['column_names']) == {'email', 'telefono'}
            for constraint in personas_constraints
        )
        
        if not constraint_exists:
            op.create_unique_constraint(
                'email',
                'personas',
                ['email', 'telefono']
            )
    except Exception as e:
        print(f"Nota: No se pudo crear constraint UNIQUE en personas: {e}")


def _eliminar_columna_area_potrero(inspector: sa.Inspector) -> None:
    """Elimina columna 'area' de potrero si existe."""
    try:
        potrero_columns = [col['name'] for col in inspector.get_columns('potrero')]
        if 'area' in potrero_columns:
            op.drop_column('potrero', 'area')
    except Exception:
        pass


def _asegurar_columna_not_null(
    inspector: sa.Inspector,
    tabla: str,
    columna: str,
    tipo: types.TypeEngine
) -> None:
    """Asegura que una columna sea NOT NULL."""
    try:
        columns = inspector.get_columns(tabla)
        target_col = next((col for col in columns if col['name'] == columna), None)
        if target_col and target_col['nullable']:
            op.alter_column(tabla, columna, existing_type=tipo, nullable=False)
    except Exception:
        pass


def _asegurar_tenant_id_not_null(inspector: sa.Inspector, tabla: str) -> None:
    """Asegura que tenant_id en una tabla sea NOT NULL."""
    _asegurar_columna_not_null(inspector, tabla, 'tenant_id', sa.Integer())


def upgrade() -> None:
    """Sincroniza el esquema con el dump SQL actual."""
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    _agregar_constraint_unique_personas(inspector)
    _eliminar_columna_area_potrero(inspector)
    _asegurar_columna_not_null(
        inspector, 'ganado', 'sexo', sa.Enum('macho', 'hembra')
    )
    
    tablas_tenant = ['ganado', 'potrero', 'vacunacion', 'qr']
    for tabla in tablas_tenant:
        _asegurar_tenant_id_not_null(inspector, tabla)


def downgrade() -> None:
    """Revierte los cambios de sincronización."""
    # 1. Eliminar constraint UNIQUE en personas(email, telefono)
    try:
        op.drop_constraint('email', 'personas', type_='unique')
    except Exception:
        pass
    
    # 2. Reagregar columna 'area' a potrero si fue eliminada
    try:
        connection = op.get_bind()
        inspector = sa.inspect(connection)
        potrero_columns = [col['name'] for col in inspector.get_columns('potrero')]
        if 'area' not in potrero_columns:
            op.add_column('potrero', sa.Column('area', sa.Numeric(10, 2), nullable=True))
    except Exception:
        pass
    
    # 3. Hacer tenant_id nullable en las tablas (revertir NOT NULL)
    tablas_tenant = ['ganado', 'potrero', 'vacunacion', 'qr']
    for tabla in tablas_tenant:
        try:
            op.alter_column(tabla, 'tenant_id',
                          existing_type=sa.Integer(),
                          nullable=True)
        except Exception:
            pass

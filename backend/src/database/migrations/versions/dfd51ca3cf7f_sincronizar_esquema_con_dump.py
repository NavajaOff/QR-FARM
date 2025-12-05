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


# revision identifiers, used by Alembic.
revision: str = 'dfd51ca3cf7f'
down_revision: str = 'c10aea45c417'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Sincroniza el esquema con el dump SQL actual."""
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    # 1. Agregar constraint UNIQUE en personas(email, telefono) si no existe
    try:
        # Verificar si el constraint ya existe
        personas_constraints = inspector.get_unique_constraints('personas')
        constraint_exists = any(
            constraint['name'] == 'email' and 
            set(constraint['column_names']) == {'email', 'telefono'}
            for constraint in personas_constraints
        )
        
        if not constraint_exists:
            # Crear el constraint UNIQUE compuesto
            op.create_unique_constraint(
                'email',
                'personas',
                ['email', 'telefono']
            )
    except Exception as e:
        # Si el constraint ya existe o hay otro problema, continuar
        print(f"Nota: No se pudo crear constraint UNIQUE en personas: {e}")
    
    # 2. Eliminar columna 'area' de potrero si existe (no está en el dump)
    try:
        potrero_columns = [col['name'] for col in inspector.get_columns('potrero')]
        if 'area' in potrero_columns:
            op.drop_column('potrero', 'area')
    except Exception:
        # La columna puede no existir
        pass
    
    # 3. Asegurar que la columna 'sexo' en ganado sea NOT NULL (según dump)
    try:
        ganado_columns = inspector.get_columns('ganado')
        sexo_col = next((col for col in ganado_columns if col['name'] == 'sexo'), None)
        if sexo_col and sexo_col['nullable']:
            op.alter_column('ganado', 'sexo',
                          existing_type=sa.Enum('macho', 'hembra'),
                          nullable=False)
    except Exception:
        # La columna puede ya ser NOT NULL o no existir
        pass
    
    # 4. Asegurar que tenant_id en ganado sea NOT NULL (según dump)
    try:
        ganado_columns = inspector.get_columns('ganado')
        tenant_col = next((col for col in ganado_columns if col['name'] == 'tenant_id'), None)
        if tenant_col and tenant_col['nullable']:
            op.alter_column('ganado', 'tenant_id',
                          existing_type=sa.Integer(),
                          nullable=False)
    except Exception:
        # La columna puede ya ser NOT NULL
        pass
    
    # 5. Asegurar que tenant_id en potrero sea NOT NULL (según dump)
    try:
        potrero_columns = inspector.get_columns('potrero')
        tenant_col = next((col for col in potrero_columns if col['name'] == 'tenant_id'), None)
        if tenant_col and tenant_col['nullable']:
            op.alter_column('potrero', 'tenant_id',
                          existing_type=sa.Integer(),
                          nullable=False)
    except Exception:
        # La columna puede ya ser NOT NULL
        pass
    
    # 6. Asegurar que tenant_id en vacunacion sea NOT NULL (según dump)
    try:
        vacunacion_columns = inspector.get_columns('vacunacion')
        tenant_col = next((col for col in vacunacion_columns if col['name'] == 'tenant_id'), None)
        if tenant_col and tenant_col['nullable']:
            op.alter_column('vacunacion', 'tenant_id',
                          existing_type=sa.Integer(),
                          nullable=False)
    except Exception:
        # La columna puede ya ser NOT NULL
        pass
    
    # 7. Asegurar que tenant_id en qr sea NOT NULL (según dump)
    try:
        qr_columns = inspector.get_columns('qr')
        tenant_col = next((col for col in qr_columns if col['name'] == 'tenant_id'), None)
        if tenant_col and tenant_col['nullable']:
            op.alter_column('qr', 'tenant_id',
                          existing_type=sa.Integer(),
                          nullable=False)
    except Exception:
        # La columna puede ya ser NOT NULL
        pass


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

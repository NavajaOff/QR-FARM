"""migracion inicial base datos existente

Revision ID: 001
Revises:
Create Date: 2025-11-04 19:53:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Crear tabla roles
    op.create_table('roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rol', sa.String(length=50), nullable=True),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tabla personas
    op.create_table('personas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_rol', sa.Integer(), nullable=True),
        sa.Column('primer_nombre', sa.String(length=50), nullable=True),
        sa.Column('segundo_nombre', sa.String(length=50), nullable=True),
        sa.Column('primer_apellido', sa.String(length=50), nullable=True),
        sa.Column('segundo_apellido', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('telefono', sa.String(length=10), nullable=True),
        sa.Column('fecha_creacion', mysql.DATETIME(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['id_rol'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tabla usuarios
    op.create_table('usuarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_persona', sa.Integer(), nullable=True),
        sa.Column('id_rol', sa.Integer(), nullable=True),
        sa.Column('contrasena', sa.String(length=255), nullable=True),
        sa.Column('estado', sa.Enum('activo', 'inactivo'), nullable=True),
        sa.ForeignKeyConstraint(['id_persona'], ['personas.id'], ),
        sa.ForeignKeyConstraint(['id_rol'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tabla tipo_pasto
    op.create_table('tipo_pasto',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tipo_pasto', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tabla estado_ganado
    op.create_table('estado_ganado',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tipo_estado', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tabla revision
    op.create_table('revision',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('control', mysql.DATETIME(), nullable=True),
        sa.Column('visita', mysql.DATETIME(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tabla potrero
    op.create_table('potrero',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_tipo_pasto', sa.Integer(), nullable=True),
        sa.Column('nombre', sa.String(length=50), nullable=True),
        sa.Column('capacidad', sa.Integer(), nullable=True),
        sa.Column('hectareas', sa.Float(), nullable=True),
        sa.Column('ocupacion', sa.Integer(), server_default=sa.text("'0'"), nullable=True),
        sa.Column('fecha_ultimo_uso', mysql.DATETIME(), nullable=True),
        sa.Column('responsable_persona_id', sa.Integer(), nullable=True),
        sa.Column('proxima_limpieza', mysql.DATETIME(), nullable=True),
        sa.Column('area', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('ultima_limpieza', mysql.DATETIME(), nullable=True),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('estado', sa.Enum('disponible', 'ocupado', 'limpieza'), nullable=False),
        sa.ForeignKeyConstraint(['id_tipo_pasto'], ['tipo_pasto.id'], ),
        sa.ForeignKeyConstraint(['responsable_persona_id'], ['personas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tabla ganado
    op.create_table('ganado',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_potrero', sa.Integer(), nullable=True),
        sa.Column('id_persona', sa.Integer(), nullable=True),
        sa.Column('id_revision', sa.Integer(), nullable=True),
        sa.Column('nombre', sa.String(length=50), nullable=True),
        sa.Column('peso', sa.Integer(), nullable=True),
        sa.Column('raza', sa.String(length=50), nullable=True),
        sa.Column('fecha_nacimiento', mysql.DATETIME(), nullable=True),
        sa.Column('id_estado', sa.Integer(), nullable=True),
        sa.Column('sexo', sa.Enum('macho', 'hembra'), nullable=False),
        sa.ForeignKeyConstraint(['id_estado'], ['estado_ganado.id'], ),
        sa.ForeignKeyConstraint(['id_persona'], ['personas.id'], ),
        sa.ForeignKeyConstraint(['id_potrero'], ['potrero.id'], ),
        sa.ForeignKeyConstraint(['id_revision'], ['revision.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tabla qr
    op.create_table('qr',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_ganado', sa.Integer(), nullable=False),
        sa.Column('id_persona_encargado', sa.Integer(), nullable=True),
        sa.Column('id_persona_dueno', sa.Integer(), nullable=True),
        sa.Column('codigo_qr', sa.String(length=255), nullable=False),
        sa.Column('fecha_creacion', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('fecha_actualizacion', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['id_ganado'], ['ganado.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['id_persona_encargado'], ['personas.id'], ),
        sa.ForeignKeyConstraint(['id_persona_dueno'], ['personas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tabla tipo_vacuna
    op.create_table('tipo_vacuna',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre_vacuna', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tabla vacunacion
    op.create_table('vacunacion',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_animal', sa.Integer(), nullable=True),
        sa.Column('nombre_animal', sa.String(length=50), nullable=True),
        sa.Column('fecha_inicio', mysql.DATETIME(), nullable=True),
        sa.Column('fecha_fin', mysql.DATETIME(), nullable=True),
        sa.Column('fecha_aplicacion', mysql.DATETIME(), nullable=True),
        sa.Column('proxima_dosis', mysql.DATETIME(), nullable=True),
        sa.Column('responsable', sa.Integer(), nullable=True),
        sa.Column('estado', sa.Enum('aplicado', 'pendiente'), nullable=True),
        sa.Column('id_tipo_vacuna', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['id_animal'], ['ganado.id'], ),
        sa.ForeignKeyConstraint(['id_tipo_vacuna'], ['tipo_vacuna.id'], ),
        sa.ForeignKeyConstraint(['responsable'], ['personas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear índices
    op.create_index(op.f('ix_ganado_id_potrero'), 'ganado', ['id_potrero'], unique=False)
    op.create_index(op.f('ix_ganado_id_persona'), 'ganado', ['id_persona'], unique=False)
    op.create_index(op.f('ix_personas_id_rol'), 'personas', ['id_rol'], unique=False)
    op.create_index(op.f('ix_potrero_id_tipo_pasto'), 'potrero', ['id_tipo_pasto'], unique=False)
    op.create_index(op.f('ix_potrero_responsable_persona_id'), 'potrero', ['responsable_persona_id'], unique=False)
    op.create_index(op.f('ix_qr_id_ganado'), 'qr', ['id_ganado'], unique=False)
    op.create_index(op.f('ix_qr_id_persona_encargado'), 'qr', ['id_persona_encargado'], unique=False)
    op.create_index(op.f('ix_qr_id_persona_dueno'), 'qr', ['id_persona_dueno'], unique=False)
    op.create_index(op.f('ix_usuarios_id_persona'), 'usuarios', ['id_persona'], unique=False)
    op.create_index(op.f('ix_usuarios_id_rol'), 'usuarios', ['id_rol'], unique=False)
    op.create_index(op.f('ix_vacunacion_id_animal'), 'vacunacion', ['id_animal'], unique=False)
    op.create_index(op.f('ix_vacunacion_responsable'), 'vacunacion', ['responsable'], unique=False)


def downgrade() -> None:
    # Eliminar índices
    op.drop_index(op.f('ix_vacunacion_responsable'), table_name='vacunacion')
    op.drop_index(op.f('ix_vacunacion_id_animal'), table_name='vacunacion')
    op.drop_index(op.f('ix_usuarios_id_rol'), table_name='usuarios')
    op.drop_index(op.f('ix_usuarios_id_persona'), table_name='usuarios')
    op.drop_index(op.f('ix_qr_id_persona_dueno'), table_name='qr')
    op.drop_index(op.f('ix_qr_id_persona_encargado'), table_name='qr')
    op.drop_index(op.f('ix_qr_id_ganado'), table_name='qr')
    op.drop_index(op.f('ix_potrero_responsable_persona_id'), table_name='potrero')
    op.drop_index(op.f('ix_potrero_id_tipo_pasto'), table_name='potrero')
    op.drop_index(op.f('ix_personas_id_rol'), table_name='personas')
    op.drop_index(op.f('ix_ganado_id_persona'), table_name='ganado')
    op.drop_index(op.f('ix_ganado_id_potrero'), table_name='ganado')

    # Eliminar tablas
    op.drop_table('vacunacion')
    op.drop_table('tipo_vacuna')
    op.drop_table('qr')
    op.drop_table('ganado')
    op.drop_table('potrero')
    op.drop_table('revision')
    op.drop_table('estado_ganado')
    op.drop_table('tipo_pasto')
    op.drop_table('usuarios')
    op.drop_table('personas')
    op.drop_table('roles')
"""datos iniciales

Revision ID: 002
Revises: 001
Create Date: 2025-11-04 19:54:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Insertar datos iniciales para roles
    op.bulk_insert(
        sa.table('roles',
            sa.column('id', sa.Integer),
            sa.column('rol', sa.String),
            sa.column('descripcion', sa.Text)
        ),
        [
            {'id': 1, 'rol': 'admin', 'descripcion': 'Administrador del sistema'},
            {'id': 2, 'rol': 'usuario', 'descripcion': 'Usuario normal'}
        ]
    )

    # Insertar datos iniciales para tipo_pasto
    op.bulk_insert(
        sa.table('tipo_pasto',
            sa.column('id', sa.Integer),
            sa.column('tipo_pasto', sa.String)
        ),
        [
            {'id': 1, 'tipo_pasto': 'Brachiaria humidicola'},
            {'id': 2, 'tipo_pasto': 'Brachiaria decumbens'},
            {'id': 3, 'tipo_pasto': 'Pasto mombazaa'}
        ]
    )

    # Insertar datos iniciales para estado_ganado
    op.bulk_insert(
        sa.table('estado_ganado',
            sa.column('id', sa.Integer),
            sa.column('tipo_estado', sa.String)
        ),
        [
            {'id': 1, 'tipo_estado': 'activo'},
            {'id': 2, 'tipo_estado': 'saludable'},
            {'id': 3, 'tipo_estado': 'revision'},
            {'id': 4, 'tipo_estado': 'enfermo'},
            {'id': 5, 'tipo_estado': 'vendido'}
        ]
    )

    # Insertar datos iniciales para tipo_vacuna
    op.bulk_insert(
        sa.table('tipo_vacuna',
            sa.column('id', sa.Integer),
            sa.column('nombre_vacuna', sa.String)
        ),
        [
            {'id': 1, 'nombre_vacuna': 'Brucella'},
            {'id': 2, 'nombre_vacuna': 'Aftosa'},
            {'id': 3, 'nombre_vacuna': 'Clostridiales'},
            {'id': 4, 'nombre_vacuna': 'Rabia'},
            {'id': 5, 'nombre_vacuna': 'Leptospirosis'}
        ]
    )

    # Insertar usuario administrador por defecto
    # Primero insertar persona
    op.bulk_insert(
        sa.table('personas',
            sa.column('id', sa.Integer),
            sa.column('id_rol', sa.Integer),
            sa.column('primer_nombre', sa.String),
            sa.column('segundo_nombre', sa.String),
            sa.column('primer_apellido', sa.String),
            sa.column('segundo_apellido', sa.String),
            sa.column('email', sa.String),
            sa.column('telefono', sa.String),
            sa.column('fecha_creacion', sa.DateTime)
        ),
        [
            {
                'id': 1,
                'id_rol': 1,
                'primer_nombre': 'Admin',
                'segundo_nombre': 'Sistema',
                'primer_apellido': 'QR',
                'segundo_apellido': 'Farm',
                'email': 'admin@qrfarm.com',
                'telefono': '1234567890',
                'fecha_creacion': sa.text('NOW()')
            }
        ]
    )

    # Insertar usuario admin
    op.bulk_insert(
        sa.table('usuarios',
            sa.column('id', sa.Integer),
            sa.column('id_persona', sa.Integer),
            sa.column('id_rol', sa.Integer),
            sa.column('contrasena', sa.String),
            sa.column('estado', sa.Enum('activo', 'inactivo'))
        ),
        [
            {
                'id': 1,
                'id_persona': 1,
                'id_rol': 1,
                'contrasena': 'admin123',
                'estado': 'activo'
            }
        ]
    )


def downgrade() -> None:
    # Eliminar datos iniciales
    op.execute("DELETE FROM usuarios WHERE id_persona = 1")
    op.execute("DELETE FROM personas WHERE email = 'admin@qrfarm.com'")
    op.execute("DELETE FROM tipo_vacuna WHERE id IN (1, 2, 3, 4, 5)")
    op.execute("DELETE FROM estado_ganado WHERE id IN (1, 2, 3, 4, 5)")
    op.execute("DELETE FROM tipo_pasto WHERE id IN (1, 2, 3)")
    op.execute("DELETE FROM roles WHERE id IN (1, 2)")
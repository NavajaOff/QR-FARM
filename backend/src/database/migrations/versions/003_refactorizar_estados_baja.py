"""Refactorizar sistema de baja para usar solo estado_ganado

Revision ID: 003_refactorizar_estados_baja
Revises: 002_baja_ganado
Create Date: 2025-01-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '003_refactorizar_estados_baja'
down_revision = '002_baja_ganado'
branch_labels = None
depends_on = None


def upgrade():
    # Agregar estados de baja a estado_ganado
    op.bulk_insert(
        sa.table('estado_ganado',
            sa.column('id', sa.Integer),
            sa.column('tipo_estado', sa.String)
        ),
        [
            {'id': 5, 'tipo_estado': 'muerte'},
            {'id': 6, 'tipo_estado': 'venta'},
            {'id': 7, 'tipo_estado': 'robo'},
            {'id': 8, 'tipo_estado': 'otra'}
        ]
    )
    
    # Migrar animales dados de baja al nuevo sistema
    # Si tienen estado_baja = 'dado_de_baja', cambiar su id_estado según la causa_baja
    op.execute("""
        UPDATE ganado 
        SET id_estado = CASE 
            WHEN causa_baja = 'muerte' THEN 5
            WHEN causa_baja = 'venta' THEN 6
            WHEN causa_baja = 'robo' THEN 7
            WHEN causa_baja = 'otra' THEN 8
            ELSE 8
        END
        WHERE estado_baja = 'dado_de_baja'
    """)
    
    # Eliminar columnas de baja de la tabla ganado
    op.drop_column('ganado', 'observaciones_baja')
    op.drop_column('ganado', 'fecha_baja')
    op.drop_column('ganado', 'causa_baja')
    op.drop_column('ganado', 'estado_baja')


def downgrade():
    # Reagregar columnas de baja
    op.add_column('ganado', sa.Column('estado_baja', sa.Enum('activo', 'dado_de_baja', name='estado_baja'), nullable=False, server_default='activo'))
    op.add_column('ganado', sa.Column('causa_baja', sa.String(length=255), nullable=True))
    op.add_column('ganado', sa.Column('fecha_baja', sa.Date(), nullable=True))
    op.add_column('ganado', sa.Column('observaciones_baja', sa.Text(), nullable=True))
    
    # Migrar de vuelta: si id_estado es de baja, poner estado_baja = 'dado_de_baja'
    op.execute("""
        UPDATE ganado 
        SET estado_baja = 'dado_de_baja',
            causa_baja = CASE 
                WHEN id_estado = 5 THEN 'muerte'
                WHEN id_estado = 6 THEN 'venta'
                WHEN id_estado = 7 THEN 'robo'
                WHEN id_estado = 8 THEN 'otra'
                ELSE 'otra'
            END
        WHERE id_estado IN (5, 6, 7, 8)
    """)
    
    # Eliminar estados de baja de estado_ganado
    op.execute("DELETE FROM estado_ganado WHERE id IN (5, 6, 7, 8)")


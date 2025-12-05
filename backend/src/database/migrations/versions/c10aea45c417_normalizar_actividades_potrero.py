"""Normalizar actividades de potrero a 3FN

Revision ID: c10aea45c417
Revises: 005_eliminar_revision
Create Date: 2025-12-04

Esta migración normaliza los campos fecha_ultimo_uso, ultima_limpieza y proxima_limpieza
de la tabla potrero a una nueva tabla historial_potrero, siguiendo las mejores prácticas
de normalización 3FN según recomendación del instructor.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c10aea45c417'
down_revision: str = '005_eliminar_revision'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crea la tabla historial_potrero y migra los datos de potrero."""
    # Crear la tabla historial_potrero según especificación del instructor
    op.create_table(
        'historial_potrero',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('id_potrero', sa.Integer, sa.ForeignKey('potrero.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tipo_evento', sa.Enum('uso', 'limpieza', 'inspeccion', 'mantenimiento', name='tipo_evento_potrero'), nullable=False),
        sa.Column('fecha_evento', sa.DateTime, nullable=False),
        sa.Column('observaciones', sa.Text, nullable=True),
        sa.Column('tenant_id', sa.Integer, sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime, server_default=sa.func.current_timestamp()),
        sa.Column('fecha_actualizacion', sa.DateTime, server_default=sa.func.current_timestamp(), 
                  onupdate=sa.func.current_timestamp())
    )
    
    # Crear índices para mejorar rendimiento
    op.create_index('idx_historial_potrero_potrero', 'historial_potrero', ['id_potrero'])
    op.create_index('idx_historial_potrero_tipo', 'historial_potrero', ['tipo_evento'])
    op.create_index('idx_historial_potrero_fecha', 'historial_potrero', ['fecha_evento'])
    op.create_index('idx_historial_potrero_tenant', 'historial_potrero', ['tenant_id'])
    
    # Migrar datos existentes de potrero a historial_potrero
    # 1. Migrar fecha_ultimo_uso como evento tipo 'uso'
    op.execute("""
        INSERT INTO historial_potrero (id_potrero, tipo_evento, fecha_evento, tenant_id, fecha_creacion, fecha_actualizacion)
        SELECT id, 'uso', fecha_ultimo_uso, tenant_id, NOW(), NOW()
        FROM potrero
        WHERE fecha_ultimo_uso IS NOT NULL
    """)
    
    # 2. Migrar ultima_limpieza como evento tipo 'limpieza'
    op.execute("""
        INSERT INTO historial_potrero (id_potrero, tipo_evento, fecha_evento, tenant_id, fecha_creacion, fecha_actualizacion)
        SELECT id, 'limpieza', ultima_limpieza, tenant_id, NOW(), NOW()
        FROM potrero
        WHERE ultima_limpieza IS NOT NULL
    """)
    
    # 3. Migrar proxima_limpieza como evento tipo 'limpieza' programada
    op.execute("""
        INSERT INTO historial_potrero (id_potrero, tipo_evento, fecha_evento, observaciones, tenant_id, fecha_creacion, fecha_actualizacion)
        SELECT id, 'limpieza', proxima_limpieza, 'Programada', tenant_id, NOW(), NOW()
        FROM potrero
        WHERE proxima_limpieza IS NOT NULL
    """)
    
    # Eliminar las columnas de la tabla potrero
    try:
        op.drop_column('potrero', 'fecha_ultimo_uso')
    except Exception:
        pass
    
    try:
        op.drop_column('potrero', 'ultima_limpieza')
    except Exception:
        pass
    
    try:
        op.drop_column('potrero', 'proxima_limpieza')
    except Exception:
        pass


def downgrade() -> None:
    """Revierte los cambios, restaurando las columnas en potrero."""
    # Reagregar las columnas a potrero
    op.add_column('potrero', sa.Column('fecha_ultimo_uso', sa.DateTime, nullable=True))
    op.add_column('potrero', sa.Column('ultima_limpieza', sa.DateTime, nullable=True))
    op.add_column('potrero', sa.Column('proxima_limpieza', sa.DateTime, nullable=True))
    
    # Migrar datos de vuelta desde historial_potrero
    # Obtener la última fecha de uso por potrero
    op.execute("""
        UPDATE potrero p
        INNER JOIN (
            SELECT id_potrero, MAX(fecha_evento) as fecha_uso
            FROM historial_potrero
            WHERE tipo_evento = 'uso'
            GROUP BY id_potrero
        ) hp ON p.id = hp.id_potrero
        SET p.fecha_ultimo_uso = hp.fecha_uso
    """)
    
    # Obtener la última limpieza por potrero
    op.execute("""
        UPDATE potrero p
        INNER JOIN (
            SELECT id_potrero, MAX(fecha_evento) as fecha_limpieza
            FROM historial_potrero
            WHERE tipo_evento = 'limpieza' AND (observaciones IS NULL OR observaciones != 'Programada')
            GROUP BY id_potrero
        ) hp ON p.id = hp.id_potrero
        SET p.ultima_limpieza = hp.fecha_limpieza
    """)
    
    # Obtener la próxima limpieza programada por potrero
    op.execute("""
        UPDATE potrero p
        INNER JOIN (
            SELECT id_potrero, MIN(fecha_evento) as fecha_proxima
            FROM historial_potrero
            WHERE tipo_evento = 'limpieza' AND observaciones = 'Programada' AND fecha_evento > NOW()
            GROUP BY id_potrero
        ) hp ON p.id = hp.id_potrero
        SET p.proxima_limpieza = hp.fecha_proxima
    """)
    
    # Eliminar índices
    try:
        op.drop_index('idx_historial_potrero_tenant', 'historial_potrero')
    except Exception:
        pass
    
    try:
        op.drop_index('idx_historial_potrero_fecha', 'historial_potrero')
    except Exception:
        pass
    
    try:
        op.drop_index('idx_historial_potrero_tipo', 'historial_potrero')
    except Exception:
        pass
    
    try:
        op.drop_index('idx_historial_potrero_potrero', 'historial_potrero')
    except Exception:
        pass
    
    # Eliminar la tabla historial_potrero
    op.drop_table('historial_potrero')
    
    # Eliminar el enum tipo_evento_potrero
    try:
        op.execute("DROP TYPE IF EXISTS tipo_evento_potrero")
    except Exception:
        pass

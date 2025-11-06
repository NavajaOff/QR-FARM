"""Estructura base sin datos

Revision ID: 003
Revises: 75b46c2713f7
Create Date: 2025-11-05 20:30:00.000000

Esta migración contiene únicamente la estructura de la base de datos.
Los datos se insertan mediante seeders.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: str = '75b46c2713f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """
    Esta migración solo mantiene la estructura.
    Los datos de la migración anterior se han movido a seeders.
    
    Nota: La estructura ya existe desde migraciones anteriores,
    por lo que esta migración solo documenta el cambio de estrategia.
    """
    
    # Eliminar datos de ejemplo de la migración anterior
    # (excepto el usuario admin que se crea desde app.py)
    
    # Limpiar ganado
    op.execute("DELETE FROM ganado WHERE id > 0")
    
    # Limpiar potreros
    op.execute("DELETE FROM potrero WHERE id > 0")
    
    # Limpiar usuarios (excepto admin)
    op.execute("DELETE FROM usuarios WHERE id_persona > 1")
    
    # Limpiar personas (excepto admin)
    op.execute("DELETE FROM personas WHERE id > 1")
    
    print("✅ Datos de ejemplo eliminados. Use los seeders para insertar datos base.")

def downgrade() -> None:
    """
    Para revertir, ejecute la migración 75b46c2713f7 que contiene los datos
    """
    pass
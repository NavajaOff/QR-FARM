


"""eliminar_campos_baja_ganado

Revision ID: 12673429ef47
Revises: 003_refactorizar_estados_baja
Create Date: 2025-11-22 14:59:47.680880

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12673429ef47'
down_revision: str = '003_refactorizar_estados_baja'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:


def downgrade() -> None:

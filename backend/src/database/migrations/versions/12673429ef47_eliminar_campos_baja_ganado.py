


"""eliminar_campos_baja_ganado

Revision ID: 12673429ef47
Revises: 003_refactorizar_estados_baja
Create Date: 2025-11-22 14:59:47.680880

"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12673429ef47'
down_revision: str = '003_refactorizar_estados_baja'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    # This migration intentionally left empty as the fields were already removed
    # in a previous migration or manually. No database changes needed.
    pass


def downgrade() -> None:
    # This migration intentionally left empty as there are no changes to revert.
    # The fields removal was handled in a previous migration or manually.
    pass

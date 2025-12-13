"""Hacer expires_at nullable en password_recovery_tokens."""
from typing import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '009_make_expires_at_nullable'
down_revision: str | Sequence[str] | None = '008_add_recovery_status'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Hacer expires_at nullable."""
    # MySQL requires the full column definition when modifying
    op.alter_column('password_recovery_tokens', 'expires_at',
                    existing_type=sa.DateTime,
                    nullable=True,
                    existing_nullable=False)


def downgrade() -> None:
    """Revertir cambios."""
    op.alter_column('password_recovery_tokens', 'expires_at',
                    existing_type=sa.DateTime,
                    nullable=False,
                    existing_nullable=True)


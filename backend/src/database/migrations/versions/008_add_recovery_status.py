"""Agregar campo estado a password_recovery_tokens y hacer token_hash nullable."""
from typing import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '008_add_recovery_status'
down_revision: str | Sequence[str] | None = '007_password_recovery_tokens'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Agregar campo estado y hacer token_hash nullable."""
    # Create enum for recovery status
    recovery_status_enum = sa.Enum('pendiente', 'aprobada', 'rechazada', name='recovery_estado')
    recovery_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Make token_hash nullable (will be set when approved)
    # MySQL requires the full column definition when modifying
    op.alter_column('password_recovery_tokens', 'token_hash',
                    existing_type=sa.String(128),
                    nullable=True,
                    existing_nullable=False)
    
    # Make expires_at nullable (will be set when approved)
    op.alter_column('password_recovery_tokens', 'expires_at',
                    existing_type=sa.DateTime,
                    nullable=True,
                    existing_nullable=False)
    
    # Add estado column with default 'pendiente'
    op.add_column('password_recovery_tokens', 
                  sa.Column('estado', recovery_status_enum, nullable=False, server_default='pendiente'))
    
    # Add index for estado for faster queries
    op.create_index('idx_recovery_estado', 'password_recovery_tokens', ['estado'])
    
    # Add approved_at and rejected_at columns for tracking
    op.add_column('password_recovery_tokens',
                  sa.Column('approved_at', sa.DateTime, nullable=True))
    op.add_column('password_recovery_tokens',
                  sa.Column('rejected_at', sa.DateTime, nullable=True))
    op.add_column('password_recovery_tokens',
                  sa.Column('approved_by', sa.Integer, sa.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True))


def downgrade() -> None:
    """Revertir cambios."""
    op.drop_index('idx_recovery_estado', table_name='password_recovery_tokens')
    op.drop_column('password_recovery_tokens', 'approved_by')
    op.drop_column('password_recovery_tokens', 'rejected_at')
    op.drop_column('password_recovery_tokens', 'approved_at')
    op.drop_column('password_recovery_tokens', 'estado')
    
    # MySQL requires the full column definition when modifying
    op.alter_column('password_recovery_tokens', 'expires_at',
                    existing_type=sa.DateTime,
                    nullable=False,
                    existing_nullable=True)
    
    op.alter_column('password_recovery_tokens', 'token_hash',
                    existing_type=sa.String(128),
                    nullable=False,
                    existing_nullable=True)
    
    recovery_status_enum = sa.Enum(name='recovery_estado')
    recovery_status_enum.drop(op.get_bind(), checkfirst=True)


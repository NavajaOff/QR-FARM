"""Agregar tabla de tokens de recuperación de contraseña."""
from typing import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '007_password_recovery_tokens'
down_revision: str | Sequence[str] | None = '006_esquema_erd'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crear tabla de tokens de recuperación."""
    recovery_type_enum = sa.Enum('usuario', 'admin', name='recovery_tipo')
    recovery_type_enum.create(op.get_bind(), checkfirst=True)
    op.create_table(
        'password_recovery_tokens',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('usuario_id', sa.Integer, sa.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(128), nullable=False, unique=True),
        sa.Column('tipo', recovery_type_enum, nullable=False),
        sa.Column('tenant_id', sa.Integer, nullable=True),
        sa.Column('solicitante_email', sa.String(255), nullable=True),
        sa.Column('contexto', sa.String(255), nullable=True),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('used_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.current_timestamp(), nullable=False)
    )
    op.create_index('idx_recovery_usuario_id', 'password_recovery_tokens', ['usuario_id'])
    op.create_index('idx_recovery_token_hash', 'password_recovery_tokens', ['token_hash'])


def downgrade() -> None:
    """Eliminar tabla de tokens de recuperación."""
    op.drop_index('idx_recovery_usuario_id', table_name='password_recovery_tokens')
    op.drop_index('idx_recovery_token_hash', table_name='password_recovery_tokens')
    op.drop_table('password_recovery_tokens')
    recovery_type_enum = sa.Enum(name='recovery_tipo')
    recovery_type_enum.drop(op.get_bind(), checkfirst=True)


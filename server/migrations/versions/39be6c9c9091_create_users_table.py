"""create users table

Revision ID: 39be6c9c9091
Revises: c5ce79442a18
Create Date: 2025-03-16 08:46:25.428913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39be6c9c9091'
down_revision: Union[str, None] = 'c5ce79442a18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),  # Contraseña sin encriptar
    )
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('users')
    pass
    # ### end Alembic commands ###

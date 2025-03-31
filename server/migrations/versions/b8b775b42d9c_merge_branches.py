"""Merge branches

Revision ID: b8b775b42d9c
Revises: b44d5ae6aceb, fb436d52bbbb
Create Date: 2025-03-28 22:18:22.224270

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8b775b42d9c'
down_revision: Union[str, None] = ('b44d5ae6aceb', 'fb436d52bbbb')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

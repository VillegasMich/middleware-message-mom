"""create_user_queues_table

Revision ID: b44d5ae6aceb
Revises: f21a3eeba530
Create Date: 2025-03-20 18:58:10.552255

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b44d5ae6aceb"
down_revision: Union[str, None] = "f21a3eeba530"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_queue",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("queue_id", sa.Integer(), sa.ForeignKey("queues.id"), nullable=True),
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

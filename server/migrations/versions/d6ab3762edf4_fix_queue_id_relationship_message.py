"""Fix queue id relationship message

Revision ID: d6ab3762edf4
Revises: a1059a1d3113
Create Date: 2025-03-29 14:07:03.214456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'd6ab3762edf4'
down_revision: Union[str, None] = 'a1059a1d3113'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    pass

def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("messages") as batch_op:
        batch_op.add_column(sa.Column("queue_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("messages_ibfk_1", "queues", ["queue_id"], ["id"])
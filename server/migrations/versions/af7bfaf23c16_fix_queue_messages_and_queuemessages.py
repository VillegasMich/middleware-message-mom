"""Fix Queue Messages and QueueMessages

Revision ID: af7bfaf23c16
Revises: 07143ea52e96
Create Date: 2025-03-29 14:38:10.046727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'af7bfaf23c16'
down_revision: Union[str, None] = '07143ea52e96'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to fix Queue Messages relationships."""
    with op.batch_alter_table("queue_messages") as batch_op:
        batch_op.drop_constraint("fk_queue_messages_message", type_="foreignkey")
        batch_op.drop_constraint("fk_queue_messages_queue", type_="foreignkey")

def downgrade() -> None:
    """Downgrade schema to restore Queue Messages relationships."""
    with op.batch_alter_table("queue_messages") as batch_op:
        batch_op.create_foreign_key(
            "fk_queue_messages_message", "messages", ["message_id"], ["id"]
        )
        batch_op.create_foreign_key(
            "fk_queue_messages_queue", "queues", ["queue_id"], ["id"]
        )
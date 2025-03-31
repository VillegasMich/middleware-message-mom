"""Fix QueueMessage relationships

Revision ID: 0647f6a0c4e8
Revises: d6ab3762edf4
Create Date: 2025-03-29 14:23:25.082402

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '0647f6a0c4e8'
down_revision: Union[str, None] = 'd6ab3762edf4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    """Apply the migration: Fix QueueMessage relationships"""
    with op.batch_alter_table("queue_messages") as batch_op:
        batch_op.drop_constraint("queue_messages_ibfk_1", type_="foreignkey")
        batch_op.drop_constraint("queue_messages_ibfk_2", type_="foreignkey")
        batch_op.create_foreign_key("queue_messages_message_id_fkey", "messages", ["message_id"], ["id"])
        batch_op.create_foreign_key("queue_messages_queue_id_fkey", "queues", ["queue_id"], ["id"])

def downgrade():
    """Rollback the migration"""
    with op.batch_alter_table("queue_messages") as batch_op:
        batch_op.drop_constraint("queue_messages_message_id_fkey", type_="foreignkey")
        batch_op.drop_constraint("queue_messages_queue_id_fkey", type_="foreignkey")
        batch_op.create_foreign_key("queue_messages_ibfk_1", "queues", ["queue_id"], ["id"])
        batch_op.create_foreign_key("queue_messages_ibfk_2", "messages", ["message_id"], ["id"])
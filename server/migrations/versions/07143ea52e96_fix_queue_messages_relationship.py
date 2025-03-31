"""Fix Queue messages relationship

Revision ID: 07143ea52e96
Revises: 0647f6a0c4e8
Create Date: 2025-03-29 14:29:16.403742

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '07143ea52e96'
down_revision: Union[str, None] = '0647f6a0c4e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    """Fix Queue messages relationship."""
    # Drop the incorrect foreign key if it exists
    with op.batch_alter_table("queue_messages") as batch_op:
        batch_op.drop_constraint("queue_messages_message_id_fkey", type_="foreignkey")
        batch_op.drop_constraint("queue_messages_queue_id_fkey", type_="foreignkey")
    
    # Recreate the foreign keys with correct references
    with op.batch_alter_table("queue_messages") as batch_op:
        batch_op.create_foreign_key("fk_queue_messages_queue", "queues", ["queue_id"], ["id"], ondelete="CASCADE")
        batch_op.create_foreign_key("fk_queue_messages_message", "messages", ["message_id"], ["id"], ondelete="CASCADE")

def downgrade():
    """Revert Queue messages relationship changes."""
    with op.batch_alter_table("queue_messages") as batch_op:
        batch_op.drop_constraint("fk_queue_messages_queue", type_="foreignkey")
        batch_op.drop_constraint("fk_queue_messages_message", type_="foreignkey")
    
    with op.batch_alter_table("queue_messages") as batch_op:
        batch_op.create_foreign_key("queue_messages_message_id_fkey", "messages", ["message_id"], ["id"])
        batch_op.create_foreign_key("queue_messages_queue_id_fkey", "queues", ["queue_id"], ["id"])
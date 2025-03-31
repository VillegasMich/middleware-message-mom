"""add queue_messages table and update messages & queues

Revision ID: a1059a1d3113
Revises: b8b775b42d9c
Create Date: 2025-03-29 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = "a1059a1d3113"
down_revision = "b8b775b42d9c"
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Upgrade schema."""
    # Create queue_messages table
    op.create_table(
        "queue_messages",
        sa.Column("queue_id", sa.Integer(), sa.ForeignKey("queues.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("message_id", sa.Integer(), sa.ForeignKey("messages.id", ondelete="CASCADE"), primary_key=True),
    )

    # Explicitly drop foreign key constraint before dropping the column
    op.drop_constraint("messages_ibfk_1", "messages", type_="foreignkey")
    
    # Remove queue_id from messages (as it's now many-to-many)
    op.drop_column("messages", "queue_id")

def downgrade() -> None:
    """Downgrade schema."""
    # Add queue_id back to messages
    op.add_column("messages", sa.Column("queue_id", sa.Integer(), nullable=True))

    # Restore foreign key constraint
    op.create_foreign_key("messages_ibfk_1", "messages", "queues", ["queue_id"], ["id"], ondelete="CASCADE")

    # Drop queue_messages table
    op.drop_table("queue_messages")
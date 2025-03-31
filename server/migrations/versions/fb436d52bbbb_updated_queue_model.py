"""add queue_routing_keys table and update queues

Revision ID: fb436d52bbbb
Revises: f21a3eeba530
Create Date: 2025-03-27 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = "fb436d52bbbb"
down_revision = "f21a3eeba530" 
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create queue_routing_keys table
    op.create_table(
        "queue_routing_keys",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("queue_id", sa.Integer(), sa.ForeignKey("queues.id", ondelete="CASCADE"), nullable=False),
        sa.Column("routing_key", sa.String(length=255), nullable=False),
    )

    # Add new columns to queues table
    op.add_column("queues", sa.Column("topic_id", sa.Integer(), sa.ForeignKey("topics.id"), nullable=True))
    op.add_column("queues", sa.Column("is_private", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove added columns
    op.drop_column("queues", "topic_id")
    op.drop_column("queues", "is_private")

    # Drop queue_routing_keys table
    op.drop_table("queue_routing_keys")

"""Fix Queue and User 2

Revision ID: 519ed1faafe4
Revises: 37fca595e704
Create Date: 2025-03-29 15:25:51.434566

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '519ed1faafe4'
down_revision: Union[str, None] = '37fca595e704'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add the user_id column first
    op.add_column("queues", sa.Column("user_id", sa.Integer, nullable=False))

    # Now, create the foreign key constraint
    op.create_foreign_key("queues_ibfk_1", "queues", "users", ["user_id"], ["id"])

def downgrade():
    # Drop the foreign key first
    op.drop_constraint("queues_ibfk_1", "queues", type_="foreignkey")
    
    # Then drop the column
    op.drop_column("queues", "user_id")
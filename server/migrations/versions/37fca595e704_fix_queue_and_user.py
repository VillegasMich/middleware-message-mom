"""Fix Queue and User

Revision ID: 37fca595e704
Revises: af7bfaf23c16
Create Date: 2025-03-29 15:04:29.527359

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '37fca595e704'
down_revision: Union[str, None] = 'af7bfaf23c16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():

    op.drop_constraint("queues_ibfk_1", "queues", type_="foreignkey")
    op.drop_column("queues", "user_id")

def downgrade():

    op.add_column("queues", sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True))
    op.create_foreign_key("queues_ibfk_1", "queues", "users", ["user_id"], ["id"])
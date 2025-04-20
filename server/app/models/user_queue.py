from app.core.database import Base
from sqlalchemy import Column, ForeignKey, Integer

"""
    ATTRIBUTES
    id => Represents the unique id for the user queue table.
    user_id => Represents the unique id of a user.
    queue_id => Represents the unique id of a queue.
"""
class user_queue(Base):
    __tablename__ = "user_queue"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column("user_id", Integer, ForeignKey("users.id"), nullable=True)
    queue_id = Column("queue_id", Integer, ForeignKey("queues.id"), nullable=True)

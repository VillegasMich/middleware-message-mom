from app.core.database import Base
from sqlalchemy import Column, ForeignKey, Integer


class user_queue(Base):
    __tablename__ = "user_queues"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column("user_id", Integer, ForeignKey("users.id"), nullable=True)
    queue_id = Column("queue_id", Integer, ForeignKey("queues.id"), nullable=True)

from app.core.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
import sqlalchemy as sa
from sqlalchemy.orm import relationship


class Queue(Base):
    __tablename__ = "queues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    is_private = Column(Boolean, default=sa.sql.expression.false(), nullable=False)
    is_leader = Column(Boolean, default=sa.sql.expression.false(), nullable=False)
    owner = relationship("User", back_populates="owned_queues")
    queue_messages = relationship(
        "QueueMessage", back_populates="queue", cascade="all, delete-orphan"
    )
    users = relationship("User", secondary="user_queue", back_populates="queues")
    topic = relationship("Topic", back_populates="queues")
    routing_keys = relationship(
        "QueueRoutingKey", back_populates="queue", cascade="all, delete-orphan"
    )


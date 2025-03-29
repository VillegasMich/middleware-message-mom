from app.core.database import Base
from sqlalchemy import Column, ForeignKey, Integer
import sqlalchemy as sa
from sqlalchemy.orm import relationship

class QueueMessage(Base):
    __tablename__ = "queue_messages"

    queue_id = Column(Integer, ForeignKey("queues.id"), primary_key=True)
    message_id = Column(Integer, ForeignKey("messages.id"), primary_key=True)

    queue = relationship("Queue", back_populates="queue_messages")
    message = relationship("Message", back_populates="queue_messages")
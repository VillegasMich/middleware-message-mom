from app.core.database import Base
from sqlalchemy import Column, ForeignKey, Integer
import sqlalchemy as sa
from sqlalchemy.orm import relationship

"""
    ATTRIBUTES
    queue_id => Represents the unique id of a queue.
    message_id => Represents the unique id of a message.
    
    queue => Relationship with the Queue model, which represents the queues in the system.
    message => Relationship with the Message model, which represents the messages in the system.
"""

class QueueMessage(Base):
    __tablename__ = "queue_messages"

    queue_id = Column(Integer, ForeignKey("queues.id"), primary_key=True)
    message_id = Column(Integer, ForeignKey("messages.id"), primary_key=True)

    queue = relationship("Queue", back_populates="queue_messages")
    message = relationship("Message", back_populates="queue_messages")
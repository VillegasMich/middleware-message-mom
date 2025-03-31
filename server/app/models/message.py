from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

'''
    MESSAGE ATTRIBUTES
    id => Represents the unique id for the message.
    content => Contains the body of the message.
    queue_id => Relationship with a specific queue, if null the message is not related to a queue.
    topic_id => Relationship with a specific topic, if null the message is not related to a topic.
    status => Status of the message, initialized in "Pending".
    routing_key => Represents the name of the queue or topic the message is set to be delivered.
    created_at => Creation date of the message, needed to implement FIFO functionality.
'''
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(255), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    status = Column(String(10), default='Pending')
    routing_key = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now()) 

    queue_messages = relationship("QueueMessage", back_populates="message", cascade="all, delete-orphan")
    topic = relationship("Topic", overlaps="messages")
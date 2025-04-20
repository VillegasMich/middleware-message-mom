from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

"""
    ATTRIBUTES
    id => Represents the unique id for the message.
    content => Contains the body of the message.
    topic_id => Relationship with a specific topic, if null the message is not related to a topic.
    status => Status of the message, initialized in "Pending".
    routing_key => Routing key used to identify the message, it is a string that can be used to filter messages.
    created_at => Creation date of the message, needed to implement FIFO functionality.
    
    queue_messages => Relationship with the QueueMessage model, which represents the messages in the queues.
    topic => Relationship with the Topic model, which represents the messages in the topics.
"""
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
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base
import sqlalchemy as sa

"""
    ATTRIBUTES
    id => Represents the unique id for the topic.
    name => Represents the name of the topic, it is a string that can be used to identify the topic.
    user_id => Represents the unique id of a user, more specifically the owner of the topic.
    
    users => Relationship with the User model, which represents the users that are subscribed to the topic.
    messages => Relationship with the Message model, which represents the messages associated to the topic.
    queues => Relationship with the Queue model, which represents the queues associated with the topic.
"""


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    users = relationship("User", secondary="user_topic", overlaps="topics")
    messages = relationship("Message", overlaps="topic")
    queues = relationship("Queue", back_populates="topic")

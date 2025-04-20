from app.core.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
import sqlalchemy as sa
from sqlalchemy.orm import relationship

"""
    ATTRIBUTES
    id => Represents the unique id for the queue.
    name => Represents the name of the queue, it is a string that can be used to identify the queue.
    user_id => Represents the unique id of a user.
    topic_id => Represents the unique id of a topic, if null the queue is not related to a topic.
    is_private => Represents if the queue is private or not, it is a boolean value.
    
    owner => Relationship with the User model, which represents the user that owns the queue.
    queue_messages => Relationship with the QueueMessage model, which represents the messages in the queue.
    users => Relationship with the User model, which represents the users that are subscribed to the queue.
    topic => Relationship with the Topic model, which represents the topic that the queue is associated to.
    routing_keys => Relationship with the QueueRoutingKey model, which represents the routing keys used to 
        identify the messages in the queue.
"""

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


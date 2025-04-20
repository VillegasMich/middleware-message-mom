from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

"""
    ATTRIBUTES
    id => Represents the unique id for the routing key.
    queue_id => Represents the unique id of a queue.
    routing_key => Represents the routing key used to identify the message, it is a string that can be used to filter messages.
    
    queue => Relationship with the Queue model, which represents the queues in the system.
"""

class QueueRoutingKey(Base):
    __tablename__ = "queue_routing_keys"

    id = Column(Integer, primary_key=True, index=True)
    queue_id = Column(Integer, ForeignKey("queues.id", ondelete="CASCADE"), nullable=False)
    routing_key = Column(String(255), nullable=False)

    queue = relationship("Queue", back_populates="routing_keys")

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class QueueRoutingKey(Base):
    __tablename__ = "queue_routing_keys"

    id = Column(Integer, primary_key=True, index=True)
    queue_id = Column(Integer, ForeignKey("queues.id", ondelete="CASCADE"), nullable=False)
    routing_key = Column(String(255), nullable=False)

    queue = relationship("Queue", back_populates="routing_keys")

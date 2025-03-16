from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(255), nullable=False)
    queue_id = Column(Integer, ForeignKey("queues.id"), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    status = Column(String(10), default='Pending')

    queue = relationship("Queue")
    topic = relationship("Topic")
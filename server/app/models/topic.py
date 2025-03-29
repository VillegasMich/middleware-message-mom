from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    users = relationship('User', secondary='user_topic', overlaps="topics")
    messages = relationship('Message', overlaps="topic")
    queues = relationship("Queue", back_populates="topic")

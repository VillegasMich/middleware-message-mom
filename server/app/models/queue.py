from app.core.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Queue(Base):
    __tablename__ = "queues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    messages = relationship("Message", overlaps="queue")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    users = relationship("User", secondary="user_queue", overlaps="queues")

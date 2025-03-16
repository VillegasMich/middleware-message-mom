from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Queue(Base):
    __tablename__ = "queues"

    id = Column(Integer, primary_key=True, index=True)
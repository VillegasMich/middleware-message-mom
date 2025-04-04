from app.core.database import Base
from sqlalchemy import Column, ForeignKey, Integer


class user_topic(Base):
    __tablename__ = "user_topic"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column("user_id", Integer, ForeignKey("users.id"), nullable=True)
    topic_id = Column("topic_id", Integer, ForeignKey("topics.id"), nullable=True)

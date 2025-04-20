from app.core.database import Base
from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

"""
    ATTRIBUTES
    id => Represents the unique id for the user.
    name => Represents the name of the user.
    password => Represents the password of the user.
    
    owned_queues => Relationship with the Queue model, which represents the queues owned by the user.
    topics => Relationship with the Topic model, which represents the topics associated with the user.
    queues => Relationship with the Queue model, which represents the queues associated with the user.
"""

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    
    owned_queues = relationship("Queue", back_populates="owner")
    topics = relationship("Topic", secondary="user_topic", overlaps="users")
    queues = relationship("Queue", secondary="user_queue", back_populates="users")

    def set_password(self, password):
        #Hash the password and store it in the database
        self.password = self.hash_password(password)

    def verify_password(self, plain_password):
        #Verify the password against the hashed password in the database
        return pwd_context.verify(plain_password, str(self.password))

    @classmethod
    def hash_password(cls, password):
        #Hash the password using encryption algorithms
        return pwd_context.hash(password)

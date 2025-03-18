from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)  
    topics = relationship('Topic', secondary='user_topic', overlaps="users")
    
    def set_password(self, password):
        self.password = self.hash_password(password)
    
    def verify_password(self, plain_password):
        return pwd_context.verify(plain_password, self.password)

    @classmethod
    def hash_password(cls, password):
        return pwd_context.hash(password)

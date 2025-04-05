from sqlalchemy.orm import Session, joinedload

from fastapi import HTTPException
from collections import deque

from ..models.topic import Topic
from ..models.user_queue import user_queue as UserQueue
from ..RoundRobinManager import RoundRobinManager


class TopicRepository:
    def __init__(self, db: Session):
        self.db = db

    def all(self):
        query = self.db.query(Topic)
        topics = query.all()
        
        return topics
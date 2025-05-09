from sqlalchemy.orm import Session

from fastapi import HTTPException
from ..models.user import User
from ..models.queue import Queue
from zookeeper import ZK_NODE_USERS, zk


class UserRepository:
    """
    This class provides methods to interact with the database for user-related operations.
    It includes functionality to register new users, validate user existence, and retrieve topic-related queues
    for a specific user. This class ensures proper database transactions and integrates with ZooKeeper for
    user metadata management.
    """
    def __init__(self, db: Session):
        self.db = db

    def register(self, request):
        username = request.user_name
        password = request.user_password

        if self.db.query(User).filter(User.name == username).first():
            raise HTTPException(status_code=400, detail="User already exists")

        new_user = User(id=request.user_id, name=username)
        new_user.set_password(password)

        self.db.add(new_user)
        self.db.commit()

        zk.ensure_path(f"{ZK_NODE_USERS}/{new_user.id}")

    def get_topic_queues(self, request):
        user_queues = (
            self.db.query(Queue)
            .filter(Queue.user_id == request.user_id, Queue.topic_id != None)
            .all()
        )
        return user_queues

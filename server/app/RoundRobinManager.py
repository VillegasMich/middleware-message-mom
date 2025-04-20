from collections import deque

from app.models.queue import Queue
from sqlalchemy.orm import Session


class RoundRobinManager:
    """
    This class is responsible for managing the round robin algorithm for users in queues.
    It maintains a dictionary of queues and their associated users, allowing for efficient user management.
    """

    def __init__(self) -> None:
        self.user_queues_dict = dict()

    def sync_users_queues(self, db: Session):
        #Synchronize the users and queues in the database with the user_queues_dict.
        queues = db.query(Queue).all()
        for queue in queues:
            if queue not in self.user_queues_dict.keys():
                self.user_queues_dict[queue.id] = deque()
            for user in queue.users:
                self.user_queues_dict[queue.id].append(user.name)

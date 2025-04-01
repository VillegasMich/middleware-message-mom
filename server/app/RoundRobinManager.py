from collections import deque

from app.models.queue import Queue
from sqlalchemy.orm import Session


class RoundRobinManager:
    def __init__(self) -> None:
        self.user_queues_dict = dict()

    def sync_users_queues(self, db: Session):
        queues = db.query(Queue).all()
        for queue in queues:
            if queue not in self.user_queues_dict.keys():
                self.user_queues_dict[queue.id] = deque()
            for user in queue.users:
                self.user_queues_dict[queue.id].append(user.name)

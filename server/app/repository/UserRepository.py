from sqlalchemy.orm import Session
from fastapi import HTTPException
from collections import deque

from ..models.queue import Queue
from ..models.user_queue import user_queue as UserQueue
from ..RoundRobinManager import RoundRobinManager
from app.core.rrmanager import get_round_robin_manager


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def subscribe_queue(self, request):
        round_robin_manager: RoundRobinManager = get_round_robin_manager()

        existing_queue = self.db.query(Queue).filter(
            Queue.id == request.queue_id).first()

        if existing_queue.is_private:
            is_invited = (
                self.db.query(UserQueue)
                .filter(
                    UserQueue.user_id == request.user_id,
                    UserQueue.queue_id == existing_queue.id,
                )
                .first()
            )
            if not is_invited:
                raise HTTPException(
                    status_code=403, detail="You must be invited to join this queue."
                )

        user_queue_entry = (
            self.db.query(UserQueue)
            .filter(
                UserQueue.user_id == request.user_id,
                UserQueue.queue_id == existing_queue.id,
            )
            .first()
        )

        if user_queue_entry:
            raise HTTPException(
                status_code=409, detail="User already subscribed")

        new_subscription = UserQueue(
            user_id=request.user_id, queue_id=existing_queue.id
        )
        self.db.add(new_subscription)
        self.db.commit()

        if request.queue_id not in round_robin_manager.user_queues_dict:
            round_robin_manager.user_queues_dict[request.queue_id] = deque()

        round_robin_manager.user_queues_dict[request.queue_id].append(
            request.user_name)
        
        print(round_robin_manager.user_queues_dict)

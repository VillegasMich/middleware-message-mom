from sqlalchemy.orm import Session, joinedload

from fastapi import HTTPException
from collections import deque

from ..models.queue import Queue
from ..models.message import Message
from ..models.queue_message import QueueMessage
from ..models.user_queue import user_queue as UserQueue
from ..RoundRobinManager import RoundRobinManager
from app.core.rrmanager import get_round_robin_manager
from zookeeper import zk, ZK_NODE_QUEUES


class QueueRepository:
    def __init__(self, db: Session):
        self.db = db

    def all(self):
        query = self.db.query(Queue).options(joinedload(Queue.owner))
        query = query.filter(Queue.is_private == False)
        queues = query.all()

        return queues

    def subscribe(self, request):
        round_robin_manager: RoundRobinManager = get_round_robin_manager()

        existing_queue = (
            self.db.query(Queue).filter(Queue.id == request.queue_id).first()
        )

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
            raise HTTPException(status_code=409, detail="User already subscribed")

        new_subscription = UserQueue(
            user_id=request.user_id, queue_id=existing_queue.id
        )
        self.db.add(new_subscription)
        self.db.commit()

        if request.queue_id not in round_robin_manager.user_queues_dict:
            round_robin_manager.user_queues_dict[request.queue_id] = deque()

        round_robin_manager.user_queues_dict[request.queue_id].append(request.user_name)

        print(round_robin_manager.user_queues_dict)

    def delete(self, request):
        round_robin_manager: RoundRobinManager = get_round_robin_manager()
        queue = self.db.query(Queue).filter(Queue.id == request.id).first()
        if queue:
            if queue.user_id != request.user_id:
                raise HTTPException(
                    status_code=403,
                    detail="You do not have permission to delete this queue.",
                )
            
            queue_messages = self.db.query(QueueMessage).filter(QueueMessage.queue_id == queue.id).all()
        
            for queue_message in queue_messages:
                
                queue_message_id = queue_message.message_id
                self.db.delete(queue_message)
                
                message = self.db.query(Message).filter(Message.id == queue_message_id).first()
                self.db.delete(message)

            self.db.delete(queue)
            self.db.commit()

            zk.delete(f"{ZK_NODE_QUEUES}/{request.id}", recursive=True)
            round_robin_manager.user_queues_dict.pop(request.id, None)
            return {"message": "Queue deleted successfully", "queue_id": request.id}

    def unsubscribe(self, request):
        round_robin_manager: RoundRobinManager = get_round_robin_manager()
        existing_queue = (
            self.db.query(Queue).filter(Queue.id == request.queue_id).first()
        )

        if existing_queue:
            user_queue_entry = (
                self.db.query(UserQueue)
                .filter(
                    UserQueue.user_id == request.user_id,
                    UserQueue.queue_id == existing_queue.id,
                )
                .first()
            )

            if not user_queue_entry:
                raise HTTPException(status_code=409, detail="User was not subscribed")

            self.db.delete(user_queue_entry)
            self.db.commit()

            if request.queue_id in round_robin_manager.user_queues_dict:
                round_robin_manager.user_queues_dict[request.queue_id] = deque(
                    user
                    for user in round_robin_manager.user_queues_dict[request.queue_id]
                    if user != request.user_name
                )

                if not round_robin_manager.user_queues_dict[request.queue_id]:
                    del round_robin_manager.user_queues_dict[request.queue_id]

            return {"message": "Successfully unsubscribed from the queue"}

    def create(self, request):
        # Check if in the current server the queue exists
        existing_queue = self.db.query(Queue).filter(Queue.name == request.name).first()
        if existing_queue:
            raise HTTPException(status_code=400, detail="Queue already exists")

        new_id = request.id

        new_queue = Queue(
            id=new_id,
            name=request.name,
            is_private=False,
            user_id=request.user_id,
        )
        self.db.add(new_queue)
        self.db.commit()
        self.db.refresh(new_queue)

        print("\n QUEUE REPLICATED \n")

from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models.message import Message
from ..models.queue import Queue
from ..models.queue_message import QueueMessage
from ..models.user_queue import user_queue as UserQueue
from ..models.queue_routing_key import QueueRoutingKey
from ..RoundRobinManager import RoundRobinManager
from app.core.rrmanager import get_round_robin_manager
import fnmatch


class MessageRepository:
    """
    This class provides methods to interact with the database for message-related operations.
    It includes functionality to save messages to queues or topics, consume messages from queues, and handle
    message routing based on routing keys. This class ensures proper database transactions and message management
    for the middleware.
    """

    def __init__(self, db: Session):
        self.db = db

    def save_queue_message(self, request):
        new_message = Message(content=request.content,
                              routing_key=request.routing_key)

        self.db.add(new_message)
        self.db.flush()

        queue_message = QueueMessage(
            queue_id=request.id, message_id=new_message.id
        )

        self.db.add(queue_message)
        self.db.commit()

    def save_topic_message(self, request):
        routing_key = request.routing_key

        new_message = Message(
            content=request.content,
            routing_key=routing_key,
            topic_id=request.id,
        )

        self.db.add(new_message)
        self.db.flush()

        if not new_message.id:
            raise HTTPException(
                status_code=500, detail="Failed to create message.")

        all_queues = (
            self.db.query(Queue)
            .join(QueueRoutingKey, Queue.id == QueueRoutingKey.queue_id)
                .filter(Queue.topic_id == request.id)
                .all()
        )

        matching_queues = [
            queue
            for queue in all_queues
            if any(
                fnmatch.fnmatch(routing_key, qr.routing_key)
                for qr in queue.routing_keys
            )
        ]

        queue_messages = [
            QueueMessage(queue_id=queue.id, message_id=new_message.id)
            for queue in matching_queues
        ]

        self.db.add_all(queue_messages)
        self.db.commit()

    def consume_queue_message(self, request):
        round_robin_manager: RoundRobinManager = get_round_robin_manager()

        is_subscribed = (
            self.db.query(UserQueue)
            .filter(
                UserQueue.queue_id == request.id, UserQueue.user_id == request.user_id
            )
            .first()
        )

        if not is_subscribed:
            raise HTTPException(
                status_code=403, detail="You are not subscribed to this queue."
            )

        expected_user_name = round_robin_manager.user_queues_dict[request.id][-1]

        print(expected_user_name)
        print(request.user_name)
        if expected_user_name == request.user_name:
            queue_message = (
                self.db.query(QueueMessage)
                .join(Message)
                .filter(QueueMessage.queue_id == request.id)
                .order_by(Message.created_at.asc())
                .with_for_update(skip_locked=True)
                .first()
            )

            if not queue_message:
                raise HTTPException(
                    status_code=404, detail="Message not found")

            message_content = queue_message.message.content
            message_id = queue_message.message_id

            self.db.delete(queue_message)
            self.db.flush()

            remaining_refs = (
                self.db.query(QueueMessage)
                .filter(QueueMessage.message_id == message_id)
                .count()
            )

            if remaining_refs == 0:
                message_to_delete = (
                    self.db.query(Message)
                    .filter(Message.id == message_id)
                    .first()
                )
                print(message_to_delete)
                if message_to_delete:
                    self.db.delete(message_to_delete)

            self.db.flush()
            self.db.commit()

            turn_user = round_robin_manager.user_queues_dict[request.id].popleft(
            )
            round_robin_manager.user_queues_dict[request.id].append(turn_user)

            print(message_content)
            return message_content
        else:
            return "It is not your turn!"

    def consume_topic_message(self, request):
        
        private_queue = (
            self.db.query(Queue)
            .filter(
                Queue.id == request.id,
                Queue.user_id == request.user_id,
                Queue.is_private == True,
            )
            .first()
        )

        print('-------------Private queue------------------')
        print(private_queue)
        print('-------------------------------')
        if private_queue:
            
            routing_keys = [rk.routing_key for rk in private_queue.routing_keys]
            
            messages = (
                self.db.query(Message)
                .join(QueueMessage, Message.id == QueueMessage.message_id)
                .filter(
                    QueueMessage.queue_id == private_queue.id,
                    Message.routing_key.in_(routing_keys) 
                )
                .order_by(Message.created_at.asc())
                .all()
            )

            if not messages:
                raise HTTPException(status_code=404, detail="No messages found")

            return {
                "content": [message.content for message in messages],
                "ids": [message.id for message in messages],
            }
        else:
            return {
                "message": "No private queue found",
                "content": [],
                "ids": [],
            }


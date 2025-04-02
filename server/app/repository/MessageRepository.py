from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models.message import Message
from ..models.queue import Queue
from ..models.queue_message import QueueMessage
from ..models.queue_routing_key import QueueRoutingKey

import fnmatch


class MessageRepository:

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

        print(all_queues)

        matching_queues = [
            queue
            for queue in all_queues
            if any(
                fnmatch.fnmatch(routing_key, qr.routing_key)
                for qr in queue.routing_keys
            )
        ]

        print(matching_queues)

        queue_messages = [
            QueueMessage(queue_id=queue.id, message_id=new_message.id)
            for queue in matching_queues
        ]
        
        print(queue_messages)
        
        self.db.add_all(queue_messages)
        self.db.commit()

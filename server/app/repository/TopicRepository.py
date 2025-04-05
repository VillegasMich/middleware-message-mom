from sqlalchemy.orm import Session

from fastapi import HTTPException
from collections import deque

from ..models.topic import Topic
from ..models.queue import Queue
from ..models.queue_routing_key import QueueRoutingKey

class TopicRepository:
    def __init__(self, db: Session):
        self.db = db

    def all(self):
        query = self.db.query(Topic)
        topics = query.all()
        
        return topics
    
    def subscribe(self, request):
        existing_topic = self.db.query(Topic).filter(Topic.id == request.topic_id).first()

        if existing_topic:
            topic_id = existing_topic.id

            queue_name = f"{existing_topic.name}_{existing_topic.id}_{request.user_name}_{request.user_id}"

            private_queue = self.db.query(Queue).filter(Queue.name == queue_name).first()

            if not private_queue:
                private_queue = Queue(
                    name=queue_name,
                    user_id=request.user_id,
                    topic_id=topic_id,
                    is_private=True,
                )

                self.db.add(private_queue)
                self.db.commit()
                self.db.refresh(private_queue)

            existing_routing_key = (
                self.db.query(QueueRoutingKey)
                .filter(
                    QueueRoutingKey.queue_id == private_queue.id,
                    QueueRoutingKey.routing_key == request.routing_key,
                )
                .first()
            )

            if not existing_routing_key:
                routing_key = QueueRoutingKey(
                    queue_id=private_queue.id, routing_key=request.routing_key
                )
                self.db.add(routing_key)
                self.db.commit()
            else:
                raise HTTPException(
                    status_code=400, detail="Routing key already exists for this queue"
                )

        return {"message": "Successfully subscribed to the topic"}
from sqlalchemy.orm import Session

from fastapi import HTTPException
from collections import deque

from ..models.topic import Topic
from ..models.queue import Queue
from ..models.queue_routing_key import QueueRoutingKey
from ..models.queue_message import QueueMessage
from zookeeper import zk, ZK_NODE_QUEUES, ZK_NODE_TOPICS



class TopicRepository:
    def __init__(self, db: Session):
        self.db = db

    def all(self):
        query = self.db.query(Topic)
        topics = query.all()
        
        return topics
    
    def delete(self, request):
        topic = self.db.query(Topic).filter(Topic.id == request.id).first()
        if topic:
            if topic.user_id != request.user_id:
                raise HTTPException(
                    status_code=403,
                    detail="You do not have permission to delete this topic",
                )

            bound_queues = self.db.query(Queue).filter(Queue.topic_id == topic.id).all()

            for queue in bound_queues:
                self.db.query(QueueMessage).filter(QueueMessage.queue_id == queue.id).delete()
                self.db.delete(queue)

            self.db.delete(topic)
            self.db.commit()

            zk.delete(f"{ZK_NODE_TOPICS}/{topic.id}", recursive=True)
    
    def subscribe(self, request):
        print('\n'+ str(request.topic_id))
        existing_topic = self.db.query(Topic).filter(Topic.id == request.topic_id).first()
        print('\n'+ existing_topic.name)
        if existing_topic:
            topic_id = existing_topic.id

            queue_name = f"{existing_topic.name}_{existing_topic.id}_{request.user_name}_{request.user_id}"

            private_queue = self.db.query(Queue).filter(Queue.name == queue_name).first()

            if not private_queue:
                
                new_id = 1
                servers: list[str] = zk.get_children("/servers") or []
                for server in servers:
                    server_queues: list[str] = (
                        zk.get_children(f"/servers-metadata/{server}/Queues") or []
                    )
                    for queue_id in server_queues:
                        if int(queue_id) >= new_id:
                            new_id = int(queue_id) + 1

                private_queue = Queue(
                    id=new_id,
                    name=queue_name,
                    user_id=request.user_id,
                    topic_id=topic_id,
                    is_private=True,
                )                

                self.db.add(private_queue)
                self.db.commit()
                self.db.refresh(private_queue)
                zk.ensure_path(f"{ZK_NODE_QUEUES}/{private_queue.id}")


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
        else:
            return {"message": "Your subscription failed"}

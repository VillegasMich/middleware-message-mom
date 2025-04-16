from sqlalchemy.orm import Session

from fastapi import HTTPException
from collections import deque
import traceback
import grpc
from ..models.topic import Topic
from ..models.queue import Queue
from ..models.message import Message
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
            queue_ids = [queue.id for queue in bound_queues]

            self.db.query(QueueMessage).filter(QueueMessage.queue_id.in_(queue_ids)).delete(synchronize_session=False)
            
            self.db.query(Message).filter(Message.topic_id == topic.id).delete(synchronize_session=False)
            
            for queue in bound_queues:
                self.db.delete(queue)
                
            self.db.delete(topic)
            self.db.commit()

            zk.delete(f"{ZK_NODE_TOPICS}/{topic.id}", recursive=True)

    def subscribe(self, request):
        print("\n" + str(request.topic_id))
        existing_topic = (
            self.db.query(Topic).filter(Topic.id == request.topic_id).first()
        )
        print("\n" + existing_topic.name)
        if existing_topic:
            topic_id = existing_topic.id

            queue_name = f"{existing_topic.name}_{existing_topic.id}_{request.user_name}_{request.user_id}"

            private_queue = (
                self.db.query(Queue).filter(Queue.name == queue_name).first()
            )

            if not private_queue:

                if not request.HasField("queue_id"):
                    new_id = 1
                    servers: list[str] = zk.get_children("/servers") or []
                    for server in servers:
                        server_queues: list[str] = (
                            zk.get_children(f"/servers-metadata/{server}/Queues") or []
                        )
                        for queue_id in server_queues:
                            if int(queue_id) >= new_id:
                                new_id = int(queue_id) + 1
                else:
                    new_id = request.queue_id
                    
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
        
        
    def unsubscribe(self, request):
        try:
            user_id = request.user_id
            user_name = request.user_name
            topic_id = request.topic_id
            routing_key = request.routing_key
            
            if not request.queue_id:
                
                existing_private_queue = (
                    self.db.query(Queue)
                    .filter(Queue.topic_id == topic_id, Queue.user_id == user_id)
                    .first()
                )
                
            else:
                queue_id = request.queue_id
                
                existing_private_queue = (
                    self.db.query(Queue)
                    .filter(Queue.id == queue_id)
                    .first()
                )

            if not existing_private_queue:
                raise grpc.RpcError(grpc.StatusCode.NOT_FOUND, "Queue not found")

            routing_key_entry = (
                self.db.query(QueueRoutingKey)
                .filter(
                    QueueRoutingKey.queue_id == queue_id,
                    QueueRoutingKey.routing_key == routing_key,
                )
                .first()
            )

            if not routing_key_entry:
                raise HTTPException(status_code=404, detail="Routing key not found for queue")

            self.db.delete(routing_key_entry)
            self.db.flush()
            self.db.commit()

            remaining_keys = (
                self.db.query(QueueRoutingKey)
                .filter(QueueRoutingKey.queue_id == queue_id)
                .count()
            )

            if remaining_keys == 0:
                queue_messages = (
                    self.db.query(QueueMessage)
                    .filter(QueueMessage.queue_id == queue_id)
                    .all()
                )

                for queue_message in queue_messages:
                    message_id = queue_message.message_id
                    self.db.delete(queue_message)
                    self.db.flush()

                    remaining_refs = (
                        self.db.query(QueueMessage)
                        .filter(QueueMessage.message_id == message_id)
                        .count()
                    )

                    if remaining_refs == 0:
                        message = self.db.query(Message).filter(Message.id == message_id).first()
                        if message:
                            self.db.delete(message)

                self.db.delete(existing_private_queue)
                self.db.commit()

            return {"message": "Successfully unsubscribed from the topic with that routing key."}
        
        except Exception as e:
            print(f"[Server Unsubscribe] Error: {e}")
            traceback.print_exc()
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Internal server error while unsubscribing.")


    def create(self, request):
        existing_topic = self.db.query(Topic).filter(Topic.name == request.name).first()

        if existing_topic:
            raise HTTPException(status_code=400, detail="Topic already exists")

        new_id = request.id

        new_topic = Topic(id=new_id, name=request.name, user_id=request.user_id)
        self.db.add(new_topic)
        self.db.commit()
        self.db.refresh(new_topic)

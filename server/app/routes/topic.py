import fnmatch
from typing import Optional

from app.core.auth_helpers import get_current_user
from app.core.database import get_db
from app.models.message import Message
from app.models.queue import Queue
from app.models.queue_message import QueueMessage
from app.models.queue_routing_key import QueueRoutingKey
from app.models.topic import Topic
from app.models.user import User
from app.models.user_queue import user_queue as UserQueue
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from zookeeper import SERVER_IP, SERVER_PORT, ZK_NODE_TOPICS, zk

router = APIRouter()


class TopicCreate(BaseModel):
    name: str
    routing_key: Optional[str] = None


class TopicSubscribe(BaseModel):
    topic_id: int
    routing_key: Optional[str] = None


class MessageCreate(BaseModel):
    content: str
    routing_key: str


@router.get("/topics/")
async def get_topics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    only_owned: bool = False,
):
    query = db.query(Topic)

    if only_owned:
        query = query.filter(Topic.user_id == current_user.id)

    topics = query.all()

    # Traemos los topicos del zk o mandamos un grpc a cada servidor para que las entreguen ???
    servers: list[str] = zk.get_children("/servers") or []
    for server in servers:
        if server != f"{SERVER_IP}:{SERVER_PORT}":
            print("Ask for topics")
            # #TEST
            # #------------------------------
            # Client.send_grpc_message(
            #     "queue", 1, "listando todas las queues", "default", "127.0.0.1:8080")
            # #------------------------------

    return {"message": "Topics listed successfully", "topics": topics}


# Get the queue related to a topic (not taking into account routing key)
@router.get("/user/queue-topic")
async def get_user_queue_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_queue = (
        db.query(Queue)
        .filter(Queue.user_id == current_user.id, Queue.topic_id == topic_id)
        .first()
    )
    if user_queue:
        return {"message": "Queue listed successfully", "queue": user_queue}
    else:
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_queue = zk.get_children(f"/servers/{server}/Queues") or []
                for queue in server_queue:
                    return {"message": "Queue listed successfully", "queue": queue}


# Queues of ALL subscribed topics
@router.get("/user/queues-topics")
async def get_user_queues_topics(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    user_queues = (
        db.query(Queue)
        .filter(Queue.user_id == current_user.id, Queue.topic_id != None)
        .all()
    )

    if user_queues:
        return {"message": "Queues listed successfully", "queues": user_queues}
    else:
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_queue = zk.get_children(f"/servers/{server}/Queues") or []
                for queue in server_queue:
                    return {"message": "Queue listed successfully", "queue": queue}
    return {"message": "No queues found for subscribed topics", "queues": []}


# Queue binded to a routing key (1 topic)
@router.get("/user/routingkey-topic")
async def get_user_routingkey_topic(
    topic_id: int,
    routing_key: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_queue = (
        db.query(Queue)
        .filter(Queue.user_id == current_user.id, Queue.topic_id == topic_id)
        .join(QueueRoutingKey, Queue.id == QueueRoutingKey.queue_id)
        .filter(QueueRoutingKey.routing_key == routing_key)
        .first()
    )

    if not user_queue:
        raise HTTPException(
            status_code=404, detail="No queue found for the given topic and routing key"
        )

    return {"message": "Queue listed successfully", "queue": user_queue}


@router.post("/topics/")
async def create_topic(
    topic: TopicCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    existing_topic = db.query(Topic).filter(Topic.name == topic.name).first()
    if existing_topic:
        raise HTTPException(status_code=400, detail="Topic already exists")

    new_topic = Topic(name=topic.name, user_id=current_user.id)
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)

    zk.ensure_path(f"{ZK_NODE_TOPICS}/{new_topic.id}")

    return {"message": "Topic created successfully", "topic_id": new_topic.id}


@router.delete("/topics/{topic_id}")
async def delete_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()

    if topic:
        if topic.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to delete this topic",
            )

        bound_queues = db.query(Queue).filter(Queue.topic_id == topic.id).all()

        for queue in bound_queues:
            db.query(QueueMessage).filter(QueueMessage.queue_id == queue.id).delete()
            db.delete(queue)

        db.delete(topic)
        db.commit()

        zk.delete(f"{ZK_NODE_TOPICS}/{topic.id}", recursive=True)

        return {"message": "Topic deleted successfully", "topic_name": topic.name}
    else:
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_topic = zk.get_children(f"/servers/{server}/Topics") or []
                for topic in server_topic:
                    print("Send grcp to delete topic")
                    return {
                        "message": "Topic deleted successfully",
                        "topic_name": topic,
                    }
    raise HTTPException(status_code=404, detail="Topic not found")


@router.post("/topics/{topic_id}/publish")
async def publish_message(
    topic_id: int, message: MessageCreate, db: Session = Depends(get_db)
):
    existing_topic = db.query(Topic).filter(Topic.id == topic_id).first()

    if existing_topic:
        routing_key = message.routing_key

        new_message = Message(
            content=message.content,
            routing_key=routing_key,
            topic_id=existing_topic.id,
        )

        db.add(new_message)
        db.flush()

        if not new_message.id:
            raise HTTPException(status_code=500, detail="Failed to create message.")

        all_queues = (
            db.query(Queue)
            .join(QueueRoutingKey, Queue.id == QueueRoutingKey.queue_id)
            .filter(Queue.topic_id == topic_id)
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
        db.add_all(queue_messages)

        db.commit()

        return {
            "message": "Message published successfully",
            "topic_id": existing_topic.id,
            "message_id": new_message.id,
        }
    else:
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_topic = zk.get_children(f"/servers/{server}/Topics") or []
                for topic in server_topic:
                    print("Send grpc to publish message")
                    return {
                        "message": "Message published successfully",
                        "topic_id": topic_id,
                    }
    raise HTTPException(status_code=404, detail="Topic not found")


@router.get("/topics/queues/{queue_id}/consume")
async def consume_message(
    queue_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    private_queue = (
        db.query(Queue)
        .filter(
            Queue.id == queue_id,
            Queue.user_id == current_user.id,
            Queue.is_private == True,
        )
        .first()
    )

    print("\n", private_queue.id, "\n")

    if private_queue:
        messages = (
            db.query(Message)
            .join(QueueMessage, Message.id == QueueMessage.message_id)
            .filter(QueueMessage.queue_id == private_queue.id)
            .order_by(Message.created_at.asc())
            .all()
        )

        if not messages:
            raise HTTPException(status_code=404, detail="No messages found")

        return {
            "message": "Messages consumed successfully",
            "content": [message.content for message in messages],
            "ids": [message.id for message in messages],
        }
    else:
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_queue = zk.get_children(f"/servers/{server}/Queues") or []
                for queue in server_queue:
                    print("Send grpc to consume message")
                    return {
                        "message": "Messages consumed successfully",
                        "queue": queue,
                    }
    raise HTTPException(status_code=404, detail="Private queue not found")


@router.post("/topics/subscribe")
async def subscribe(
    topic: TopicSubscribe,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    existing_topic = db.query(Topic).filter(Topic.id == topic.topic_id).first()

    if existing_topic:
        topic_id = existing_topic.id

        queue_name = f"{existing_topic.name}_{existing_topic.id}_{current_user.name}_{current_user.id}"

        private_queue = db.query(Queue).filter(Queue.name == queue_name).first()

        if not private_queue:
            private_queue = Queue(
                name=queue_name,
                user_id=current_user.id,
                topic_id=topic_id,
                is_private=True,
            )

            db.add(private_queue)
            db.commit()
            db.refresh(private_queue)

        existing_routing_key = (
            db.query(QueueRoutingKey)
            .filter(
                QueueRoutingKey.queue_id == private_queue.id,
                QueueRoutingKey.routing_key == topic.routing_key,
            )
            .first()
        )

        if not existing_routing_key:
            routing_key = QueueRoutingKey(
                queue_id=private_queue.id, routing_key=topic.routing_key
            )
            db.add(routing_key)
            db.commit()
        else:
            raise HTTPException(
                status_code=400, detail="Routing key already exists for this queue"
            )

        return {"message": "Successfully subscribed to the topic"}
    else:
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_topic = zk.get_children(f"/servers/{server}/Topics") or []
                for topic in server_topic:
                    print("Send grpc to subscribe")
                    return {
                        "message": "Successfully subscribed to the topic",
                        "topic_name": topic,
                    }
    raise HTTPException(status_code=404, detail="Topic not found")

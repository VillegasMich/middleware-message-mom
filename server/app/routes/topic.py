import fnmatch
from typing import Optional
import json
import traceback
from random import sample
from app.core.auth_helpers import get_current_user
from app.core.database import get_db
from app.grpc.Client import Client
from app.models.message import Message
from app.models.queue import Queue
from app.models.queue_message import QueueMessage
from app.models.queue_routing_key import QueueRoutingKey
from app.models.topic import Topic
from app.models.user import User
from app.models.user_queue import user_queue as UserQueue
from fastapi import APIRouter, Depends, HTTPException
from fastapi.logger import logger
from pydantic import BaseModel
from sqlalchemy.orm import Session
from zookeeper import (
    SERVER_ADDR,
    SERVER_IP,
    SERVER_PORT,
    ZK_NODE_TOPICS,
    zk,
    ZK_NODE_QUEUES,
)

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
    servers: list[str] = zk.get_children("/servers") or []
    for server in servers:
        if server != f"{SERVER_IP}:{SERVER_PORT}":
            server_ip, _ = server.split(":")
            remote_topics = Client.send_grpc_get_all_topics(server_ip + ":8080") or []
            for remote_topic in remote_topics:
                topics.append(
                    Topic(id=remote_topic.get("id"), name=remote_topic.get("name"))
                )
            # topics.extend(remote_queues)

    seen_ids = set()
    unique_topics = []
    for topic in topics:
        if topic.id not in seen_ids:
            unique_topics.append(topic)
            seen_ids.add(topic.id)

    unique_topics.sort(key=lambda q: q.id)

    return {"message": "Topics listed successfully", "topics": unique_topics}


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
                server_queue = (
                    zk.get_children(f"/servers-metadata/{server}/Queues") or []
                )
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

    servers: list[str] = zk.get_children("/servers") or []
    for server in servers:
        if server != f"{SERVER_IP}:{SERVER_PORT}":
            server_ip, _ = server.split(":")
            remote_queues = Client.send_grpc_get_all_topic_queues(
                current_user.id, server_ip + ":8080"
            )
            user_queues.extend(remote_queues)

    if len(user_queues) > 0:
        return {"message": "Queues listed successfully", "queues": user_queues}

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

    new_id = 1
    servers: list[str] = zk.get_children("/servers") or []
    for server in servers:
        server_topics: list[str] = (
            zk.get_children(f"/servers-metadata/{server}/Topics") or []
        )
        for topic_id in server_topics:
            if int(topic_id) >= new_id:
                new_id = int(topic_id) + 1

    new_topic = Topic(id=new_id, name=topic.name, user_id=current_user.id)
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)

    if len(servers) >= 2:
        print("\n REPLICATION \n")
        servers.remove(SERVER_ADDR)
        follower_ip = sample(servers, 1)[0]
        leader_path = f"{ZK_NODE_TOPICS}/{new_topic.id}"
        follower_path = f"/servers-metadata/{follower_ip}/Topics/{new_topic.id}"
        print("\n FOLLOWER PATH: " + str(follower_path) + "\n")
        zk.ensure_path(ZK_NODE_TOPICS)
        zk.ensure_path(f"/servers-metadata/{follower_ip}/Topics")
        # Data to store in ZooKeeper
        payload_leader = json.dumps(
            {
                "leader": True,
            }
        ).encode()

        payload_follower = json.dumps(
            {
                "leader": False,
            }
        ).encode()

        server_ip, _ = follower_ip.split(":")
        response = Client.send_grpc_topic_create(
            new_id, topic.name, current_user.id, server_ip + ":8080"
        )

        # Create ZooKeeper entries
        zk.create(leader_path, payload_leader)
        zk.create(follower_path, payload_follower)
        return {"message": "Topic created successfully", "topic_id": new_topic.id}

    payload_leader = json.dumps(
        {
            "leader": True,
        }
    ).encode()
    zk.create(f"{ZK_NODE_TOPICS}/{new_topic.id}", payload_leader)

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
        queue_ids = [queue.id for queue in bound_queues]

        db.query(QueueMessage).filter(QueueMessage.queue_id.in_(queue_ids)).delete(synchronize_session=False)
         
        db.query(Message).filter(Message.topic_id == topic.id).delete(synchronize_session=False)
        
        for queue in bound_queues:
            db.delete(queue)
            
        db.delete(topic)
        db.commit()

        zk.delete(f"{ZK_NODE_TOPICS}/{topic.id}", recursive=True)

        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_topic = (
                    zk.get_children(f"/servers-metadata/{server}/Topics") or []
                )
                for topic_zk_id in server_topic:
                    if topic_zk_id == str(topic_id):
                        server_ip, _ = server.split(":")
                        Client.send_grpc_topic_delete(
                            topic_id, current_user.id, server_ip + ":8080"
                        )

        return {"message": "Topic deleted successfully", "topic_name": topic.name}

    else:
        was_deleted = False
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_topic = (
                    zk.get_children(f"/servers-metadata/{server}/Topics") or []
                )
                for topic_zk_id in server_topic:
                    if topic_zk_id == str(topic_id):
                        server_ip, _ = server.split(":")
                        Client.send_grpc_topic_delete(
                            topic_id, current_user.id, server_ip + ":8080"
                        )
                    was_deleted = True
        if was_deleted:
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

        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_topic = (
                    zk.get_children(f"/servers-metadata/{server}/Topics") or []
                )
                for topic in server_topic:
                    if topic == str(topic_id):
                        server_ip, _ = server.split(":")
                        response = Client.send_grpc_message(
                            "topic",
                            topic_id,
                            message.content,
                            message.routing_key,
                            server_ip + ":8080",
                        )
                        if response != 1:
                            raise HTTPException(
                                status_code=500,
                                detail="Client wasn't able to save the message",
                            )

        return {
            "message": "Message published successfully",
            "topic_id": existing_topic.id,
            "message_id": new_message.id,
        }
    else:
        was_message_sent = False
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_topic = (
                    zk.get_children(f"/servers-metadata/{server}/Topics") or []
                )
                for topic in server_topic:
                    if topic == str(topic_id):
                        server_ip, _ = server.split(":")
                        response = Client.send_grpc_message(
                            "topic",
                            topic_id,
                            message.content,
                            message.routing_key,
                            server_ip + ":8080",
                        )
                        if response != 1:
                            raise HTTPException(
                                status_code=500,
                                detail="Client wasn't able to save the message",
                            )
                        was_message_sent = True
        if was_message_sent:
            return {
                "message": "Message published successfully",
                "queue_id": "",
                "message_id": "",
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

    if private_queue:
        
        valid_keys_subquery = (
            db.query(QueueRoutingKey.routing_key)
            .filter(QueueRoutingKey.queue_id == private_queue.id)
            .subquery()
        )
        
        messages = (
            db.query(Message)
            .join(QueueMessage, Message.id == QueueMessage.message_id)
             .filter(
                QueueMessage.queue_id == private_queue.id,
                Message.routing_key.in_(valid_keys_subquery)
            )
            .order_by(Message.created_at.asc())
            .all()
        )

        if not messages:
            raise HTTPException(status_code=404, detail="No messages found")

        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_queue = (
                    zk.get_children(f"/servers-metadata/{server}/Queues") or []
                )
                for queue in server_queue:
                    if queue == str(queue_id):
                        server_ip, _ = server.split(":")
                        messages_zk = Client.send_grpc_consume_topic(
                            queue_id,
                            current_user.id,
                            current_user.name,
                            server_ip + ":8080",
                        )

        return {
            "message": "Messages consumed successfully",
            "content": [message.content for message in messages],
            "ids": [message.id for message in messages],
        }
    else:
        was_message_consumed = False
        messages = []
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_queue = (
                    zk.get_children(f"/servers-metadata/{server}/Queues") or []
                )
                for queue in server_queue:
                    if queue == str(queue_id):
                        server_ip, _ = server.split(":")
                        messages = (
                            Client.send_grpc_consume_topic(
                                queue_id,
                                current_user.id,
                                current_user.name,
                                server_ip + ":8080",
                            )
                            or []
                        )
                        was_message_consumed = True
        if was_message_consumed:
            return {
                "message": "Message consumed successfully",
                "content": [message["content"] for message in messages],
                "ids": [message["id"] for message in messages],
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
                user_id=current_user.id,
                topic_id=topic_id,
                is_private=True,
            )

            db.add(private_queue)
            db.commit()
            db.refresh(private_queue)
            zk.ensure_path(f"{ZK_NODE_QUEUES}/{private_queue.id}")

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

        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_topic = (
                    zk.get_children(f"/servers-metadata/{server}/Topics") or []
                )
                for topic_zk in server_topic:
                    if topic_zk == str(topic.topic_id):
                        server_ip, _ = server.split(":")
                        response = Client.send_grpc_topic_subscribe(
                            topic.topic_id,
                            current_user.id,
                            current_user.name,
                            topic.routing_key,
                            server_ip + ":8080",
                            private_queue.id
                        )
                        if response.status_code != 1:
                            raise HTTPException(
                                status_code=500,
                                detail="Client wasn't able to subscribe",
                            )
        return {"message": "Successfully subscribed to the topic"}
    else:
        was_subscribed = False
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_topic = (
                    zk.get_children(f"/servers-metadata/{server}/Topics") or []
                )
                for topic_zk in server_topic:
                    if topic_zk == str(topic.topic_id):
                        server_ip, _ = server.split(":")
                        response = Client.send_grpc_topic_subscribe(
                            topic.topic_id,
                            current_user.id,
                            current_user.name,
                            topic.routing_key,
                            server_ip + ":8080",
                        )
                        if response.status_code != 1:
                            raise HTTPException(
                                status_code=500,
                                detail="Client wasn't able to subscribe",
                            )
                        was_subscribed = True
        if was_subscribed:
            return {
                "message": "Successfully subscribed to the queue",
                "topic_id": topic.topic_id,
            }
    raise HTTPException(status_code=404, detail="Topic not found")


@router.post("/topics/unsubscribe")
async def unsubscribe(
    topic: TopicSubscribe,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        
        existing_private_queue = (
            db.query(Queue)
            .filter(Queue.topic_id == topic.topic_id, Queue.user_id == current_user.id)
            .first()
        )
        
        if existing_private_queue:
            
            queue_id = existing_private_queue.id
            
            routing_key_entry = (
                db.query(QueueRoutingKey)
                .filter(
                    QueueRoutingKey.queue_id == queue_id,
                    QueueRoutingKey.routing_key == topic.routing_key,
                )
                .first()
            )

            if not routing_key_entry:
                raise HTTPException(status_code=404, detail="Routing key not found for queue")

            db.delete(routing_key_entry)
            db.flush()
            db.commit()

            remaining_keys = (
                db.query(QueueRoutingKey)
                .filter(QueueRoutingKey.queue_id == queue_id)
                .count()
            )

            if remaining_keys == 0:
                queue_messages = (
                    db.query(QueueMessage)
                    .filter(QueueMessage.queue_id == queue_id)
                    .all()
                )

                for queue_message in queue_messages:
                    message_id = queue_message.message_id
                    db.delete(queue_message)

                    remaining_refs = (
                        db.query(QueueMessage)
                        .filter(QueueMessage.message_id == message_id)
                        .count()
                    )

                    if remaining_refs == 0:
                        message = db.query(Message).filter(Message.id == message_id).first()
                        if message:
                            db.delete(message)

                db.delete(existing_private_queue)
                db.commit()
            
            servers: list[str] = zk.get_children("/servers") or []
            for server in servers:
                if server != f"{SERVER_IP}:{SERVER_PORT}":
                    server_queues: list[str] = (
                        zk.get_children(f"/servers-metadata/{server}/Queues") or []
                    )
                    for server_queue in server_queues:
                        if int(server_queue) == (queue_id):
                            server_ip, _ = server.split(":")
                            response = Client.send_grpc_topic_unsubscribe(
                                private_queue_id=queue_id,
                                user_id=current_user.id,
                                user_name=current_user.name,
                                remote_host=server_ip + ":8080",
                                topic_id=topic.topic_id,
                                routing_key=topic.routing_key,
                            )
                            if response.status_code != 1:
                                raise HTTPException(
                                    status_code=500,
                                    detail="Client wasn't able to unsubscribe",
                                )

            return {"message": "Successfully unsubscribed from the topic with that routing key."}
        
        else:
            servers: list[str] = zk.get_children("/servers") or []
            for server in servers:
                if server != f"{SERVER_IP}:{SERVER_PORT}":
                    server_topics: list[str] = (
                        zk.get_children(f"/servers-metadata/{server}/Topics") or []
                    )
                    for server_topic_id in server_topics:
                        if int(server_topic_id) == (topic.topic_id):
                            server_ip, _ = server.split(":")
                            response = Client.send_grpc_topic_unsubscribe(
                                private_queue_id=None,
                                user_id=current_user.id,
                                user_name=current_user.name,
                                remote_host=server_ip + ":8080",
                                topic_id=topic.topic_id,
                                routing_key=topic.routing_key,
                            )
                            if response.status_code != 1:
                                raise HTTPException(
                                    status_code=500,
                                    detail="Client wasn't able to unsubscribe",
                                )

            return {"message": "Successfully unsubscribed from the topic with that routing key."}
        
    except Exception as e:
        logger.error(f"Error in unsubscribe: {e}")
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail="Unsubscribe failed due to server error.")


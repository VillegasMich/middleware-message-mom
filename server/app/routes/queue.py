"""
This file defines the routes for managing message queues in the server side application.
It includes endpoints for creating, retrieving, deleting, publishing messages to, consuming messages from,
subscribing to, and unsubscribing from queues. The routes interact with the database, ZooKeeper, and gRPC
services to ensure proper queue management and replication across servers.
"""

from collections import deque
import json
from random import sample
from app.core.auth_helpers import get_current_user
from app.core.database import get_db
from app.core.rrmanager import get_round_robin_manager
from app.grpc.Client import Client
from app.models.message import Message
from app.models.queue import Queue
from app.models.queue_message import QueueMessage
from app.models.user_queue import user_queue as UserQueue
from app.RoundRobinManager import RoundRobinManager
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from zookeeper import SERVER_ADDR, SERVER_IP, SERVER_PORT, ZK_NODE_QUEUES, zk

router = APIRouter()


class QueueCreate(BaseModel):
    name: str


class MessageCreate(BaseModel):
    content: str
    routing_key: str

#Get all queues, either owned by the user or public ones.
@router.get("/queues/")
async def get_queues(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    only_owned: bool = False,
):
    query = db.query(Queue).options(joinedload(Queue.owner))  # Load owner details

    if only_owned:
        query = query.filter(Queue.user_id == current_user.id)
    else:
        query = query.filter(Queue.is_private == False)

    queues = query.all()

    #Send gRPC request to other servers to get their queues
    servers: list[str] = zk.get_children("/servers") or []
    for server in servers:
        if server != f"{SERVER_IP}:{SERVER_PORT}":
            server_ip, _ = server.split(":")
            remote_queues = Client.send_grpc_get_all_queues(server_ip + ":8080") or []
            for remote_queue in remote_queues:
                queues.append(
                    Queue(id=remote_queue.get("id"), name=remote_queue.get("name"))
                )
            # queues.extend(remote_queues)

    seen_ids = set()
    unique_queues = []
    for queue in queues:
        if queue.id not in seen_ids:
            unique_queues.append(queue)
            seen_ids.add(queue.id)

    unique_queues.sort(key=lambda q: q.id)

    return {"message": "Queues listed successfully", "queues": unique_queues}

#Create a new queue, ensuring it doesn't already exist in the current server.
@router.post("/queues/")
async def create_queue(
    queue: QueueCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    round_robin_manager: RoundRobinManager = Depends(get_round_robin_manager),
):
    # Check if the queue exists locally
    existing_queue = db.query(Queue).filter(Queue.name == queue.name).first()
    if existing_queue:
        raise HTTPException(status_code=400, detail="Queue already exists")

    #Set the new queue ID to be the highest ID + 1 across all servers
    new_id = 1
    servers: list[str] = zk.get_children("/servers") or []
    for server in servers:
        server_queues: list[str] = (
            zk.get_children(f"/servers-metadata/{server}/Queues") or []
        )
        for queue_id in server_queues:
            if int(queue_id) >= new_id:
                new_id = int(queue_id) + 1

    new_queue = Queue(
        id=new_id,
        name=queue.name,
        is_private=False,
        user_id=current_user.id,
        is_leader=True,
    )
    db.add(new_queue)
    db.commit()
    db.refresh(new_queue)

    # Choose leader and follower servers
    if len(servers) >= 2:
        print("\n REPLICATION \n")
        servers.remove(SERVER_ADDR)
        follower_ip = sample(servers, 1)[0]
        leader_path = f"{ZK_NODE_QUEUES}/{new_queue.id}"
        follower_path = f"/servers-metadata/{follower_ip}/Queues/{new_queue.id}"
        print("\n FOLLOWER PATH: " + str(follower_path) + "\n")
        zk.ensure_path(ZK_NODE_QUEUES)
        zk.ensure_path(f"/servers-metadata/{follower_ip}/Queues")
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
        response = Client.send_grpc_queue_create(
            new_id,
            queue.name,
            current_user.id,
            server_ip + ":8080",
        )

        # Create ZooKeeper entries
        zk.create(leader_path, payload_leader)
        zk.create(follower_path, payload_follower)

        round_robin_manager.user_queues_dict[new_queue.id] = deque()

        print("\n", "Leader and Follower queues created", "\n")

        return {"message": "Queue created successfully", "queue_id": new_queue.id}

    payload_leader = json.dumps(
        {
            "leader": True,
        }
    ).encode()
    zk.create(f"{ZK_NODE_QUEUES}/{new_queue.id}", payload_leader)
    round_robin_manager.user_queues_dict[new_queue.id] = deque()

    print("\n", "Leader and NO Follower queues created", "\n")

    return {"message": "Queue created successfully", "queue_id": new_queue.id}

#Delete a queue, ensuring the user has permission to do so.
@router.delete("/queues/{queue_id}")
async def delete_queue(
    queue_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    round_robin_manager: RoundRobinManager = Depends(get_round_robin_manager),
):
    queue = db.query(Queue).filter(Queue.id == queue_id).first()

    #Check if the queue exists locally
    if queue:
        if queue.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to delete this queue.",
            )

        # Delete leftover messages in the queue
        queue_messages = (
            db.query(QueueMessage).filter(QueueMessage.queue_id == queue_id).all()
        )

        for queue_message in queue_messages:
            queue_message_id = queue_message.message_id
            db.delete(queue_message)

            message = db.query(Message).filter(Message.id == queue_message_id).first()
            db.delete(message)

        db.delete(queue)
        db.commit()

        zk.delete(f"{ZK_NODE_QUEUES}/{queue_id}", recursive=True)
        round_robin_manager.user_queues_dict.pop(queue_id, None)

        #Propagate the deletion to other servers
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_queues: list[str] = (
                    zk.get_children(f"/servers-metadata/{server}/Queues") or []
                )
                for queue in server_queues:
                    if queue == str(queue_id):
                        server_ip, _ = server.split(":")
                        Client.send_grpc_queue_delete(
                            queue_id, current_user.id, server_ip + ":8080"
                        )

        return {"message": "Queue deleted successfully", "queue_id": queue_id}

    #If the queue doesn't exist locally, check other servers and propagate the deletion
    else:
        was_deleted = False
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_queues: list[str] = (
                    zk.get_children(f"/servers-metadata/{server}/Queues") or []
                )
                for queue in server_queues:
                    if queue == str(queue_id):
                        server_ip, _ = server.split(":")
                        Client.send_grpc_queue_delete(
                            queue_id, current_user.id, server_ip + ":8080"
                        )
                    was_deleted = True
        if was_deleted:
            return {
                "message": "Queue deleted successfully",
                "queue_id": queue_id,
            }
    raise HTTPException(status_code=404, detail="Queue not found.")

#Publish a message to a queue
@router.post("/queues/{queue_id}/publish")
async def publish_message(
    queue_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    existing_queue = db.query(Queue).filter(Queue.id == queue_id).first()
    
    #Check if the queue exists locally
    if existing_queue:
        new_message = Message(
            content=message.content,
            routing_key=message.routing_key,
        )
        db.add(new_message)
        db.flush()

        queue_message = QueueMessage(
            queue_id=existing_queue.id, message_id=new_message.id
        )
        db.add(queue_message)

        db.commit()

        #Propagate the message to other servers
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_queues: list[str] = (
                    zk.get_children(f"/servers-metadata/{server}/Queues") or []
                )
                for queue in server_queues:
                    if queue == str(queue_id):
                        server_ip, _ = server.split(":")
                        response = Client.send_grpc_message(
                            "queue",
                            queue_id,
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
            "queue_id": existing_queue.id,
            "message_id": new_message.id,
        }
        
    #If the queue doesn't exist locally, check other servers and propagate the message    
    else:
        was_message_sent = False
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_queues: list[str] = (
                    zk.get_children(f"/servers-metadata/{server}/Queues") or []
                )
                for queue in server_queues:
                    if queue == str(queue_id):
                        server_ip, _ = server.split(":")
                        response = Client.send_grpc_message(
                            "queue",
                            queue_id,
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
                "message": "Message published successfully"
            }

    raise HTTPException(status_code=404, detail="Queue not found")

#Consume a message from a queue
@router.get("/queues/{queue_id}/consume")
async def consume_message(
    queue_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    round_robin_manager: RoundRobinManager = Depends(get_round_robin_manager),
):
    queue = db.query(Queue).filter(Queue.id == queue_id).first()
    
    #Check if the queue exists locally
    if queue:
        is_subscribed = (
            db.query(UserQueue)
            .filter(
                UserQueue.queue_id == queue_id, UserQueue.user_id == current_user.id
            )
            .first()
        )
        if not is_subscribed:
            raise HTTPException(
                status_code=403, detail="You are not subscribed to this queue."
            )

        expected_user_name = round_robin_manager.user_queues_dict[queue.id][-1]

        #Check if it is the current user's turn to consume the message
        if expected_user_name == current_user.name:
            queue_message = (
                db.query(QueueMessage)
                .join(Message)
                .filter(QueueMessage.queue_id == queue_id)
                .order_by(Message.created_at.asc())
                .with_for_update(skip_locked=True)
                .first()
            )

            if not queue_message:
                raise HTTPException(status_code=404, detail="Message not found")

            message_content = queue_message.message.content
            message_id = queue_message.message_id

            db.delete(queue_message)
            db.flush()

            remaining_refs = (
                db.query(QueueMessage)
                .filter(QueueMessage.message_id == message_id)
                .count()
            )
            if remaining_refs == 0:
                message_to_delete = (
                    db.query(Message).filter(Message.id == message_id).first()
                )
                if message_to_delete:
                    db.delete(message_to_delete)

            db.flush()
            db.commit()

            #Update the round robin queue for the current user
            turn_user = round_robin_manager.user_queues_dict[queue.id].popleft()
            round_robin_manager.user_queues_dict[queue.id].append(turn_user)

            #Propagate the message consumption to other servers
            servers: list[str] = zk.get_children("/servers") or []
            for server in servers:
                if server != f"{SERVER_IP}:{SERVER_PORT}":
                    server_queues: list[str] = (
                        zk.get_children(f"/servers-metadata/{server}/Queues") or []
                    )
                    for queue in server_queues:
                        if queue == str(queue_id):
                            server_ip, _ = server.split(":")
                            response = Client.send_grpc_consume_queue(
                                queue_id,
                                current_user.id,
                                current_user.name,
                                server_ip + ":8080",
                            )

            return {
                "message": "Message consumed successfully",
                "content": message_content,
            }

    #If the queue doesn't exist locally, check other servers and propagate the consumption
    else:
        was_message_consumed = False
        message_content = ""
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_queues: list[str] = (
                    zk.get_children(f"/servers-metadata/{server}/Queues") or []
                )
                for queue in server_queues:
                    if queue == str(queue_id):
                        server_ip, _ = server.split(":")
                        response = Client.send_grpc_consume_queue(
                            queue_id,
                            current_user.id,
                            current_user.name,
                            server_ip + ":8080",
                        )
                        message_content = response.content
                        was_message_consumed = True
        if was_message_consumed:
            return {
                "message": "Message consumed successfully",
                "content": response.content,
            }
    raise HTTPException(status_code=409, detail="Invalid user turn")

#Subscribe a user to a queue
@router.post("/queues/subscribe")
async def subscribe(
    queue_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    round_robin_manager: RoundRobinManager = Depends(get_round_robin_manager),
):
    existing_queue = db.query(Queue).filter(Queue.id == queue_id).first()

    #Check if the queue exists locally
    if existing_queue:

        user_queue_entry = (
            db.query(UserQueue)
            .filter(
                UserQueue.user_id == current_user.id,
                UserQueue.queue_id == existing_queue.id,
            )
            .first()
        )

        if user_queue_entry:
            raise HTTPException(status_code=409, detail="User already subscribed")

        new_subscription = UserQueue(
            user_id=current_user.id, queue_id=existing_queue.id
        )
        db.add(new_subscription)
        db.commit()

        # Update the round robin queue for the current user
        if queue_id not in round_robin_manager.user_queues_dict:
            round_robin_manager.user_queues_dict[queue_id] = deque()

        round_robin_manager.user_queues_dict[queue_id].append(current_user.name)

        # Propagate the subscription to other servers
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_queues: list[str] = (
                    zk.get_children(f"/servers-metadata/{server}/Queues") or []
                )
                for queue in server_queues:
                    if queue == str(queue_id):
                        server_ip, _ = server.split(":")
                        response = Client.send_grpc_queue_subscribe(
                            queue_id,
                            current_user.id,
                            current_user.name,
                            server_ip + ":8080",
                        )
                        if response.status_code != 1:
                            raise HTTPException(
                                status_code=500,
                                detail="Client wasn't able to subscribe",
                            )

        return {"message": "Successfully subscribed to the queue"}
    
    #If the queue doesn't exist locally, check other servers and propagate the subscription
    else:
        was_subscribed = False
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_queues: list[str] = (
                    zk.get_children(f"/servers-metadata/{server}/Queues") or []
                )
                for queue in server_queues:
                    if queue == str(queue_id):
                        server_ip, _ = server.split(":")
                        response = Client.send_grpc_queue_subscribe(
                            queue_id,
                            current_user.id,
                            current_user.name,
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
                "queue_id": queue_id,
            }

    raise HTTPException(status_code=404, detail="Queue not found")

#Unsubscribe a user from a queue
@router.post("/queues/unsubscribe")
async def unsubscribe(
    queue_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    round_robin_manager: RoundRobinManager = Depends(get_round_robin_manager),
):
    existing_queue = db.query(Queue).filter(Queue.id == queue_id).first()

    #Check if the queue exists locally
    if existing_queue:
        user_queue_entry = (
            db.query(UserQueue)
            .filter(
                UserQueue.user_id == current_user.id,
                UserQueue.queue_id == existing_queue.id,
            )
            .first()
        )

        if not user_queue_entry:
            raise HTTPException(status_code=409, detail="User was not subscribed")

        db.delete(user_queue_entry)
        db.commit()

        #Update the round robin queue for the current user
        if queue_id in round_robin_manager.user_queues_dict:
            round_robin_manager.user_queues_dict[queue_id] = deque(
                user
                for user in round_robin_manager.user_queues_dict[queue_id]
                if user != current_user.name
            )

            if not round_robin_manager.user_queues_dict[queue_id]:
                del round_robin_manager.user_queues_dict[queue_id]

        #Propagate the unsubscription to other servers
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_queues: list[str] = (
                    zk.get_children(f"/servers-metadata/{server}/Queues") or []
                )
                for queue in server_queues:
                    if queue == str(queue_id):
                        server_ip, _ = server.split(":")
                        response = Client.send_grpc_queue_unsubscribe(
                            queue_id,
                            current_user.id,
                            current_user.name,
                            server_ip + ":8080",
                        )

        return {"message": "Successfully unsubscribed from the queue"}
    
    #If the queue doesn't exist locally, check other servers and propagate the unsubscription
    else:
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_queues: list[str] = (
                    zk.get_children(f"/servers-metadata/{server}/Queues") or []
                )
                for queue in server_queues:
                    if queue == str(queue_id):
                        server_ip, _ = server.split(":")
                        response = Client.send_grpc_queue_unsubscribe(
                            queue_id,
                            current_user.id,
                            current_user.name,
                            server_ip + ":8080",
                        )
                        if response.status_code != 1:
                            raise HTTPException(
                                status_code=404, detail="Queue not found"
                            )
        return {"message": "Successfully unsubscribed to the queue"}

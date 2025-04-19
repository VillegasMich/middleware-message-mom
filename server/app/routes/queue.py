from collections import deque
import json
import os
from kazoo.exceptions import NodeExistsError
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


@router.post("/queues/")
async def create_queue(
    queue: QueueCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    round_robin_manager: RoundRobinManager = Depends(get_round_robin_manager),
):
    # Check if in the current server the queue exists
    existing_queue = db.query(Queue).filter(Queue.name == queue.name).first()
    if existing_queue:
        raise HTTPException(status_code=400, detail="Queue already exists")

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
        id=new_id, name=queue.name, is_private=False, user_id=current_user.id
    )
    db.add(new_queue)
    db.commit()
    db.refresh(new_queue)


    def _create_or_set(path: str, payload: bytes):
        """
        Crea el znode con `payload`.  
        Si ya existe, lo actualiza con `zk.set`.
        """
        zk.ensure_path(os.path.dirname(path))
        try:
            zk.create(path, payload)
        except NodeExistsError:
            zk.set(path, payload)

    def _json_payload(is_leader: bool) -> bytes:
        return json.dumps({"leader": is_leader}).encode()

    # ---------- dentro de tu función ----------
    if len(servers) >= 2:
        servers.remove(SERVER_ADDR)
        follower_ip = sample(servers, 1)[0]

        leader_path   = f"{ZK_NODE_QUEUES}/{new_queue.id}"
        follower_path = f"/servers-metadata/{follower_ip}/Queues/{new_queue.id}"

        # 1) crea/actualiza los nodos con datos
        _create_or_set(leader_path,   _json_payload(True))
        _create_or_set(follower_path, _json_payload(False))

        # 2) llamar al follower para que cree la cola en su BD
        server_ip, _ = follower_ip.split(":")
        Client.send_grpc_queue_create(
            new_id,
            queue.name,
            current_user.id,
            f"{server_ip}:8080",
        )

        round_robin_manager.user_queues_dict[new_queue.id] = deque()
        return {"message": "Queue created successfully", "queue_id": new_queue.id}

    # ------ caso sin follower ------
    _create_or_set(f"{ZK_NODE_QUEUES}/{new_queue.id}", _json_payload(True))
    round_robin_manager.user_queues_dict[new_queue.id] = deque()
    return {"message": "Queue created successfully", "queue_id": new_queue.id}
    # # Choose leader and follower servers
    # if len(servers) >= 2:
    #     print("\n REPLICATION \n")
    #     servers.remove(SERVER_ADDR)
    #     follower_ip = sample(servers, 1)[0]
    #     leader_path = f"{ZK_NODE_QUEUES}/{new_queue.id}"
    #     follower_path = f"/servers-metadata/{follower_ip}/Queues/{new_queue.id}"
    #     print("\n FOLLOWER PATH: " + str(follower_path) + "\n")
    #     zk.ensure_path(ZK_NODE_QUEUES)
    #     zk.ensure_path(f"/servers-metadata/{follower_ip}/Queues")
    #     # Data to store in ZooKeeper
    #     payload_leader = json.dumps(
    #         {
    #             "leader": True,
    #         }
    #     ).encode()

    #     payload_follower = json.dumps(
    #         {
    #             "leader": False,
    #         }
    #     ).encode()

    #     server_ip, _ = follower_ip.split(":")
    #     response = Client.send_grpc_queue_create(
    #         new_id,
    #         queue.name,
    #         current_user.id,
    #         server_ip + ":8080",
    #     )

    #     # Create ZooKeeper entries
    #     zk.create(leader_path, payload_leader)
    #     zk.create(follower_path, payload_follower)

    #     round_robin_manager.user_queues_dict[new_queue.id] = deque()

    #     print("\n", "Leader and Follower queues created", "\n")

    #     return {"message": "Queue created successfully", "queue_id": new_queue.id}

    # payload_leader = json.dumps(
    #     {
    #         "leader": True,
    #     }
    # ).encode()
    # zk.create(f"{ZK_NODE_QUEUES}/{new_queue.id}", payload_leader)
    # round_robin_manager.user_queues_dict[new_queue.id] = deque()

    # print("\n", "Leader and NO Follower queues created", "\n")

    # return {"message": "Queue created successfully", "queue_id": new_queue.id}


@router.delete("/queues/{queue_id}")
async def delete_queue(
    queue_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    round_robin_manager: RoundRobinManager = Depends(get_round_robin_manager),
):
    queue = db.query(Queue).filter(Queue.id == queue_id).first()

    if queue:
        if queue.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to delete this queue.",
            )

        #Delete leftover messages in the queue
        queue_messages = db.query(QueueMessage).filter(QueueMessage.queue_id == queue_id).all()
        
        for queue_message in queue_messages:
            
            queue_message_id = queue_message.message_id
            db.delete(queue_message)
            
            message = db.query(Message).filter(Message.id == queue_message_id).first()
            db.delete(message)
            
        db.delete(queue)
        db.commit()

        zk.delete(f"{ZK_NODE_QUEUES}/{queue_id}", recursive=True)
        round_robin_manager.user_queues_dict.pop(queue_id, None)

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


@router.post("/queues/{queue_id}/publish")
async def publish_message(
    queue_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    existing_queue = db.query(Queue).filter(Queue.id == queue_id).first()

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

        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_queues: list[str] = (
                    zk.get_children(f"/servers-metadata/{server}/Queues") or []
                )
                for queue in server_queues:
                    print("Searching in servers for queues")
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
    else:
        was_message_sent = False
        servers: list[str] = zk.get_children("/servers") or []
        for server in servers:
            if server != f"{SERVER_IP}:{SERVER_PORT}":
                server_queues: list[str] = (
                    zk.get_children(f"/servers-metadata/{server}/Queues") or []
                )
                for queue in server_queues:
                    print("Searching in servers for queues")
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
                "message": "Message published successfully",
                "queue_id": "",
                "message_id": "",
            }

    raise HTTPException(status_code=404, detail="Queue not found")


@router.get("/queues/{queue_id}/consume")
async def consume_message(
    queue_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    round_robin_manager: RoundRobinManager = Depends(get_round_robin_manager),
):
    queue = db.query(Queue).filter(Queue.id == queue_id).first()
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

            turn_user = round_robin_manager.user_queues_dict[queue.id].popleft()
            round_robin_manager.user_queues_dict[queue.id].append(turn_user)

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


@router.post("/queues/subscribe")
async def subscribe(
    queue_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    round_robin_manager: RoundRobinManager = Depends(get_round_robin_manager),
):
    existing_queue = db.query(Queue).filter(Queue.id == queue_id).first()

    if existing_queue:
        if existing_queue.is_private:
            is_invited = (
                db.query(UserQueue)
                .filter(
                    UserQueue.user_id == current_user.id,
                    UserQueue.queue_id == existing_queue.id,
                )
                .first()
            )
            if not is_invited:
                raise HTTPException(
                    status_code=403, detail="You must be invited to join this queue."
                )

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

        if queue_id not in round_robin_manager.user_queues_dict:
            round_robin_manager.user_queues_dict[queue_id] = deque()

        round_robin_manager.user_queues_dict[queue_id].append(current_user.name)

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


@router.post("/queues/unsubscribe")
async def unsubscribe(
    queue_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    round_robin_manager: RoundRobinManager = Depends(get_round_robin_manager),
):
    existing_queue = db.query(Queue).filter(Queue.id == queue_id).first()

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

        if queue_id in round_robin_manager.user_queues_dict:
            round_robin_manager.user_queues_dict[queue_id] = deque(
                user
                for user in round_robin_manager.user_queues_dict[queue_id]
                if user != current_user.name
            )

            if not round_robin_manager.user_queues_dict[queue_id]:
                del round_robin_manager.user_queues_dict[queue_id]

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
        return {
            "message": "Successfully unsubscribed to the queue"
        }

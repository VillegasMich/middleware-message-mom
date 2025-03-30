from collections import deque

from app.core.auth_helpers import get_current_user
from app.core.database import get_db
from app.core.rrmanager import get_round_robin_manager
from app.grpc.Client import Client
from app.models.message import Message
from app.models.queue import Queue
from app.models.user_queue import user_queue as UserQueue
from app.models.queue_message import QueueMessage
from app.RoundRobinManager import RoundRobinManager
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

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


    # #TEST
    # #------------------------------
    # Client.send_grpc_message(
    #     "queue", 1, "listando todas las queues", "default", "127.0.0.1:8080")
    # #------------------------------

    queues = query.all()
    return {"message": "Queues listed successfully", "queues": queues}


@router.post("/queues/")
async def create_queue(
    queue: QueueCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    round_robin_manager: RoundRobinManager = Depends(get_round_robin_manager),
):
    existing_queue = db.query(Queue).filter(Queue.name == queue.name).first()
    if existing_queue:
        raise HTTPException(status_code=400, detail="Queue already exists")

    new_queue = Queue(name=queue.name, is_private=False, user_id=current_user.id)
    db.add(new_queue)
    db.commit()
    db.refresh(new_queue)

    round_robin_manager.user_queues_dict[new_queue.name] = deque()
    
    return {"message": "Queue created successfully", "queue_id": new_queue.id}


@router.delete("/queues/{queue_name}")
async def delete_queue(
    queue_name: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    round_robin_manager: RoundRobinManager = Depends(get_round_robin_manager),
):
    queue = db.query(Queue).filter(Queue.name == queue_name).first()

    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found.")

    if queue.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this queue.")

    db.delete(queue)
    db.commit()

    round_robin_manager.user_queues_dict.pop(queue_name, None)
    
    return {"message": "Queue deleted successfully", "queue_name": queue_name}


@router.post("/queues/{queue_id}/publish")
async def publish_message(
    queue_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    existing_queue = db.query(Queue).filter(Queue.id == queue_id).first()

    if not existing_queue:
        raise HTTPException(status_code=404, detail="Queue not found")

    new_message = Message(
        content=message.content,
        routing_key=message.routing_key,
    )
    db.add(new_message)
    db.flush()

    queue_message = QueueMessage(queue_id=existing_queue.id, message_id=new_message.id)
    db.add(queue_message)

    db.commit()

    return {
        "message": "Message published successfully",
        "queue_id": existing_queue.id,
        "message_id": new_message.id,
    }


@router.get("/queues/{queue_id}/consume")
async def consume_message(
    queue_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    round_robin_manager: RoundRobinManager = Depends(get_round_robin_manager),
):
    queue = db.query(Queue).filter(Queue.id == queue_id).first()

    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")

    is_subscribed = (
        db.query(UserQueue)
        .filter(UserQueue.queue_id == queue_id, UserQueue.user_id == current_user.id)
        .first()
    )
    if not is_subscribed:
        raise HTTPException(status_code=403, detail="You are not subscribed to this queue.")

    expected_user_name = round_robin_manager.user_queues_dict[queue.name][-1]

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

        db.delete(queue_message)

        remaining_refs = db.query(QueueMessage).filter(QueueMessage.message_id == queue_message.message_id).count()
        if remaining_refs == 0:
            message_to_delete = db.query(Message).filter(Message.id == queue_message.message_id).first()
            if message_to_delete:
                db.delete(message_to_delete)

        db.commit()

        turn_user = round_robin_manager.user_queues_dict[queue.name].popleft()
        round_robin_manager.user_queues_dict[queue.name].append(turn_user)

        return {
            "message": "Message consumed successfully",
            "content": message_content, 
        }

    else:
        raise HTTPException(status_code=409, detail="Invalid user turn")



@router.post("/queues/subscribe")
async def subscribe(
    queue: QueueCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    round_robin_manager: RoundRobinManager = Depends(get_round_robin_manager),
):
    existing_queue = db.query(Queue).filter(Queue.name == queue.name).first()

    if not existing_queue:
        raise HTTPException(status_code=404, detail="Queue not found")

    if existing_queue.is_private:
        is_invited = (
            db.query(UserQueue)
            .filter(UserQueue.user_id == current_user.id, UserQueue.queue_id == existing_queue.id)
            .first()
        )
        if not is_invited:
            raise HTTPException(status_code=403, detail="You must be invited to join this queue.")

    user_queue_entry = (
        db.query(UserQueue)
        .filter(UserQueue.user_id == current_user.id, UserQueue.queue_id == existing_queue.id)
        .first()
    )

    if user_queue_entry:
        raise HTTPException(status_code=409, detail="User already subscribed")

    new_subscription = UserQueue(user_id=current_user.id, queue_id=existing_queue.id)
    db.add(new_subscription)
    db.commit()

    if queue.name not in round_robin_manager.user_queues_dict:
        round_robin_manager.user_queues_dict[queue.name] = deque()

    round_robin_manager.user_queues_dict[queue.name].append(current_user.name)

    return {"message": "Successfully subscribed to the queue"}



@router.post("/queues/unsubscribe")
async def unsubscribe(
    queue: QueueCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    round_robin_manager: RoundRobinManager = Depends(get_round_robin_manager),
):
    existing_queue = db.query(Queue).filter(Queue.name == queue.name).first()

    if not existing_queue:
        raise HTTPException(status_code=404, detail="Queue not found")

    user_queue_entry = (
        db.query(UserQueue)
        .filter(UserQueue.user_id == current_user.id, UserQueue.queue_id == existing_queue.id)
        .first()
    )

    if not user_queue_entry:
        raise HTTPException(status_code=409, detail="User was not subscribed")

    db.delete(user_queue_entry)
    db.commit()

    if queue.name in round_robin_manager.user_queues_dict:
        round_robin_manager.user_queues_dict[queue.name] = deque(
            user for user in round_robin_manager.user_queues_dict[queue.name] if user != current_user.name
        )

        if not round_robin_manager.user_queues_dict[queue.name]:
            del round_robin_manager.user_queues_dict[queue.name]

    return {"message": "Successfully unsubscribed from the queue"}


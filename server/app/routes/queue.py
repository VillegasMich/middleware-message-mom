from collections import deque

from app.core.auth_helpers import get_current_user
from app.core.database import get_db
from app.models.message import Message
from app.models.queue import Queue
from app.RoundRobinManager import RoundRobinManager
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter()


class QueueCreate(BaseModel):
    name: str


class MessageCreate(BaseModel):
    content: str
    routing_key: str


@router.get("/queues/")
async def get_queues(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    only_owned: bool = False,
):
    query = db.query(Queue)

    if only_owned:
        query = query.filter(Queue.user_id == current_user.id)

    queues = query.all()
    return {"message": "Queues listed successfully", "queues": queues}


@router.post("/queues/")
async def create_queue(
    queue: QueueCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    existing_queue = db.query(Queue).filter(Queue.name == queue.name).first()
    if existing_queue:
        raise HTTPException(status_code=400, detail="Queue already exists")

    new_queue = Queue(name=queue.name, user_id=current_user.id)
    db.add(new_queue)
    db.commit()
    db.refresh(new_queue)

    RoundRobinManager.user_queues_dict[new_queue.name] = deque()

    return {"message": "Queue created successfully", "queue_id": new_queue.id}


@router.delete("/queues/{queue_name}")
async def delete_queue(
    queue_name: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    queue = db.query(Queue).filter(Queue.name == queue_name).first()

    if not queue:
        raise HTTPException(
            status_code=404,
            detail="Queue not found or you do not have permission to delete it.",
        )

    db.delete(queue)
    db.commit()

    del RoundRobinManager.user_queues_dict[queue_name]

    return {"message": "Queue deleted successfully", "queue_name": queue_name}


@router.post("/queues/{queue_id}/publish")
async def publish_message(
    queue_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    existing_queue = db.query(Queue).filter(Queue.id == queue_id).first()

    if not existing_queue:
        raise HTTPException(status_code=404, detail="Queue not found")

    new_message = Message(
        content=message.content,
        routing_key=message.routing_key,
        queue_id=existing_queue.id,
    )
    db.add(new_message)
    db.commit()

    return {
        "message": "Message published successfully",
        "queue_id": existing_queue.id,
        "message_id": new_message.id,
    }


# The query is made this way bc we want to ensure two consumers can't consume the same message
@router.get("/queues/{queue_id}/consume")
async def consume_message(
    queue_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    queue = db.query(Queue).filter(Queue.id == queue_id).first()

    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")

    if RoundRobinManager.user_queues_dict[queue.name][-1] == current_user:
        popped_message = (
            db.query(Message)
            .filter(Message.queue_id == queue_id)
            .order_by(Message.created_at.asc())
            .with_for_update(skip_locked=True)
            .first()
        )

        if not popped_message:
            raise HTTPException(status_code=404, detail="Message not found")

        db.delete(popped_message)
        db.commit()

        turn_user = RoundRobinManager[queue.name].pop()
        RoundRobinManager[queue.name].append(turn_user)

        return {
            "message": "Message consumed successfully",
            "content": popped_message.content,
        }

    else:
        raise HTTPException(status_code=404, detail="Invalid user turn")


@router.post("/queues/subscribe")
async def subscribe(
    queue: QueueCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    existing_queue = db.query(Queue).filter(Queue.name == queue.name).first()

    if not existing_queue:
        raise HTTPException(status_code=404, detail="Queue not found")

    existing_queue.users = [current_user]

    db.add(existing_queue)
    db.commit()

    RoundRobinManager.user_queues_dict[queue.name].append(current_user)

    return {"message": "Successfully subscribed to the queue"}

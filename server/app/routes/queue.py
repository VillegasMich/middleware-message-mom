from app.core.database import get_db
from app.models import Queue
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter()


class QueueCreate(BaseModel):
    name: str


@router.get("/queues/")
async def get_queues(db: Session = Depends(get_db)):
    queues = db.query(Queue).all()

    return {"message": "Queues listed successfully", "queues": queues}


# TODO: Add 'creator' created by user ...
@router.post("/queues/")
async def create_queue(queue: QueueCreate, db: Session = Depends(get_db)):
    existing_queue = db.query(Queue).filter(Queue.name == queue.name).first()
    if existing_queue:
        raise HTTPException(status_code=400, detail="Queue already exists")

    new_queue = Queue(name=queue.name)
    db.add(new_queue)
    db.commit()
    db.refresh(new_queue)

    return {"message": "Queue created successfully", "queue_id": new_queue.id}


# TODO: Add user 'creator' verification
@router.delete("/queues/{queue_id}")
async def delete_queue(queue_id: int, db: Session = Depends(get_db)):
    deleted_queue = db.query(Queue).filter(Queue.id == queue_id).first()
    if not deleted_queue:
        raise HTTPException(status_code=404, detail="Queue not found")

    db.delete(deleted_queue)
    db.commit()

    return {"message": "Queue deleted successfully", "queue_id": deleted_queue.id}

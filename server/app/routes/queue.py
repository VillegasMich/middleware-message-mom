from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Queue
from app.core.database import get_db
from pydantic import BaseModel

router = APIRouter()

class QueueCreate(BaseModel):
    name: str

@router.post("/queues/")
def create_queue(queue: QueueCreate, db: Session = Depends(get_db)):

    existing_queue = db.query(Queue).filter(Queue.name == queue.name).first()
    if existing_queue:
        raise HTTPException(status_code=400, detail="Queue already exists")

    new_queue = Queue(name=queue.name)
    db.add(new_queue)
    db.commit()
    db.refresh(new_queue)

    return {"message": "Queue created successfully", "queue_id": new_queue.id}

from app.core.database import get_db
from app.models import Topic
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter()


class TopicCreate(BaseModel):
    name: str
    key: str


@router.get("/topics/")
async def get_topics(db: Session = Depends(get_db)):
    topics = db.query(Topic).all()

    return {"message": "Topics listed successfully", "topics": topics}


# TODO: Add 'creator' created by user ...
@router.post("/topics/")
async def create_topic(topic: TopicCreate, db: Session = Depends(get_db)):
    existing_topic = db.query(Topic).filter(Topic.name == topic.name).first()
    if existing_topic:
        raise HTTPException(status_code=400, detail="Topic already exists")

    new_topic = Topic(name=topic.name, key=topic.key)
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)

    return {"message": "Topic created successfully", "topic_id": new_topic.id}


# TODO: Add user 'creator' verification
@router.delete("/topics/{topic_id}")
async def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    deleted_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not deleted_topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    db.delete(deleted_topic)
    db.commit()

    return {"message": "Topic deleted successfully", "topic_id": deleted_topic.id}

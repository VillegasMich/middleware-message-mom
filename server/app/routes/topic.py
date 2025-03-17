from app.core.database import get_db
from app.models.topic import Topic
from app.models.message import Message
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter()


class TopicCreate(BaseModel):
    name: str

class MessageCreate(BaseModel):
    content: str
    routing_key: str

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

    new_topic = Topic(name=topic.name)
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


@router.post("/topics/{topic_id}/publish")
async def publish_message(topic_id: int, message: MessageCreate, db: Session = Depends(get_db)):
    existing_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not existing_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    new_message = Message(content=message.content, routing_key=message.routing_key, topic_id=existing_topic.id)
    db.add(new_message)
    db.commit()

    return {"message": "Message published successfully", "topic_id": existing_topic.id , "message_id": new_message.id}


@router.get("/topics/{topic_id}/consume")
async def consume_message(topic_id: int, db: Session = Depends(get_db)):
    message = db.query(Message) \
        .filter(Message.topic_id == topic_id) \
        .order_by(Message.created_at.desc()) \
        .first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return {"message": "Message consumed successfully", "content": message.content}



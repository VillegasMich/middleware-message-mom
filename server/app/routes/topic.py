from app.core.auth_helpers import get_current_user
from app.core.database import get_db
from app.models.message import Message
from app.models.topic import Topic
from app.models.user import User
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
async def get_topics(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    only_owned: bool = False,
):
    query = db.query(Topic)

    if only_owned:
        query = query.filter(Topic.user_id == current_user.id)

    topics = query.all()
    return {"message": "Topics listed successfully", "topics": topics}


@router.post("/topics/")
async def create_topic(
    topic: TopicCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    existing_topic = db.query(Topic).filter(Topic.name == topic.name).first()
    if existing_topic:
        raise HTTPException(status_code=400, detail="Topic already exists")

    new_topic = Topic(name=topic.name, user_id=current_user.id)
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)

    return {"message": "Topic created successfully", "topic_id": new_topic.id}


@router.delete("/topics/{topic_name}")
async def delete_topic(
    topic_name: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    topic = db.query(Topic).filter(Topic.name == topic_name).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    if topic.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="You do not have permission to delete this topic"
        )

    db.delete(topic)
    db.commit()

    return {"message": "Topic deleted successfully", "topic_name": topic.name}


@router.post("/topics/{topic_id}/publish")
async def publish_message(
    topic_id: int, message: MessageCreate, db: Session = Depends(get_db)
):
    existing_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not existing_topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    new_message = Message(
        content=message.content,
        routing_key=message.routing_key,
        topic_id=existing_topic.id,
    )
    db.add(new_message)
    db.commit()

    return {
        "message": "Message published successfully",
        "topic_id": existing_topic.id,
        "message_id": new_message.id,
    }


@router.get("/topics/{topic_id}/consume")
async def consume_message(topic_id: int, db: Session = Depends(get_db)):
    message = (
        db.query(Message)
        .filter(Message.topic_id == topic_id)
        .order_by(Message.created_at.asc())
        .first()
    )

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    return {
        "message": "Message consumed successfully",
        "content": message.content,
        "id": message.id,
    }


@router.post("/topics/subscribe")
async def subscribe(
    topic: TopicCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    existing_topic = db.query(Topic).filter(Topic.name == topic.name).first()

    if not existing_topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    if len(existing_topic.users) != 0:
        if current_user not in existing_topic.users:
            existing_topic.users.append(current_user)
    else:
        existing_topic.users = [current_user]

    db.add(existing_topic)
    db.commit()

    return {"message": "Successfully subscribed to the topic"}

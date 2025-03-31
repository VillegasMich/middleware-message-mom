from app.core.auth_helpers import get_current_user
from app.core.database import get_db
from app.models.user import User
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from zookeeper import SERVER_IP, SERVER_PORT, zk

router = APIRouter()


@router.get("/users/topics")
async def get_subscribed_topics(
    db: Session = Depends(get_db), current_user: str = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    servers = zk.get_children("/servers") or []
    for server in servers:
        if server != f"{SERVER_IP}:{SERVER_PORT}":
            server_topics = zk.get_children(f"/servers/{server}/Topics") or []
            for topic in server_topics:
                if topic not in user.topics:
                    user.topics.append(topic)
    return {
        "message": "Successfully subscribed to the topic",
        "topics": user.topics,
    }

from app.routes.queue import router as queue_router
from app.routes.topic import router as topic_router
from app.routes.auth import router as auth_router
from app.routes.user import router as user_router

from fastapi import FastAPI

app = FastAPI()

app.include_router(queue_router)
app.include_router(topic_router)
app.include_router(auth_router)
app.include_router(user_router)

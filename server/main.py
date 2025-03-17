from app.routes.queue import router as queue_router
from app.routes.topic import router as topic_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(queue_router)
app.include_router(topic_router)

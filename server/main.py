from app.routes.queue import router as queue_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(queue_router)

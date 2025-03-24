from app.core.database import get_db
from app.core.rrmanager import round_robin_manager
from app.grpc.Server import Server

from app.routes.auth import router as auth_router
from app.routes.queue import router as queue_router
from app.routes.topic import router as topic_router
from app.routes.user import router as user_router
from fastapi import FastAPI

app = FastAPI()

db = next(get_db())
round_robin_manager.sync_users_queues(db)
db.close()

server = Server()
server.start()

def get_round_robin_manager():
    return round_robin_manager

app.include_router(queue_router)
app.include_router(topic_router)
app.include_router(auth_router)
app.include_router(user_router)

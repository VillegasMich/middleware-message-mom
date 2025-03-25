import os
import socket
from contextlib import asynccontextmanager

import uvicorn
from app.core.database import get_db
from app.core.rrmanager import round_robin_manager
from app.grpc.Server import Server
from app.routes.auth import router as auth_router
from app.routes.queue import router as queue_router
from app.routes.topic import router as topic_router
from app.routes.user import router as user_router
from fastapi import FastAPI
from kazoo.client import KazooClient

ZK_HOST = "localhost:2181"  # LOCAL
# ZK_HOST = "52.21.11.66:2181"  # EC2

zk = KazooClient(hosts=ZK_HOST)
zk.start()


# Server identification
HOSTNAME = socket.gethostname()
SERVER_IP = "127.0.0.1"  # LOCAL
# SERVER_IP = os.getenv("SERVER_ELASTIC_IP")  # EC2
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
ZK_NODE = f"/servers/{SERVER_IP}:{SERVER_PORT}"


db = next(get_db())
round_robin_manager.sync_users_queues(db)
db.close()

server = Server()
server.start()


def get_round_robin_manager():
    return round_robin_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Register server on startup
    zk.ensure_path("/servers")
    zk.create(ZK_NODE, f"{SERVER_IP}:{SERVER_PORT}".encode(), ephemeral=True)
    print(f"Registered: {ZK_NODE}")

    yield

    # Deregister server on shutdown
    if zk.exists(ZK_NODE):
        zk.delete(ZK_NODE)
    zk.stop()
    print(f"Deregistered: {ZK_NODE}")


app = FastAPI(lifespan=lifespan)


app.include_router(queue_router)
app.include_router(topic_router)
app.include_router(auth_router)
app.include_router(user_router)

print(f"🚀 Using SERVER_PORT {SERVER_PORT}")
print(f"ZK NODE: /servers/{SERVER_IP}:{SERVER_PORT}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=SERVER_PORT)

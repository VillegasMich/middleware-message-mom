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
from zookeeper import (
    SERVER_IP,
    SERVER_PORT,
    ZK_NODE,
    ZK_NODE_QUEUES,
    ZK_NODE_TOPICS,
    zk,
)

db = next(get_db())
round_robin_manager.sync_users_queues(db)
db.close()

server = Server()
server.start()


def get_round_robin_manager():
    return round_robin_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    zk.ensure_path("/servers")

    if not zk.exists(ZK_NODE):
        zk.create(ZK_NODE, f"{SERVER_IP}:{SERVER_PORT}".encode(), ephemeral=False)

    zk.ensure_path(ZK_NODE_QUEUES)
    zk.ensure_path(ZK_NODE_TOPICS)

    print(f"Registered: {ZK_NODE} with Queues and Topics")

    yield

    if zk.exists(ZK_NODE):
        zk.delete(ZK_NODE, recursive=True)
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

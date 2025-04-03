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
from zookeeper import (SERVER_IP, SERVER_PORT, ZK_NODE_EPHEMERAL,
                       ZK_NODE_METADATA, ZK_NODE_QUEUES, ZK_NODE_TOPICS,
                       ZK_NODE_USERS, sync_all_queues, sync_all_topics,
                       sync_all_users, zk)

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
    zk.ensure_path("/servers-metadata")
    # if zk.exists(ZK_NODE_METADATA):
    #     zk.delete(ZK_NODE_METADATA, recursive=True)

    zk.create(ZK_NODE_EPHEMERAL, f"{SERVER_IP}:{SERVER_PORT}".encode(), ephemeral=True)

    if not zk.exists(ZK_NODE_METADATA):
        zk.create(
            ZK_NODE_METADATA, f"{SERVER_IP}:{SERVER_PORT}".encode(), ephemeral=False
        )

    zk.ensure_path(ZK_NODE_QUEUES)
    zk.ensure_path(ZK_NODE_TOPICS)
    zk.ensure_path(ZK_NODE_USERS)

    print(f"Registered: {ZK_NODE_METADATA} with Queues and Topics")

    sync_all_queues(db)
    sync_all_topics(db)
    sync_all_users(db)

    yield

    if zk.exists(ZK_NODE_METADATA):
        zk.delete(ZK_NODE_METADATA, recursive=True)

    zk.stop()
    print(f"Deregistered: {ZK_NODE_METADATA}")


app = FastAPI(lifespan=lifespan)


app.include_router(queue_router)
app.include_router(topic_router)
app.include_router(auth_router)
app.include_router(user_router)

print(f"🚀 Using SERVER_PORT {SERVER_PORT}")
print(f"ZK NODE: /servers/{SERVER_IP}:{SERVER_PORT}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=SERVER_PORT)

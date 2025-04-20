"""
This file handles the integration with ZooKeeper for server discovery, metadata management, and synchronization
of queues, topics, and users. It defines constants for ZooKeeper node paths, initializes the ZooKeeper client,
and provides functions to synchronize database entities (queues, topics, and users) with ZooKeeper nodes.
This ensures consistency and coordination across distributed servers in the system.
"""
import json
import os
import socket

from app.grpc import Client
from app.models.queue import Queue
from app.models.topic import Topic
from app.models.user import User
from kazoo.client import KazooClient
from sqlalchemy.orm import Session

# ZK_HOST = "localhost:2181"  # LOCAL
ZK_HOST = "52.21.11.66:2181"  # EC2
# Server identification
HOSTNAME = socket.gethostname()
# SERVER_IP = "127.0.0.1"  # LOCAL
SERVER_IP = os.getenv("SERVER_ELASTIC_IP")  # EC2
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
ZK_NODE_EPHEMERAL = f"/servers/{SERVER_IP}:{SERVER_PORT}"
ZK_NODE_METADATA = f"/servers-metadata/{SERVER_IP}:{SERVER_PORT}"
ZK_NODE_QUEUES = f"{ZK_NODE_METADATA}/Queues"
ZK_NODE_TOPICS = f"{ZK_NODE_METADATA}/Topics"
ZK_NODE_USERS = f"{ZK_NODE_METADATA}/Users"
SERVER_ADDR = f"{SERVER_IP}:{SERVER_PORT}"


zk = KazooClient(hosts=ZK_HOST)
zk.start()


def sync_all_queues(db: Session):
    payload_leader = json.dumps(
        {
            "leader": True,
        }
    ).encode()

    payload_follower = json.dumps(
        {
            "leader": False,
        }
    ).encode()
    queues = db.query(Queue).all()
    for queue in queues:
        queue_path = f"{ZK_NODE_QUEUES}/{queue.id}"
        if not zk.exists(queue_path):
            if queue.is_leader:
                zk.create(queue_path, payload_leader, ephemeral=False)
            else:
                zk.create(queue_path, payload_follower, ephemeral=False)
            print(f"Created ZK node: {queue_path}")
        else:
            print(f"ZK node already exists: {queue_path}")


def sync_all_topics(db: Session):
    topics = db.query(Topic).all()
    for topic in topics:
        topic_path = f"{ZK_NODE_TOPICS}/{topic.id}"
        if not zk.exists(topic_path):
            zk.create(topic_path, b"", ephemeral=False)
            print(f"Created ZK node: {topic_path}")
        else:
            print(f"ZK node already exists: {topic_path}")


def sync_all_users(db: Session):
    users = db.query(User).all()
    for user in users:
        user_path = f"{ZK_NODE_USERS}/{user.id}"
        if not zk.exists(user_path):
            zk.create(user_path, b"", ephemeral=False)
            print(f"Created ZK node: {user_path}")
        else:
            print(f"ZK node already exists: {user_path}")

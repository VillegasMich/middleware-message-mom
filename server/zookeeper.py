import os
import socket

from kazoo.client import KazooClient

ZK_HOST = "localhost:2181"  # LOCAL
# ZK_HOST = "52.21.11.66:2181"  # EC2
# Server identification
HOSTNAME = socket.gethostname()
SERVER_IP = "127.0.0.1"  # LOCAL
# SERVER_IP = os.getenv("SERVER_ELASTIC_IP")  # EC2
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
ZK_NODE = f"/servers/{SERVER_IP}:{SERVER_PORT}"
ZK_NODE_QUEUES = f"{ZK_NODE}/Queues"
ZK_NODE_TOPICS = f"{ZK_NODE}/Topics"


zk = KazooClient(hosts=ZK_HOST)
zk.start()

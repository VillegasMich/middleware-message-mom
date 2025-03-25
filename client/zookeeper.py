import random

from kazoo.client import KazooClient

ZK_HOST = "localhost:2181"  # LOCAL
# ZK_HOST = "52.21.11.66:2181"  # EC2

zk = KazooClient(hosts=ZK_HOST)
zk.start()


def get_server():
    if not zk.exists("/servers"):
        print("No servers available!")
        return None

    servers = zk.get_children("/servers")  # List of registered servers
    if not servers:
        print("No servers found!")
        return None

    server_node = random.choice(servers)  # Select a random server
    server_data, _ = zk.get(f"/servers/{server_node}")  # Get IP:Port
    print("Connected to server", server_data)
    return server_data.decode()

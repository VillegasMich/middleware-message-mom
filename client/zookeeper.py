from random import randint
from kazoo.client import KazooClient

# ZK_HOST = "localhost:2181"  # LOCAL
ZK_HOST = "52.21.11.66:2181"  # EC2

zk = KazooClient(hosts=ZK_HOST)
zk.start()

server_list = []
current_index_server = 0


def refresh_servers():
    global server_list, current_index

    if not zk.exists("/servers"):
        print("No servers available!")
        server_list = []
        return

    server_list = zk.get_children("/servers") or []
    current_index = randint(
        0, len(server_list) - 1
    )  # Reset index if the list is refreshed


def get_server():
    global current_index

    if not server_list:
        refresh_servers()
        if not server_list:
            print("No servers found!")
            return None

    server_node = server_list[current_index]
    current_index = (current_index + 1) % len(server_list)  # Move to next server

    server_data, _ = zk.get(f"/servers/{server_node}")
    print("Connected to server", server_data.decode())
    return server_data.decode()

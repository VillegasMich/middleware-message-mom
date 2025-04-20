import os
import threading
from concurrent import futures
import grpc
import json

from . import Service_pb2, Service_pb2_grpc
from ..core.database import get_db
from .services.MessageService import MessageService
from .services.QueueService import QueueService
from .services.TopicService import TopicService
from .services.UserService import UserService
from .Client import Client
from ..repository.QueueRepository import QueueRepository
from zookeeper import SERVER_ADDR, SERVER_IP, SERVER_PORT, ZK_NODE_QUEUES, zk


# os.environ["GRPC_VERBOSITY"] = "debug"
# os.environ["GRPC_TRACE"] = "all"

GRPC_PORT = int(os.getenv("GRPC_PORT", 8080))
PUBLIC_IP = os.getenv("PUBLIC_IP")
HOST = f"{PUBLIC_IP}:" + str(GRPC_PORT)


class Server:
    """
    This class manages the gRPC server lifecycle for the middleware.
    It provides methods to start and stop the server, initialize threads for listening to incoming requests,
    and synchronize follower queues using ZooKeeper. This class integrates various gRPC services such as
    MessageService, QueueService, TopicService, and UserService to handle client requests.
    """
    
    def __init__(self):
        self.running = False

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.listen, daemon=True)
            self.thread.start()

    def stop(self):
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join()

    def sync_follower_queues(self):
        server_queues: list[str] = (
            zk.get_children(f"/servers-metadata/{SERVER_ADDR}/Queues") or []
        )
        servers: list[str] = zk.get_children("/servers") or []
        for queue in server_queues:
            data_bytes,_  = zk.get(f"/servers-metadata/{SERVER_ADDR}/Queues/{queue}")
            print(data_bytes)
            if data_bytes:
                # Decodes de metadata from the local server
                try:
                    metadata = json.loads(data_bytes.decode("utf-8"))
                except json.JSONDecodeError:
                    print(f"{data_bytes!r}")
                    continue

                # Checks if the servers isn't leader of this queue
                if(metadata['leader'] == False):
                    db = next(get_db())
                    queue_repo = QueueRepository(db)
                    db.close()
                    # Looks in all of the servers for the leader server (Could be optimized by putting the owner inside the payload in the zk)
                    for server in servers:
                        remote_queues: list[str] = (
                            zk.get_children(f"/servers-metadata/{server}/Queues") or []
                        )
                        if queue in remote_queues:
                            remote_data_bytes,_  = zk.get(f"/servers-metadata/{server}/Queues/{queue}")
                            remote_metadata = json.loads(remote_data_bytes.decode("utf-8"))
                            if remote_metadata['leader'] == True:
                                server_ip, _ = server.split(":")
                                messages = Client.send_grpc_get_queue_messages(int(queue),server_ip + ":8080")
                                payload = {'messages':messages, 'id':queue}
                                queue_repo.sync_follower_queue(payload)


            else:
                print(f"Empty node (no data)")

    #Init the thread that listens for new incoming requests in this MOM.
    @staticmethod
    def listen():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        Service_pb2_grpc.add_MessageServiceServicer_to_server(MessageService(), server)
        Service_pb2_grpc.add_QueueServiceServicer_to_server(QueueService(), server)
        Service_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
        Service_pb2_grpc.add_TopicServiceServicer_to_server(TopicService(), server)
        server.add_insecure_port(HOST)
        print(f"Production service started on {HOST} ")
        server.start()
        server.wait_for_termination()

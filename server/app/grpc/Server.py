import os
import threading
from concurrent import futures
import grpc

from . import Service_pb2, Service_pb2_grpc
from ..core.database import get_db
from .services.MessageService import MessageService
from .services.QueueService import QueueService
from .services.TopicService import TopicService
from .services.UserService import UserService
from .Client import Client
from zookeeper import SERVER_ADDR, SERVER_IP, SERVER_PORT, ZK_NODE_QUEUES, zk


# os.environ["GRPC_VERBOSITY"] = "debug"
# os.environ["GRPC_TRACE"] = "all"

GRPC_PORT = int(os.getenv("GRPC_PORT", 8080))
PUBLIC_IP = os.getenv("PUBLIC_IP")
HOST = f"{PUBLIC_IP}:" + str(GRPC_PORT)


class Server:
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
            zk.get(f"/servers-metadata/{SERVER_ADDR}/Queues") or []
        )
        print('------------------------------------------')
        print(server_queues)
        print('------------------------------------------')

    """
        Init the thread that listens for new incoming requests in this MOM.
    """
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

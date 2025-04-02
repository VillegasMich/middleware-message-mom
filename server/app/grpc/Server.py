import os
import threading
from concurrent import futures
import socket
import grpc

from . import Service_pb2, Service_pb2_grpc
from ..core.database import get_db
from ..models.message import Message
from ..models.queue_message import QueueMessage
# os.environ["GRPC_VERBOSITY"] = "debug"
# os.environ["GRPC_TRACE"] = "all"

GRPC_PORT = int(os.getenv("GRPC_PORT", 8080))  
PUBLIC_IP = os.getenv("PUBLIC_IP")
HOST = f"{PUBLIC_IP}:" + str(GRPC_PORT)

print(HOST)


class MessageService(Service_pb2_grpc.MessageServiceServicer):
    """
    Here the message should be saved in the queue or topic received.
    """

    def AddMessage(self, request, context):
        
        db = next(get_db())
        
        new_message = Message(
            content=request.content,
            routing_key=request.routing_key,
        )

        db.add(new_message)
        db.flush()

        queue_message = QueueMessage(
            queue_id=request.id, message_id=new_message.id
        )
        
        db.add(queue_message)
        db.commit() 

        db.close()
        
        print("Request is received: " + str(request))
        return Service_pb2.MessageResponse(status_code=1)


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

    """
        Init the thread that listens for new incoming requests in this MOM.
    """

    @staticmethod
    def listen():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        Service_pb2_grpc.add_MessageServiceServicer_to_server(MessageService(), server)
        server.add_insecure_port(HOST)
        print(f"Production service started on {HOST} ")
        server.start()
        server.wait_for_termination()


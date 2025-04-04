import os
import threading
from concurrent import futures
import grpc

from . import Service_pb2, Service_pb2_grpc
from ..core.database import get_db
from ..repository.MessageRepository import MessageRepository
from ..repository.QueueRepository import QueueRepository

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
        repo = MessageRepository(db)

        if request.type == 'queue':
            repo.save_queue_message(request)
        elif request.type == 'topic':
            repo.save_topic_message(request)

        db.close()
        print("Request is received: " + str(request))
        return Service_pb2.MessageResponse(status_code=1)

    def ConsumeMessage(self, request, context):
        db = next(get_db())
        repo = MessageRepository(db)
        content = repo.consume_message(request)
        db.close()
        print("Request is received: " + str(request))
        return Service_pb2.ConsumeMessageResponse(status_code=1, content=content)
    
class QueueService(Service_pb2_grpc.QueueServiceServicer):
    
    def GetQueues(self, request, context):
        db = next(get_db())
        repo = QueueRepository(db)
        queues = repo.all()
        db.close()
        
        response = Service_pb2.GetQueuesResponse()

        print(queues)

        for queue in queues:
            queue_item = response.queues.add()
            queue_item.id = queue.id
            queue_item.name = queue.name
        
        print("Request is received: " + str(request))
        return response
    
    def Delete(self, request, context):

        print("Request is received: " + str(request))
        return Service_pb2.CRUDResponse(status_code=1)
    
    def Subscribe(self, request, context):
        
        db = next(get_db())
        
        repo = QueueRepository(db)
        repo.subscribe_queue(request)
        
        db.close()
        print("Request is received: " + str(request))
        return Service_pb2.SubscribeResponse(status_code=1)
    
    def UnSubscribe(self, request, context):

        print("Request is received: " + str(request))
        return Service_pb2.SubscribeResponse(status_code=1)


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
        Service_pb2_grpc.add_MessageServiceServicer_to_server(
            MessageService(), server)
        Service_pb2_grpc.add_QueueServiceServicer_to_server(
            QueueService(), server)
        server.add_insecure_port(HOST)
        print(f"Production service started on {HOST} ")
        server.start()
        server.wait_for_termination()

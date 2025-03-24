
from concurrent import futures
import grpc
from . import Service_pb2
from . import Service_pb2_grpc
import threading

HOST = '127.0.0.1:8080'

class MessageService(Service_pb2_grpc.MessageServiceServicer):
   
   '''
        Here the message should be saved in the queue or topic received.
   '''
   def AddMessage(self, request, context):
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

    '''
        Init the thread that listens for new incoming requests in this MOM.
    '''
    @staticmethod
    def listen():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        Service_pb2_grpc.add_MessageServiceServicer_to_server(MessageService(), server)
        server.add_insecure_port(HOST)
        print("Production service started on port 8080")
        server.start()
        server.wait_for_termination()
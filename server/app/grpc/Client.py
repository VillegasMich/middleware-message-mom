import os
import grpc
from . import Service_pb2
from . import Service_pb2_grpc

from dotenv import load_dotenv

load_dotenv()

PROTO_PATH = os.getenv("PROTO_PATH")  
REMOTE_HOST = os.getenv("REMOTE_HOST", "localhost:8080")

class Client:


    '''
        Sends the protobuf message to the remote_host (ipv4), the remote_host must see if the queue or topic exists
        within him, create the message and save it. 
    '''
    @staticmethod
    def send_grpc_message(content:str, routing_key:str, remote_host:str, queue_id:int = None,topic_id:int = None):

        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.MessageServiceStub(channel)
            
            request = Service_pb2.Message(queue_id=queue_id, topic_id=topic_id, routing_key=routing_key, content=content)

            try:
                response = stub.AddMessage(request)
                print("Response received from remote service:", response)
            except grpc.RpcError as e:
                print(f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

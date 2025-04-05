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
    def send_grpc_message(obj_type: str, obj_id: int, content: str, routing_key: str, remote_host: str):

        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.MessageServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.Message(
                id=obj_id, type=obj_type, routing_key=routing_key, content=content)
            try:
                response = stub.AddMessage(request)
                print("Response received from remote service:", response)
                return response.status_code
            except grpc.RpcError as e:
                print(
                    f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

    '''
        Sends the protobuf Queue subscribeRequest to the remote_host (ipv4).
    '''
    @staticmethod
    def send_grpc_queue_subscribe(queue_id: int, user_id: int, user_name: str, remote_host: str):
        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.QueueServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.SubscribeRequest(
                queue_id=queue_id, user_id=user_id, user_name=user_name)
            try:
                response = stub.Subscribe(request)
                print("Response received from remote service:", response)
                return response
            except grpc.RpcError as e:
                print(
                    f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

    @staticmethod
    def send_grpc_topic_subscribe(topic_id: int, user_id: int, user_name: str, routing_key: str, remote_host:str):
         with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.TopicServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.SubscribeTopicRequest(
                topic_id=topic_id, user_id=user_id, user_name=user_name, routing_key=routing_key)
            try:
                response = stub.Subscribe(request)
                print("Response received from remote service:", response)
                return response
            except grpc.RpcError as e:
                print(
                    f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

    '''
        Gets all queues from the remote_host, the queues should be parsed to dict after they are returned
    '''
    @staticmethod
    def send_grpc_get_all_queues(remote_host: str):
        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.QueueServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.GetQueuesRequest(allQueues=1)
            try:
                response = stub.GetQueues(request)
                print("Response received from remote service:", response)
                remote_queues_list = [{'id': q.id, 'name': q.name}
                                      for q in response.queues]
                return remote_queues_list
            except grpc.RpcError as e:
                print(
                    f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

    @staticmethod
    def send_grpc_consume_queue(queue_id: int, user_id: int, user_name: str, remote_host: str):
        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.MessageServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.ConsumeMessageRequest(
                id=queue_id, user_name=user_name, user_id=user_id)
            try:
                response = stub.ConsumeMessage(request)
                print("Response received from remote service:", response)
                return response
            except grpc.RpcError as e:
                print(
                    f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

    @staticmethod
    def send_grpc_register(user_name: str, user_password: str, user_id: int, remote_host: str):
        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.UserServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.RegisterRequest(
                user_name=user_name, user_password=user_password, user_id=user_id)
            try:
                response = stub.Register(request)
                print("Response received from remote service:", response)
                return response
            except grpc.RpcError as e:
                print(
                    f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

    @staticmethod
    def send_grpc_get_all_topics(remote_host: str):
        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.TopicServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.GetTopicsRequest(allTopics=1)
            try:
                response = stub.GetTopics(request)
                print("Response received from remote service:", response)
                remote_topics_list = [{'id': t.id, 'name': t.name}
                                      for t in response.topic]
                return remote_topics_list
            except grpc.RpcError as e:
                print(
                    f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

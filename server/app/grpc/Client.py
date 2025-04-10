import os
import grpc
from . import Service_pb2
from . import Service_pb2_grpc

from dotenv import load_dotenv

load_dotenv()

PROTO_PATH = os.getenv("PROTO_PATH")
REMOTE_HOST = os.getenv("REMOTE_HOST", "localhost:8080")


class Client:
    """
    Sends the protobuf message to the remote_host (ipv4), the remote_host must see if the queue or topic exists
    within him, create the message and save it.
    """

    @staticmethod
    def send_grpc_message(
        obj_type: str, obj_id: int, content: str, routing_key: str, remote_host: str
    ):
        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.MessageServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.Message(
                id=obj_id, type=obj_type, routing_key=routing_key, content=content
            )
            try:
                response = stub.AddMessage(request)
                print("Response received from remote service:", response)
                return response.status_code
            except grpc.RpcError as e:
                print(f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

    """
        Sends the protobuf Queue subscribeRequest to the remote_host (ipv4).
    """

    @staticmethod
    def send_grpc_queue_subscribe(
        queue_id: int, user_id: int, user_name: str, remote_host: str
    ):
        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.QueueServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.SubscribeRequest(
                queue_id=queue_id, user_id=user_id, user_name=user_name
            )
            try:
                response = stub.Subscribe(request)
                print("Response received from remote service:", response)
                return response
            except grpc.RpcError as e:
                print(f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

    @staticmethod
    def send_grpc_queue_unsubscribe(
        queue_id: int, user_id: int, user_name: str, remote_host: str
    ):
        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.QueueServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.SubscribeRequest(
                queue_id=queue_id, user_id=user_id, user_name=user_name
            )
            try:
                response = stub.UnSubscribe(request)
                print("Response received from remote service:", response)
                return response
            except grpc.RpcError as e:
                print(f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

    @staticmethod
    def send_grpc_topic_subscribe(
        topic_id: int, user_id: int, user_name: str, routing_key: str, remote_host: str
    ):
        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.TopicServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.SubscribeTopicRequest(
                topic_id=topic_id,
                user_id=user_id,
                user_name=user_name,
                routing_key=routing_key,
            )
            try:
                response = stub.Subscribe(request)
                print("Response received from remote service:", response)
                return response
            except grpc.RpcError as e:
                print(f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

    """
        Gets all queues from the remote_host, the queues should be parsed to dict after they are returned
    """

    @staticmethod
    def send_grpc_get_all_queues(remote_host: str):
        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.QueueServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.GetQueuesRequest(allQueues=1)
            try:
                response = stub.GetQueues(request)
                print("Response received from remote service:", response)
                remote_queues_list = [
                    {"id": q.id, "name": q.name} for q in response.queues
                ]
                return remote_queues_list
            except grpc.RpcError as e:
                print(f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

    @staticmethod
    def send_grpc_consume_queue(
        queue_id: int, user_id: int, user_name: str, remote_host: str
    ):
        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.MessageServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.ConsumeMessageRequest(
                id=queue_id, user_name=user_name, user_id=user_id
            )
            try:
                response = stub.ConsumeQueueMessage(request)
                print("Response received from remote service:", response)
                return response
            except grpc.RpcError as e:
                print(f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

    @staticmethod
    def send_grpc_consume_topic(
        topic_id: int, user_id: int, user_name: str, remote_host: str
    ):
        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.MessageServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.ConsumeMessageRequest(
                id=topic_id, user_name=user_name, user_id=user_id
            )
            try:
                response = stub.ConsumeTopicMessage(request)
                print("Consume Response received from remote service:", response)
                remote_messages_list = [m for m in response.messages]
                result = [
                    {"content": m.content, "id": m.id} for m in remote_messages_list
                ]
                return result
            except grpc.RpcError as e:
                print(f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

    @staticmethod
    def send_grpc_register(
        user_name: str, user_password: str, user_id: int, remote_host: str
    ):
        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.UserServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.RegisterRequest(
                user_name=user_name, user_password=user_password, user_id=user_id
            )
            try:
                response = stub.Register(request)
                print("Response received from remote service:", response)
                return response
            except grpc.RpcError as e:
                print(f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

    @staticmethod
    def send_grpc_get_all_topics(remote_host: str):
        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.TopicServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.GetTopicsRequest(allTopics=1)
            try:
                response = stub.GetTopics(request)
                print("Response received from remote service:", response)
                remote_topics_list = [
                    {"id": t.id, "name": t.name} for t in response.topic
                ]
                return remote_topics_list
            except grpc.RpcError as e:
                print(f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

    @staticmethod
    def send_grpc_get_all_topic_queues(user_id: int, remote_host: str):
        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.UserServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.GetUserTopicQueuesRequest(user_id=user_id)
            try:
                response = stub.GetUserTopicQueues(request)
                print("Response received from remote service:", response)
                remote_queues_list = [
                    {"id": q.id, "name": q.name} for q in response.queues
                ]
                return remote_queues_list
            except grpc.RpcError as e:
                print(f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

    @staticmethod
    def send_grpc_queue_delete(queue_id: int, user_id: str, remote_host: str):
        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.QueueServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.DeleteRequest(id=queue_id, user_id=user_id)
            try:
                response = stub.Delete(request)
                print("Response received from remote service:", response)
                return response
            except grpc.RpcError as e:
                print(f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

    @staticmethod
    def send_grpc_topic_delete(topic_id: int, user_id: str, remote_host: str):
        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.TopicServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.DeleteRequest(id=topic_id, user_id=user_id)
            try:
                response = stub.Delete(request)
                print("Response received from remote service:", response)
                return response
            except grpc.RpcError as e:
                print(f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

    @staticmethod
    def send_grpc_queue_create(
        queue_id: int, queue_name: str, user_id: str, remote_host: str
    ):
        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.QueueServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.CreateQueueRequest(
                id=queue_id, name=queue_name, user_id=user_id
            )
            try:
                response = stub.CreateQueues(request)
                print("Response received from remote service:", response)
                return response
            except grpc.RpcError as e:
                print(f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

    @staticmethod
    def send_grpc_topic_create(
        topic_id: int, topic_name: str, user_id: str, remote_host: str
    ):
        with grpc.insecure_channel(remote_host) as channel:
            stub = Service_pb2_grpc.TopicServiceStub(channel)
            print(dir(stub))
            request = Service_pb2.CreateTopicsRequest(
                id=topic_id, name=topic_name, user_id=user_id
            )
            try:
                response = stub.CreateTopics(request)
                print("Response received from remote service:", response)
                return response
            except grpc.RpcError as e:
                print(f"Error al llamar al servicio gRPC: {e.code()} - {e.details()}")

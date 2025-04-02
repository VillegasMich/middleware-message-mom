import os
import threading
from concurrent import futures
import fnmatch

from fastapi import HTTPException
import grpc

from . import Service_pb2, Service_pb2_grpc
from ..core.database import get_db
from ..repository.MessageRepository import MessageRepository
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
            # new_message = Message(
            #     content=request.content,
            #     routing_key=request.routing_key,
            # )

            # db.add(new_message)
            # db.flush()

            # queue_message = QueueMessage(
            #     queue_id=request.id, message_id=new_message.id
            # )

            # db.add(queue_message)
            # db.commit()

        elif request.type == 'topic':
            repo.save_topic_message(request)
            # routing_key = request.routing_key

            # new_message = Message(
            #     content=request.content,
            #     routing_key=routing_key,
            #     topic_id=request.id,
            # )

            # db.add(new_message)
            # db.flush()

            # if not new_message.id:
            #     raise HTTPException(status_code=500, detail="Failed to create message.")

            # all_queues = (
            #     db.query(Queue)
            #     .join(QueueRoutingKey, Queue.id == QueueRoutingKey.queue_id)
            #     .filter(Queue.topic_id == request.id)
            #     .all()
            # )

            # matching_queues = [
            #     queue
            #     for queue in all_queues
            #     if any(
            #         fnmatch.fnmatch(routing_key, qr.routing_key)
            #         for qr in queue.routing_keys
            #     )
            # ]

            # queue_messages = [
            #     QueueMessage(queue_id=queue.id, message_id=new_message.id)
            #     for queue in matching_queues
            # ]
            # db.add_all(queue_messages)
            # db.commit()

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
        Service_pb2_grpc.add_MessageServiceServicer_to_server(
            MessageService(), server)
        server.add_insecure_port(HOST)
        print(f"Production service started on {HOST} ")
        server.start()
        server.wait_for_termination()

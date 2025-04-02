import os
import threading
from concurrent import futures
import fnmatch

import grpc
from fastapi import Depends, HTTPException
from collections import deque

from . import Service_pb2, Service_pb2_grpc
from ..core.database import get_db
from ..repository.MessageRepository import MessageRepository
from ..models.queue import Queue
from ..models.user_queue import user_queue as UserQueue
from ..RoundRobinManager import RoundRobinManager
from app.core.rrmanager import get_round_robin_manager

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
        print("Request is received: " + str(request))
        return Service_pb2.ConsumeMessageResponse(status_code=1)


class SubscribeQueueService(Service_pb2_grpc.SubscribeQueueServiceServicer):

    def Subscribe(self, request, context):
        db = next(get_db())
        round_robin_manager: RoundRobinManager = get_round_robin_manager()

        existing_queue = db.query(Queue).filter(
            Queue.id == request.queue_id).first()

        if existing_queue.is_private:
            is_invited = (
                db.query(UserQueue)
                .filter(
                    UserQueue.user_id == request.user_id,
                    UserQueue.queue_id == existing_queue.id,
                )
                .first()
            )
            if not is_invited:
                raise HTTPException(
                    status_code=403, detail="You must be invited to join this queue."
                )

        user_queue_entry = (
            db.query(UserQueue)
            .filter(
                UserQueue.user_id == request.user_id,
                UserQueue.queue_id == existing_queue.id,
            )
            .first()
        )

        if user_queue_entry:
            raise HTTPException(
                status_code=409, detail="User already subscribed")

        new_subscription = UserQueue(
            user_id=request.user_id, queue_id=existing_queue.id
        )
        db.add(new_subscription)
        db.commit()

        if request.queue_id not in round_robin_manager.user_queues_dict:
                round_robin_manager.user_queues_dict[request.queue_id] = deque()

        round_robin_manager.user_queues_dict[request.queue_id].append(request.user_name)
        print(round_robin_manager.user_queues_dict)

        db.close()
        print("Request is received: " + str(request))
        return Service_pb2.SubscribeResponse(status_code=1, user_name=request.user_name)


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
        Service_pb2_grpc.add_SubscribeQueueServiceServicer_to_server(
            SubscribeQueueService(), server)
        server.add_insecure_port(HOST)
        print(f"Production service started on {HOST} ")
        server.start()
        server.wait_for_termination()

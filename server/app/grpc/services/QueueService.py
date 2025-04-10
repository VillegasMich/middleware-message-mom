from typing import override
from .. import Service_pb2, Service_pb2_grpc
from ...core.database import get_db
from ...repository.QueueRepository import QueueRepository


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
        db = next(get_db())

        repo = QueueRepository(db)
        repo.delete(request)

        db.close()

        print("Request is received: " + str(request))
        return Service_pb2.CRUDResponse(status_code=1)

    def Subscribe(self, request, context):
        db = next(get_db())

        repo = QueueRepository(db)
        repo.subscribe(request)

        db.close()
        print("Request is received: " + str(request))
        return Service_pb2.SubscribeResponse(status_code=1)

    def UnSubscribe(self, request, context):
        db = next(get_db())

        repo = QueueRepository(db)
        repo.unsubscribe(request)

        db.close()
        print("Request is received: " + str(request))
        return Service_pb2.SubscribeResponse(status_code=1)

    def CreateQueues(self, request, context):
        db = next(get_db())

        repo = QueueRepository(db)
        repo.create(request)

        db.close()
        print("Request is received: " + str(request))
        return Service_pb2.CRUDResponse(status_code=1)

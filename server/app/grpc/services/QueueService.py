from typing import override
from .. import Service_pb2, Service_pb2_grpc
from ...core.database import get_db
from ...repository.QueueRepository import QueueRepository


class QueueService(Service_pb2_grpc.QueueServiceServicer):
    """
    This class implements the gRPC service for managing queues.
    It provides methods to retrieve, create, delete, subscribe, unsubscribe, and synchronize queues.
    This class interacts with the database through the QueueRepository to perform the required operations.
    """
    
    def GetQueues(self, request, context):
        #Handle the retrieval of all queues.
        
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
        #Handle the deletion of a queue.
        
        db = next(get_db())

        repo = QueueRepository(db)
        repo.delete(request)

        db.close()

        print("Request is received: " + str(request))
        return Service_pb2.CRUDResponse(status_code=1)

    def Subscribe(self, request, context):
        #Handle the subscription to a queue.
        
        db = next(get_db())

        repo = QueueRepository(db)
        repo.subscribe(request)

        db.close()
        print("Request is received: " + str(request))
        return Service_pb2.SubscribeResponse(status_code=1)

    def UnSubscribe(self, request, context):
        #Handle the unsubscription from a queue.
        
        db = next(get_db())

        repo = QueueRepository(db)
        repo.unsubscribe(request)

        db.close()
        print("Request is received: " + str(request))
        return Service_pb2.SubscribeResponse(status_code=1)

    def CreateQueues(self, request, context):
        #Handle the creation of a new queue.
        
        db = next(get_db())

        repo = QueueRepository(db)
        repo.create(request)

        db.close()
        print("Request is received: " + str(request))
        return Service_pb2.CRUDResponse(status_code=1)

    def SyncQueues(self, request, context):
        #Handle the synchronization of queues.
        
        db = next(get_db())
        repo = QueueRepository(db)
        messages = repo.sync_queues(request)
        db.close()

        if messages:
            response = Service_pb2.SyncResponse(status_code=1)
            
            print(messages)
            for message in messages:
                message_item = response.messages.add()
                message_item.id = message.id
                message_item.type = 'queue'
                message_item.routing_key = message.routing_key
                message_item.content = message.content
            
            print("Request is received: " + str(request))
            
            return response
        else:
            return Service_pb2.SyncResponse(status_code=0)  

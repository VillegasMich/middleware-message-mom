from .. import Service_pb2, Service_pb2_grpc
from ...core.database import get_db
from ...repository.MessageRepository import MessageRepository

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
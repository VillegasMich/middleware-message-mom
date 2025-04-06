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

    def ConsumeQueueMessage(self, request, context):
        db = next(get_db())
        repo = MessageRepository(db)
        content = repo.consume_queue_message(request)
        db.close()
        print("Request is received: " + str(request))
        return Service_pb2.ConsumeMessageResponse(status_code=1, content=content)
    
    def ConsumeTopicMessage(self, request, context):
        db = next(get_db())
        repo = MessageRepository(db)
        repo_response = repo.consume_topic_message(request)

        response = Service_pb2.ConsumeMessagesResponse()

        for content in repo_response['content']:
            response.messages.append(content)

        for id in repo_response['ids']:
            response.ids.append(id)

        db.close()
        print("Request is received: " + str(request))
        return response
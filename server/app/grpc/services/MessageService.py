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
        print('--------Consume topic request------')
        print(request)
        print('-----------------------------------')
        
        db = next(get_db())
        repo = MessageRepository(db)
        repo_response = repo.consume_topic_message(request)

        response = Service_pb2.ConsumeMessagesResponse()

        for content, id in zip(repo_response['content'], repo_response['ids']):
            message_item = response.messages.add() 
            message_item.content = content
            message_item.id = id

        print('--------------Topic Messages-----------------')
        print(response)
        print('---------------------------------------')

        db.close()
        print("Request is received: " + str(request))
        return response
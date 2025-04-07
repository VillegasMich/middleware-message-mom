from .. import Service_pb2, Service_pb2_grpc
from ...core.database import get_db
from ...repository.TopicRepository import TopicRepository
class TopicService(Service_pb2_grpc.TopicServiceServicer):
    def GetTopics(self, request, context):
        db = next(get_db())
        repo = TopicRepository(db)
        topics = repo.all()
        db.close()

        response = Service_pb2.GetTopicsResponse()

        print(topics)

        for topic in topics:
            topic_item = response.topic.add()
            topic_item.id = topic.id
            topic_item.name = topic.name
        
        print("Request is received: " + str(request))
        
        return response
    
    def Subscribe(self, request, context):
        db = next(get_db())
        repo = TopicRepository(db)
        
        repo.subscribe(request)
        
        db.close()
        return Service_pb2.SubscribeResponse(status_code=1)
    
    def UnSubscribe(self, request, context):
        
        return Service_pb2.SubscribeResponse(status_code=1)
    
    def Delete(self, request, context):
        db = next(get_db())
        repo = TopicRepository(db)
        
        repo.delete(request)
        
        db.close()
        return Service_pb2.CRUDResponse(status_code=1)

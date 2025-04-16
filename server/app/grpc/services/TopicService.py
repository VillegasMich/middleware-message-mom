from .. import Service_pb2, Service_pb2_grpc
from ...core.database import get_db
from ...repository.TopicRepository import TopicRepository
import grpc


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
        db = next(get_db())
        repo = TopicRepository(db)

        try:
            print(f"[Server Unsubscribe] queue_id={request.queue_id}, routing_key={request.routing_key}")
            repo.unsubscribe(request)
            return Service_pb2.SubscribeResponse(status_code=1)
        except Exception as e:
            print(f"[Server Unsubscribe] Error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return Service_pb2.SubscribeResponse(status_code=0)
        finally:
            db.close()

    def Delete(self, request, context):
        db = next(get_db())
        repo = TopicRepository(db)

        repo.delete(request)

        db.close()
        return Service_pb2.CRUDResponse(status_code=1)

    def CreateTopics(self, request, context):
        db = next(get_db())
        repo = TopicRepository(db)

        repo.create(request)

        db.close()
        return Service_pb2.CRUDResponse(status_code=1)

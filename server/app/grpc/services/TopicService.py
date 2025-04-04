from .. import Service_pb2, Service_pb2_grpc
from ...core.database import get_db

class TopicService(Service_pb2_grpc.TopicServiceServicer):
    def GetTopics(self, request, context):
        return super().GetTopics(request, context)
    
    def Subscribe(self, request, context):
        return super().Subscribe(request, context)
    
    def UnSubscribe(self, request, context):
        return super().UnSubscribe(request, context)
    
    def Delete(self, request, context):
        return super().Delete(request, context)

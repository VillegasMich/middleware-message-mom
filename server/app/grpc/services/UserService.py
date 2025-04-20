from .. import Service_pb2, Service_pb2_grpc
from ...core.database import get_db
from ...repository.UserRepository import UserRepository

class UserService(Service_pb2_grpc.UserServiceServicer):
    """
    This class implements the gRPC service for managing users.
    It provides methods to register users and get their private queues associated to their subscribed topics.
    This class interacts with the database through the UserRepository to perform the required operations.
    """

    def Register(self, request, context):
        #Handle the registration of a new user.
        
        db = next(get_db())
        
        repo = UserRepository(db)
        repo.register(request)

        db.close()
        print("Request is received: " + str(request))
        return Service_pb2.RegisterResponse(status_code=1)
    
    def GetUserTopicQueues(self, request, context):
        #Handle the retrieval of all private queues associated with a user.
        
        db = next(get_db())
        repo = UserRepository(db)
        queues = repo.get_topic_queues(request)
        db.close()
        
        response = Service_pb2.GetQueuesResponse()

        for queue in queues:
            queue_item = response.queues.add()
            queue_item.id = queue.id
            queue_item.name = queue.name
        
        print("Request is received: " + str(request))
        return response
from .. import Service_pb2, Service_pb2_grpc
from ...core.database import get_db
from ...repository.UserRepository import UserRepository

class UserService(Service_pb2_grpc.UserServiceServicer):

    def Register(self, request, context):
        db = next(get_db())
        
        repo = UserRepository(db)
        repo.register(request)

        db.close()
        print("Request is received: " + str(request))
        return Service_pb2.RegisterResponse(status_code=1)

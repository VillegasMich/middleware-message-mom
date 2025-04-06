# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from . import Service_pb2 as Service__pb2

GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in Service_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class MessageServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.AddMessage = channel.unary_unary(
                '/MessageService/AddMessage',
                request_serializer=Service__pb2.Message.SerializeToString,
                response_deserializer=Service__pb2.MessageResponse.FromString,
                _registered_method=True)
        self.ConsumeQueueMessage = channel.unary_unary(
                '/MessageService/ConsumeQueueMessage',
                request_serializer=Service__pb2.ConsumeMessageRequest.SerializeToString,
                response_deserializer=Service__pb2.ConsumeMessageResponse.FromString,
                _registered_method=True)
        self.ConsumeTopicMessage = channel.unary_unary(
                '/MessageService/ConsumeTopicMessage',
                request_serializer=Service__pb2.ConsumeMessageRequest.SerializeToString,
                response_deserializer=Service__pb2.ConsumeMessagesResponse.FromString,
                _registered_method=True)


class MessageServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def AddMessage(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ConsumeQueueMessage(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ConsumeTopicMessage(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MessageServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'AddMessage': grpc.unary_unary_rpc_method_handler(
                    servicer.AddMessage,
                    request_deserializer=Service__pb2.Message.FromString,
                    response_serializer=Service__pb2.MessageResponse.SerializeToString,
            ),
            'ConsumeQueueMessage': grpc.unary_unary_rpc_method_handler(
                    servicer.ConsumeQueueMessage,
                    request_deserializer=Service__pb2.ConsumeMessageRequest.FromString,
                    response_serializer=Service__pb2.ConsumeMessageResponse.SerializeToString,
            ),
            'ConsumeTopicMessage': grpc.unary_unary_rpc_method_handler(
                    servicer.ConsumeTopicMessage,
                    request_deserializer=Service__pb2.ConsumeMessageRequest.FromString,
                    response_serializer=Service__pb2.ConsumeMessagesResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'MessageService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('MessageService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class MessageService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def AddMessage(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/MessageService/AddMessage',
            Service__pb2.Message.SerializeToString,
            Service__pb2.MessageResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ConsumeQueueMessage(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/MessageService/ConsumeQueueMessage',
            Service__pb2.ConsumeMessageRequest.SerializeToString,
            Service__pb2.ConsumeMessageResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ConsumeTopicMessage(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/MessageService/ConsumeTopicMessage',
            Service__pb2.ConsumeMessageRequest.SerializeToString,
            Service__pb2.ConsumeMessagesResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)


class QueueServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Subscribe = channel.unary_unary(
                '/QueueService/Subscribe',
                request_serializer=Service__pb2.SubscribeRequest.SerializeToString,
                response_deserializer=Service__pb2.SubscribeResponse.FromString,
                _registered_method=True)
        self.UnSubscribe = channel.unary_unary(
                '/QueueService/UnSubscribe',
                request_serializer=Service__pb2.SubscribeRequest.SerializeToString,
                response_deserializer=Service__pb2.SubscribeResponse.FromString,
                _registered_method=True)
        self.Delete = channel.unary_unary(
                '/QueueService/Delete',
                request_serializer=Service__pb2.DeleteRequest.SerializeToString,
                response_deserializer=Service__pb2.CRUDResponse.FromString,
                _registered_method=True)
        self.GetQueues = channel.unary_unary(
                '/QueueService/GetQueues',
                request_serializer=Service__pb2.GetQueuesRequest.SerializeToString,
                response_deserializer=Service__pb2.GetQueuesResponse.FromString,
                _registered_method=True)


class QueueServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Subscribe(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UnSubscribe(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Delete(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetQueues(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_QueueServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Subscribe': grpc.unary_unary_rpc_method_handler(
                    servicer.Subscribe,
                    request_deserializer=Service__pb2.SubscribeRequest.FromString,
                    response_serializer=Service__pb2.SubscribeResponse.SerializeToString,
            ),
            'UnSubscribe': grpc.unary_unary_rpc_method_handler(
                    servicer.UnSubscribe,
                    request_deserializer=Service__pb2.SubscribeRequest.FromString,
                    response_serializer=Service__pb2.SubscribeResponse.SerializeToString,
            ),
            'Delete': grpc.unary_unary_rpc_method_handler(
                    servicer.Delete,
                    request_deserializer=Service__pb2.DeleteRequest.FromString,
                    response_serializer=Service__pb2.CRUDResponse.SerializeToString,
            ),
            'GetQueues': grpc.unary_unary_rpc_method_handler(
                    servicer.GetQueues,
                    request_deserializer=Service__pb2.GetQueuesRequest.FromString,
                    response_serializer=Service__pb2.GetQueuesResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'QueueService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('QueueService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class QueueService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Subscribe(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/QueueService/Subscribe',
            Service__pb2.SubscribeRequest.SerializeToString,
            Service__pb2.SubscribeResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def UnSubscribe(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/QueueService/UnSubscribe',
            Service__pb2.SubscribeRequest.SerializeToString,
            Service__pb2.SubscribeResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Delete(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/QueueService/Delete',
            Service__pb2.DeleteRequest.SerializeToString,
            Service__pb2.CRUDResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetQueues(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/QueueService/GetQueues',
            Service__pb2.GetQueuesRequest.SerializeToString,
            Service__pb2.GetQueuesResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)


class TopicServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Subscribe = channel.unary_unary(
                '/TopicService/Subscribe',
                request_serializer=Service__pb2.SubscribeTopicRequest.SerializeToString,
                response_deserializer=Service__pb2.SubscribeResponse.FromString,
                _registered_method=True)
        self.UnSubscribe = channel.unary_unary(
                '/TopicService/UnSubscribe',
                request_serializer=Service__pb2.SubscribeTopicRequest.SerializeToString,
                response_deserializer=Service__pb2.SubscribeResponse.FromString,
                _registered_method=True)
        self.Delete = channel.unary_unary(
                '/TopicService/Delete',
                request_serializer=Service__pb2.DeleteRequest.SerializeToString,
                response_deserializer=Service__pb2.CRUDResponse.FromString,
                _registered_method=True)
        self.GetTopics = channel.unary_unary(
                '/TopicService/GetTopics',
                request_serializer=Service__pb2.GetTopicsRequest.SerializeToString,
                response_deserializer=Service__pb2.GetTopicsResponse.FromString,
                _registered_method=True)


class TopicServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Subscribe(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UnSubscribe(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Delete(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetTopics(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TopicServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Subscribe': grpc.unary_unary_rpc_method_handler(
                    servicer.Subscribe,
                    request_deserializer=Service__pb2.SubscribeTopicRequest.FromString,
                    response_serializer=Service__pb2.SubscribeResponse.SerializeToString,
            ),
            'UnSubscribe': grpc.unary_unary_rpc_method_handler(
                    servicer.UnSubscribe,
                    request_deserializer=Service__pb2.SubscribeTopicRequest.FromString,
                    response_serializer=Service__pb2.SubscribeResponse.SerializeToString,
            ),
            'Delete': grpc.unary_unary_rpc_method_handler(
                    servicer.Delete,
                    request_deserializer=Service__pb2.DeleteRequest.FromString,
                    response_serializer=Service__pb2.CRUDResponse.SerializeToString,
            ),
            'GetTopics': grpc.unary_unary_rpc_method_handler(
                    servicer.GetTopics,
                    request_deserializer=Service__pb2.GetTopicsRequest.FromString,
                    response_serializer=Service__pb2.GetTopicsResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'TopicService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('TopicService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class TopicService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Subscribe(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/TopicService/Subscribe',
            Service__pb2.SubscribeTopicRequest.SerializeToString,
            Service__pb2.SubscribeResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def UnSubscribe(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/TopicService/UnSubscribe',
            Service__pb2.SubscribeTopicRequest.SerializeToString,
            Service__pb2.SubscribeResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Delete(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/TopicService/Delete',
            Service__pb2.DeleteRequest.SerializeToString,
            Service__pb2.CRUDResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetTopics(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/TopicService/GetTopics',
            Service__pb2.GetTopicsRequest.SerializeToString,
            Service__pb2.GetTopicsResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)


class UserServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Register = channel.unary_unary(
                '/UserService/Register',
                request_serializer=Service__pb2.RegisterRequest.SerializeToString,
                response_deserializer=Service__pb2.RegisterResponse.FromString,
                _registered_method=True)
        self.GetUserTopicQueues = channel.unary_unary(
                '/UserService/GetUserTopicQueues',
                request_serializer=Service__pb2.GetUserTopicQueuesRequest.SerializeToString,
                response_deserializer=Service__pb2.GetQueuesResponse.FromString,
                _registered_method=True)


class UserServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Register(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetUserTopicQueues(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_UserServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Register': grpc.unary_unary_rpc_method_handler(
                    servicer.Register,
                    request_deserializer=Service__pb2.RegisterRequest.FromString,
                    response_serializer=Service__pb2.RegisterResponse.SerializeToString,
            ),
            'GetUserTopicQueues': grpc.unary_unary_rpc_method_handler(
                    servicer.GetUserTopicQueues,
                    request_deserializer=Service__pb2.GetUserTopicQueuesRequest.FromString,
                    response_serializer=Service__pb2.GetQueuesResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'UserService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('UserService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class UserService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Register(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/UserService/Register',
            Service__pb2.RegisterRequest.SerializeToString,
            Service__pb2.RegisterResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetUserTopicQueues(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/UserService/GetUserTopicQueues',
            Service__pb2.GetUserTopicQueuesRequest.SerializeToString,
            Service__pb2.GetQueuesResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

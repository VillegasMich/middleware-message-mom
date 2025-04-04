from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Message(_message.Message):
    __slots__ = ("id", "type", "routing_key", "content")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ROUTING_KEY_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    id: int
    type: str
    routing_key: str
    content: str
    def __init__(self, id: _Optional[int] = ..., type: _Optional[str] = ..., routing_key: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class MessageResponse(_message.Message):
    __slots__ = ("status_code",)
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    def __init__(self, status_code: _Optional[int] = ...) -> None: ...

class ConsumeMessageRequest(_message.Message):
    __slots__ = ("id", "user_name", "user_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    user_name: str
    user_id: int
    def __init__(self, id: _Optional[int] = ..., user_name: _Optional[str] = ..., user_id: _Optional[int] = ...) -> None: ...

class ConsumeMessageResponse(_message.Message):
    __slots__ = ("status_code", "content")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    content: str
    def __init__(self, status_code: _Optional[int] = ..., content: _Optional[str] = ...) -> None: ...

class Queue(_message.Message):
    __slots__ = ("id", "name")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class GetQueuesRequest(_message.Message):
    __slots__ = ("allQueues",)
    ALLQUEUES_FIELD_NUMBER: _ClassVar[int]
    allQueues: int
    def __init__(self, allQueues: _Optional[int] = ...) -> None: ...

class GetQueuesResponse(_message.Message):
    __slots__ = ("queues",)
    QUEUES_FIELD_NUMBER: _ClassVar[int]
    queues: _containers.RepeatedCompositeFieldContainer[Queue]
    def __init__(self, queues: _Optional[_Iterable[_Union[Queue, _Mapping]]] = ...) -> None: ...

class SubscribeRequest(_message.Message):
    __slots__ = ("queue_id", "user_id", "user_name")
    QUEUE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    queue_id: int
    user_id: int
    user_name: str
    def __init__(self, queue_id: _Optional[int] = ..., user_id: _Optional[int] = ..., user_name: _Optional[str] = ...) -> None: ...

class SubscribeResponse(_message.Message):
    __slots__ = ("status_code",)
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    def __init__(self, status_code: _Optional[int] = ...) -> None: ...

class DeleteRequest(_message.Message):
    __slots__ = ("queue_id", "user_id")
    QUEUE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    queue_id: int
    user_id: int
    def __init__(self, queue_id: _Optional[int] = ..., user_id: _Optional[int] = ...) -> None: ...

class CRUDResponse(_message.Message):
    __slots__ = ("status_code",)
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    def __init__(self, status_code: _Optional[int] = ...) -> None: ...

class RegisterRequest(_message.Message):
    __slots__ = ("user_name", "user_password", "user_id")
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    USER_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_name: str
    user_password: str
    user_id: int
    def __init__(self, user_name: _Optional[str] = ..., user_password: _Optional[str] = ..., user_id: _Optional[int] = ...) -> None: ...

class RegisterResponse(_message.Message):
    __slots__ = ("status_code",)
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    def __init__(self, status_code: _Optional[int] = ...) -> None: ...

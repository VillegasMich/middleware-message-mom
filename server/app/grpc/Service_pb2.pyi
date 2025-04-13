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

class ConsumedMessage(_message.Message):
    __slots__ = ("content", "id")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    content: str
    id: int
    def __init__(self, content: _Optional[str] = ..., id: _Optional[int] = ...) -> None: ...

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

class ConsumeMessagesResponse(_message.Message):
    __slots__ = ("status_code", "messages")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    messages: _containers.RepeatedCompositeFieldContainer[ConsumedMessage]
    def __init__(self, status_code: _Optional[int] = ..., messages: _Optional[_Iterable[_Union[ConsumedMessage, _Mapping]]] = ...) -> None: ...

class Queue(_message.Message):
    __slots__ = ("id", "name")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class CreateQueueRequest(_message.Message):
    __slots__ = ("id", "name", "user_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    user_id: int
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., user_id: _Optional[int] = ...) -> None: ...

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
    __slots__ = ("queue_id", "user_id", "user_name", "topic_id", "routing_key")
    QUEUE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    TOPIC_ID_FIELD_NUMBER: _ClassVar[int]
    ROUTING_KEY_FIELD_NUMBER: _ClassVar[int]
    queue_id: int
    user_id: int
    user_name: str
    topic_id: int
    routing_key: str
    def __init__(self, queue_id: _Optional[int] = ..., user_id: _Optional[int] = ..., user_name: _Optional[str] = ..., topic_id: _Optional[int] = ..., routing_key: _Optional[str] = ...) -> None: ...

class SubscribeResponse(_message.Message):
    __slots__ = ("status_code",)
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    def __init__(self, status_code: _Optional[int] = ...) -> None: ...

class DeleteRequest(_message.Message):
    __slots__ = ("id", "user_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    user_id: int
    def __init__(self, id: _Optional[int] = ..., user_id: _Optional[int] = ...) -> None: ...

class CRUDResponse(_message.Message):
    __slots__ = ("status_code",)
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    def __init__(self, status_code: _Optional[int] = ...) -> None: ...

class Topic(_message.Message):
    __slots__ = ("id", "name")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class CreateTopicsRequest(_message.Message):
    __slots__ = ("id", "name", "user_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    user_id: int
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., user_id: _Optional[int] = ...) -> None: ...

class SubscribeTopicRequest(_message.Message):
    __slots__ = ("topic_id", "user_id", "user_name", "routing_key")
    TOPIC_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    ROUTING_KEY_FIELD_NUMBER: _ClassVar[int]
    topic_id: int
    user_id: int
    user_name: str
    routing_key: str
    def __init__(self, topic_id: _Optional[int] = ..., user_id: _Optional[int] = ..., user_name: _Optional[str] = ..., routing_key: _Optional[str] = ...) -> None: ...

class GetTopicsRequest(_message.Message):
    __slots__ = ("allTopics",)
    ALLTOPICS_FIELD_NUMBER: _ClassVar[int]
    allTopics: int
    def __init__(self, allTopics: _Optional[int] = ...) -> None: ...

class GetTopicsResponse(_message.Message):
    __slots__ = ("topic",)
    TOPIC_FIELD_NUMBER: _ClassVar[int]
    topic: _containers.RepeatedCompositeFieldContainer[Topic]
    def __init__(self, topic: _Optional[_Iterable[_Union[Topic, _Mapping]]] = ...) -> None: ...

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

class GetUserTopicQueuesRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    def __init__(self, user_id: _Optional[int] = ...) -> None: ...

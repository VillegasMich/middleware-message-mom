from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Message(_message.Message):
    __slots__ = ("queue_id", "topic_id", "routing_key", "content")
    QUEUE_ID_FIELD_NUMBER: _ClassVar[int]
    TOPIC_ID_FIELD_NUMBER: _ClassVar[int]
    ROUTING_KEY_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    queue_id: int
    topic_id: int
    routing_key: str
    content: str
    def __init__(self, queue_id: _Optional[int] = ..., topic_id: _Optional[int] = ..., routing_key: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class MessageResponse(_message.Message):
    __slots__ = ("status_code",)
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    def __init__(self, status_code: _Optional[int] = ...) -> None: ...

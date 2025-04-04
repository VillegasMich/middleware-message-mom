from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

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
    user_id: str
    def __init__(self, id: _Optional[int] = ..., user_name: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class ConsumeMessageResponse(_message.Message):
    __slots__ = ("status_code", "content")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    content: str
    def __init__(self, status_code: _Optional[int] = ..., content: _Optional[str] = ...) -> None: ...

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

class CreateRequest(_message.Message):
    __slots__ = ("name", "user_id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    user_id: int
    def __init__(self, name: _Optional[str] = ..., user_id: _Optional[int] = ...) -> None: ...

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

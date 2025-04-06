# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: Service.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'Service.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rService.proto\"I\n\x07Message\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0c\n\x04type\x18\x02 \x01(\t\x12\x13\n\x0brouting_key\x18\x03 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x04 \x01(\t\"&\n\x0fMessageResponse\x12\x13\n\x0bstatus_code\x18\x01 \x01(\x05\"G\n\x15\x43onsumeMessageRequest\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x11\n\tuser_name\x18\x02 \x01(\t\x12\x0f\n\x07user_id\x18\x03 \x01(\x05\">\n\x16\x43onsumeMessageResponse\x12\x13\n\x0bstatus_code\x18\x01 \x01(\x05\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\t\"M\n\x17\x43onsumeMessagesResponse\x12\x13\n\x0bstatus_code\x18\x01 \x01(\x05\x12\x10\n\x08messages\x18\x02 \x03(\t\x12\x0b\n\x03ids\x18\x03 \x03(\x05\"!\n\x05Queue\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\t\"%\n\x10GetQueuesRequest\x12\x11\n\tallQueues\x18\x01 \x01(\x05\"+\n\x11GetQueuesResponse\x12\x16\n\x06queues\x18\x01 \x03(\x0b\x32\x06.Queue\"H\n\x10SubscribeRequest\x12\x10\n\x08queue_id\x18\x01 \x01(\x05\x12\x0f\n\x07user_id\x18\x02 \x01(\x05\x12\x11\n\tuser_name\x18\x03 \x01(\t\"(\n\x11SubscribeResponse\x12\x13\n\x0bstatus_code\x18\x01 \x01(\x05\",\n\rDeleteRequest\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0f\n\x07user_id\x18\x02 \x01(\x05\"#\n\x0c\x43RUDResponse\x12\x13\n\x0bstatus_code\x18\x01 \x01(\x05\"!\n\x05Topic\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\t\"b\n\x15SubscribeTopicRequest\x12\x10\n\x08topic_id\x18\x01 \x01(\x05\x12\x0f\n\x07user_id\x18\x02 \x01(\x05\x12\x11\n\tuser_name\x18\x03 \x01(\t\x12\x13\n\x0brouting_key\x18\x04 \x01(\t\"%\n\x10GetTopicsRequest\x12\x11\n\tallTopics\x18\x01 \x01(\x05\"*\n\x11GetTopicsResponse\x12\x15\n\x05topic\x18\x01 \x03(\x0b\x32\x06.Topic\"L\n\x0fRegisterRequest\x12\x11\n\tuser_name\x18\x01 \x01(\t\x12\x15\n\ruser_password\x18\x02 \x01(\t\x12\x0f\n\x07user_id\x18\x03 \x01(\x05\"\'\n\x10RegisterResponse\x12\x13\n\x0bstatus_code\x18\x01 \x01(\x05\",\n\x19GetUserTopicQueuesRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\x05\x32\xca\x01\n\x0eMessageService\x12(\n\nAddMessage\x12\x08.Message\x1a\x10.MessageResponse\x12\x46\n\x13\x43onsumeQueueMessage\x12\x16.ConsumeMessageRequest\x1a\x17.ConsumeMessageResponse\x12\x46\n\x13\x43onsumeTopicMessage\x12\x16.ConsumeMessageRequest\x1a\x17.ConsumeMessageResponse2\xd5\x01\n\x0cQueueService\x12\x32\n\tSubscribe\x12\x11.SubscribeRequest\x1a\x12.SubscribeResponse\x12\x34\n\x0bUnSubscribe\x12\x11.SubscribeRequest\x1a\x12.SubscribeResponse\x12\'\n\x06\x44\x65lete\x12\x0e.DeleteRequest\x1a\r.CRUDResponse\x12\x32\n\tGetQueues\x12\x11.GetQueuesRequest\x1a\x12.GetQueuesResponse2\xdf\x01\n\x0cTopicService\x12\x37\n\tSubscribe\x12\x16.SubscribeTopicRequest\x1a\x12.SubscribeResponse\x12\x39\n\x0bUnSubscribe\x12\x16.SubscribeTopicRequest\x1a\x12.SubscribeResponse\x12\'\n\x06\x44\x65lete\x12\x0e.DeleteRequest\x1a\r.CRUDResponse\x12\x32\n\tGetTopics\x12\x11.GetTopicsRequest\x1a\x12.GetTopicsResponse2\x84\x01\n\x0bUserService\x12/\n\x08Register\x12\x10.RegisterRequest\x1a\x11.RegisterResponse\x12\x44\n\x12GetUserTopicQueues\x12\x1a.GetUserTopicQueuesRequest\x1a\x12.GetQueuesResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'Service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_MESSAGE']._serialized_start=17
  _globals['_MESSAGE']._serialized_end=90
  _globals['_MESSAGERESPONSE']._serialized_start=92
  _globals['_MESSAGERESPONSE']._serialized_end=130
  _globals['_CONSUMEMESSAGEREQUEST']._serialized_start=132
  _globals['_CONSUMEMESSAGEREQUEST']._serialized_end=203
  _globals['_CONSUMEMESSAGERESPONSE']._serialized_start=205
  _globals['_CONSUMEMESSAGERESPONSE']._serialized_end=267
  _globals['_CONSUMEMESSAGESRESPONSE']._serialized_start=269
  _globals['_CONSUMEMESSAGESRESPONSE']._serialized_end=346
  _globals['_QUEUE']._serialized_start=348
  _globals['_QUEUE']._serialized_end=381
  _globals['_GETQUEUESREQUEST']._serialized_start=383
  _globals['_GETQUEUESREQUEST']._serialized_end=420
  _globals['_GETQUEUESRESPONSE']._serialized_start=422
  _globals['_GETQUEUESRESPONSE']._serialized_end=465
  _globals['_SUBSCRIBEREQUEST']._serialized_start=467
  _globals['_SUBSCRIBEREQUEST']._serialized_end=539
  _globals['_SUBSCRIBERESPONSE']._serialized_start=541
  _globals['_SUBSCRIBERESPONSE']._serialized_end=581
  _globals['_DELETEREQUEST']._serialized_start=583
  _globals['_DELETEREQUEST']._serialized_end=627
  _globals['_CRUDRESPONSE']._serialized_start=629
  _globals['_CRUDRESPONSE']._serialized_end=664
  _globals['_TOPIC']._serialized_start=666
  _globals['_TOPIC']._serialized_end=699
  _globals['_SUBSCRIBETOPICREQUEST']._serialized_start=701
  _globals['_SUBSCRIBETOPICREQUEST']._serialized_end=799
  _globals['_GETTOPICSREQUEST']._serialized_start=801
  _globals['_GETTOPICSREQUEST']._serialized_end=838
  _globals['_GETTOPICSRESPONSE']._serialized_start=840
  _globals['_GETTOPICSRESPONSE']._serialized_end=882
  _globals['_REGISTERREQUEST']._serialized_start=884
  _globals['_REGISTERREQUEST']._serialized_end=960
  _globals['_REGISTERRESPONSE']._serialized_start=962
  _globals['_REGISTERRESPONSE']._serialized_end=1001
  _globals['_GETUSERTOPICQUEUESREQUEST']._serialized_start=1003
  _globals['_GETUSERTOPICQUEUESREQUEST']._serialized_end=1047
  _globals['_MESSAGESERVICE']._serialized_start=1050
  _globals['_MESSAGESERVICE']._serialized_end=1252
  _globals['_QUEUESERVICE']._serialized_start=1255
  _globals['_QUEUESERVICE']._serialized_end=1468
  _globals['_TOPICSERVICE']._serialized_start=1471
  _globals['_TOPICSERVICE']._serialized_end=1694
  _globals['_USERSERVICE']._serialized_start=1697
  _globals['_USERSERVICE']._serialized_end=1829
# @@protoc_insertion_point(module_scope)

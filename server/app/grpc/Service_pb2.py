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




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rService.proto\"I\n\x07Message\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0c\n\x04type\x18\x02 \x01(\t\x12\x13\n\x0brouting_key\x18\x03 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x04 \x01(\t\"&\n\x0fMessageResponse\x12\x13\n\x0bstatus_code\x18\x01 \x01(\x05\x32:\n\x0eMessageService\x12(\n\nAddMessage\x12\x08.Message\x1a\x10.MessageResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'Service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_MESSAGE']._serialized_start=17
  _globals['_MESSAGE']._serialized_end=90
  _globals['_MESSAGERESPONSE']._serialized_start=92
  _globals['_MESSAGERESPONSE']._serialized_end=130
  _globals['_MESSAGESERVICE']._serialized_start=132
  _globals['_MESSAGESERVICE']._serialized_end=190
# @@protoc_insertion_point(module_scope)

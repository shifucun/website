# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: stat_config.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11stat_config.proto\x12\x0b\x64\x61tacommons\"w\n\x07ObsProp\x12\x12\n\x05mprop\x18\x02 \x01(\tH\x00\x88\x01\x01\x12\x12\n\x05mqual\x18\x03 \x01(\tH\x01\x88\x01\x01\x12\x13\n\x06mdenom\x18\x04 \x01(\tH\x02\x88\x01\x01\x42\x08\n\x06_mpropB\x08\n\x06_mqualB\t\n\x07_mdenomJ\x04\x08\x01\x10\x02J\x04\x08\x06\x10\x07J\x04\x08\x07\x10\x08\"\xb9\x02\n\nPopObsSpec\x12\x15\n\x08pop_type\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\r\n\x05\x63prop\x18\x04 \x03(\t\x12\'\n\x03\x64pv\x18\x05 \x03(\x0b\x32\x1a.datacommons.PopObsSpec.PV\x12\x10\n\x08vertical\x18\x07 \x03(\t\x12\'\n\tobs_props\x18\x08 \x03(\x0b\x32\x14.datacommons.ObsProp\x12-\n show_under_listed_verticals_only\x18\t \x01(\x08H\x01\x88\x01\x01\x1a:\n\x02PV\x12\x11\n\x04prop\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x10\n\x03val\x18\x02 \x01(\tH\x01\x88\x01\x01\x42\x07\n\x05_propB\x06\n\x04_valB\x0b\n\t_pop_typeB#\n!_show_under_listed_verticals_onlyJ\x04\x08\x06\x10\x07\"7\n\x0ePopObsSpecList\x12%\n\x04spec\x18\x01 \x03(\x0b\x32\x17.datacommons.PopObsSpecb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'stat_config_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _OBSPROP._serialized_start=34
  _OBSPROP._serialized_end=153
  _POPOBSSPEC._serialized_start=156
  _POPOBSSPEC._serialized_end=469
  _POPOBSSPEC_PV._serialized_start=355
  _POPOBSSPEC_PV._serialized_end=413
  _POPOBSSPECLIST._serialized_start=471
  _POPOBSSPECLIST._serialized_end=526
# @@protoc_insertion_point(module_scope)

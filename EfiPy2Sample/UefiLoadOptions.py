# UefiLoadOptions.py
#
#   part of EfiPy2
#
# Copyright (C) 2024 - 2026 MaxWu efipy.core@gmail.com
#   GPL-2.0
#

import copy
import EfiPy2
from EfiPy2.Lib.EfiPyVariable import Variable
from EfiPy2.Lib.EfiPyVariables import Variables
from EfiPy2.MdePkg.Guid.GlobalVariable import gEfiGlobalVariableGuid
from EfiPy2.MdePkg.Uefi.UefiSpec import EFI_LOAD_OPTION
from EfiPy2.MdePkg.Protocol.DevicePathEfiPy  import EFI_DEVICE_PATH_PROTOCOL

def GetDevNodeLengthFromByte (DevNodeRaw):
  TempDevNode = EFI_DEVICE_PATH_PROTOCOL.from_buffer_copy (DevNodeRaw)
  TempDevLen  = TempDevNode.Length
  del (TempDevNode)
  return TempDevLen

def GetDevPathLengthFromByte (DevPathRaw):

  TempDevNodeRaw = DevPathRaw
  TempDevPathLen = 0

  TempDevNode = EFI_DEVICE_PATH_PROTOCOL.from_buffer_copy (TempDevNodeRaw)
  while True:
    TempDevPathLen += TempDevNode.Length
    if (TempDevNode.Type == 0x7F) and (TempDevNode.SubType == 0xFF):
      return TempDevPathLen
    TempDevNodeRaw = DevPathRaw[TempDevPathLen:]
    TempDevNode = EFI_DEVICE_PATH_PROTOCOL.from_buffer_copy (TempDevNodeRaw)

  return -1

def BuildLoadOptionStructure (LoadOptionRaw):
  #
  # Build EFI_LOAD_OPTION structure
  #
  EfiLoadOptionField  = copy.copy (EFI_LOAD_OPTION._fields_)

  #
  # 1. Add Description in Load Option
  #
  EfiLoadOptionDescriptionByte = LoadOptionRaw [EfiPy2.sizeof (EFI_LOAD_OPTION):]
  EfiLoadOptionDescriptionStr  = EfiLoadOptionDescriptionByte.decode ('utf16').split('\x00')[0]

  EfiLoadOptionField.append (('Description', EfiPy2.UINT16 * (len (EfiLoadOptionDescriptionStr) + 1)))
  class EfiLoadOptionType (EfiPy2.Structure):
    _pack_          = 1
    _fields_ = EfiLoadOptionField

  # EfiLoadOptionObject  = EfiLoadOptionType.from_buffer_copy (LoadOptionRaw)

  #
  # 2. Add FilePathList and OptionalData in Load Option
  #
  EfiLoadOptionFilePathListByte = LoadOptionRaw [EfiPy2.sizeof (EfiLoadOptionType):]
  EfiLoadOptionFilePathListLen  = GetDevPathLengthFromByte (EfiLoadOptionFilePathListByte)
  EfiLoadOptionOptionalDataLen  = len(LoadOptionRaw ) - EfiPy2.sizeof (EfiLoadOptionType) - EfiLoadOptionFilePathListLen

  EfiLoadOptionField.append (('FilePathList', EfiPy2.UINT8 * (EfiLoadOptionFilePathListLen)))
  EfiLoadOptionField.append (('OptionalData', EfiPy2.UINT8 * (EfiLoadOptionOptionalDataLen)))
  class EfiLoadOptionType (EfiPy2.Structure):
    _pack_          = 1
    _fields_ = EfiLoadOptionField

  return EfiLoadOptionType

with Variables('Boot0', CaseSensitive = True) as Vars:

  for n, g in Vars:

    if g != gEfiGlobalVariableGuid:
      print (f'GUID {g} and {gEfiGlobalVariableGuid} is not equal')
      continue
    if 'Boot0' not in n:
      continue

    LoadOptionVariable = Variable (n, g)
    LoadOptionVariable.GetVariable ()

    EfiLoadOptionType   = BuildLoadOptionStructure (LoadOptionVariable.Value)
    EfiLoadOptionObject = EfiLoadOptionType.from_buffer_copy (LoadOptionVariable.Value)

    print (f'''
{n}, GUID: {g}
====================================================''')
    print (f'Variable size:      0x{len(LoadOptionVariable.Value):08X}')
    print (f'Attributes:         0x{EfiLoadOptionObject.Attributes:08X}')
    print (f'Description:        {bytes(EfiLoadOptionObject.Description)[:-2].decode("utf16")}')
    print (f'FilePathListLength: 0x{EfiLoadOptionObject.FilePathListLength:04X} ({EfiLoadOptionObject.FilePathListLength})')
    FilePathListString = (EfiPy2.cast (EfiLoadOptionObject.FilePathList, EfiPy2.POINTER(EFI_DEVICE_PATH_PROTOCOL)))[0]
    # print (f'FilePathList        {bytes(EfiLoadOptionObject.FilePathList)}')
    print (f'FilePathList        {FilePathListString}')
    print (f'OptionalData        {bytes(EfiLoadOptionObject.OptionalData)}')
    print ('\nRaw data')
    from EfiPy2.Lib.HexDump import HexDump
    HexDump (LoadOptionVariable.VarValue[:])

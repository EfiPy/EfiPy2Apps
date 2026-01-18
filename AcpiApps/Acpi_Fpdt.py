# Acpi_Fpdt.py
#
#   part of EfiPy2
#
# Copyright (C) 2025 - 2026 MaxWu efipy.core@gmail.com
#   GPL-2.0
#

#
# Reference from https://uefi.org/acpi
#
import EfiPy2
from EfiPy2.Lib.StructDump import DumpStruct
from EfiPy2.Lib.HexDump import HexDump

def GetBufFromPa (Pa: int):
  import os
  if os.name == 'nt':
    return None, None
  elif os.name == 'edk2':
    return bytes ((EfiPy2.UINT8 * 4096).from_address (Pa)), 0

  import mmap

  MmapFile = open ('/dev/mem', 'rb')
  Offset  = Pa % mmap.PAGESIZE
  MapSize = mmap.PAGESIZE - Offset

  MmapHandle = mmap.mmap (
                      MmapFile.fileno(),
                      length = mmap.PAGESIZE + Offset,
                      flags  = mmap.MAP_SHARED,
                      access = mmap.ACCESS_READ,
                      offset = Pa - Offset
                      )
  MmapFile.close ()

  return MmapHandle, Offset

def ParsingBasicFp (Entry: int) -> bool:

  VaBuff, Offset = GetBufFromPa (Entry)
  if (None, None) == (VaBuff, Offset):
    return

  print ("""
Firmware Basic Boot Performcance Table (FBPT) entry: 0x{Entry:08X}
=======================================================================================================================""")

  class BasicBootRecord (Acpi.EFIPY_INDUSTRY_STRUCTURE):
    _fields_ = [
        ("TableHeader", Acpi.EFI_ACPI_6_5_FPDT_PERFORMANCE_TABLE_HEADER),
        ("BasicBoot",   Acpi.EFI_ACPI_6_5_FPDT_FIRMWARE_BASIC_BOOT_RECORD),
    ]
  Table = BasicBootRecord.from_buffer_copy (VaBuff[Offset:])
  DumpStruct (2, Table, BasicBootRecord)
  HexDump (VaBuff[Offset: Offset + EfiPy2.sizeof (Table)])

def ParsingS3Fp (Entry: int) -> bool:

  VaBuff, Offset = GetBufFromPa (Entry)
  if (None, None) == (VaBuff, Offset):
    return

  print (f"""
S3 Performcance Table (S3PT) entry: 0x{Entry:08X}
=======================================================================================================================""")

  class S3BootRecord (Acpi.EFIPY_INDUSTRY_STRUCTURE):
    _fields_ = [
        ("TableHeader", Acpi.EFI_ACPI_6_5_FPDT_PERFORMANCE_TABLE_HEADER),
        ("S3Record",    Acpi.EFI_ACPI_6_5_FPDT_PERFORMANCE_RECORD_HEADER),
    ]
  S3Table = S3BootRecord.from_buffer_copy (VaBuff[Offset:])

  if S3Table.S3Record.Type == 0:
    class S3BootRecord (Acpi.EFIPY_INDUSTRY_STRUCTURE):
      _fields_ = [
          ("TableHeader", Acpi.EFI_ACPI_6_5_FPDT_PERFORMANCE_TABLE_HEADER),
          ("S3Resume",    Acpi.EFI_ACPI_6_5_FPDT_S3_RESUME_RECORD),
      ]
  elif S3Table.S3Record.Type == 1:
    class S3BootRecord (Acpi.EFIPY_INDUSTRY_STRUCTURE):
      _fields_ = [
          ("TableHeader", Acpi.EFI_ACPI_6_5_FPDT_PERFORMANCE_TABLE_HEADER),
          ("S3Suspend",   Acpi.EFI_ACPI_6_5_FPDT_S3_SUSPEND_RECORD),
      ]

  S3Table = S3BootRecord.from_buffer_copy (VaBuff[Offset:])
  DumpStruct (2, S3Table, S3BootRecord)
  HexDump (VaBuff[Offset: Offset + EfiPy2.sizeof (S3Table)])

if __name__ == '__main__':
    from EfiPy2.Lib.Acpi.AcpiFpdtParser import AcpiFpdtParser
    from EfiPy2.MdePkg.IndustryStandard import Acpi
    FpdtSignature = b'FPDT'

    from EfiPy2.Lib.Acpi.AcpiRetrieve import ExtractTable

    FpdtRaw = ExtractTable (FpdtSignature, 0)
    if FpdtRaw is None:
      print ('Can not retrieve FPDT')
      exit(0)
    FpdtObj, FpdtType = AcpiFpdtParser (FpdtRaw)

    print ("""
Firmware Performance Descript Table (FPDT)
=======================================================================================================================""")
    DumpStruct (2, FpdtObj, FpdtType)

    for Index in range (10):

      FpdtRecordName=f'FpdtRecord_{Index}'
      try:
        FpdtRecordObj = getattr (FpdtObj, FpdtRecordName)
      except AttributeError as e:
        break

      if FpdtRecordObj.Header.Type == 0:
        ParsingBasicFp (FpdtRecordObj.BootPerformanceTablePointer)
      elif FpdtRecordObj.Header.Type == 1:
        ParsingS3Fp (FpdtRecordObj.S3PerformanceTablePointer)

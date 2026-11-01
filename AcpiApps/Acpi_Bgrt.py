# Acpi_Bgrt.py
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

  try:
    MmapFile = open ('/dev/mem', 'rb')
  except Exception:
    return None, None

  Offset  = Pa % mmap.PAGESIZE

  try:
    MmapHandle = mmap.mmap (
                        MmapFile.fileno(),
                        length = mmap.PAGESIZE + Offset,
                        flags  = mmap.MAP_SHARED,
                        access = mmap.ACCESS_READ,
                        offset = Pa - Offset
                        )
  except Exception:
    MmapFile.close ()
    return None, None

  MmapFile.close ()
  return MmapHandle, Offset

def ParsingBgrtImage (BgrtObj):

  from EfiPy2.MdePkg.IndustryStandard import Acpi
  from EfiPy2.MdePkg.IndustryStandard import Bmp

  Entry = BgrtObj.ImageAddress
  if Entry == 0:
    return

  BgrtMem, Offset = GetBufFromPa (Entry)
  if BgrtMem is None:
    return

  try:
    DumpSize = 0x30
    if BgrtObj.ImageType == Acpi.EFI_ACPI_5_0_BGRT_IMAGE_TYPE_BMP:
      print (f"""
BMP Image Header:
=======================================================================================================================""")
      BmpType   = Bmp.BMP_IMAGE_HEADER
      BmpHeader = Bmp.BMP_IMAGE_HEADER.from_buffer_copy (BgrtMem[Offset : Offset + EfiPy2.sizeof (BmpType)])
      DumpStruct (2, BmpHeader, BmpType)
      DumpSize = EfiPy2.sizeof (BmpHeader)

    print (f"""
BGRT Image Address: 0x{Entry:08X}
=======================================================================================================================""")
    HexDump (BgrtMem[Offset: Offset + DumpSize])
  finally:
    if hasattr (BgrtMem, 'close'):
      BgrtMem.close ()

if __name__ == '__main__':
    from EfiPy2.Lib.Acpi.AcpiBgrtParser import AcpiBgrtParser
    from EfiPy2.MdePkg.IndustryStandard import Acpi
    BgrtSignature = b'BGRT'

    from EfiPy2.Lib.Acpi.AcpiRetrieve import ExtractTable

    BgrtRaw = ExtractTable (BgrtSignature, 0)
    if not BgrtRaw:
      print ('Can not retrieve BGRT')
      exit(0)
    BgrtObj, BgrtType = AcpiBgrtParser (BgrtRaw)
    if BgrtObj is None:
      print ('Can not parse BGRT')
      exit(0)

    print (f"""
Boot Graphics Resource Table (BGRT)
=======================================================================================================================""")
    DumpStruct (2, BgrtObj, BgrtType)

    ParsingBgrtImage (BgrtObj)
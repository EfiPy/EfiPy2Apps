# PciConfigDumpSingle.py
#
# Copyright (C) 2026 MaxWu efipy.core@gmail.com All rights reserved.
#
#   GPL-2.0
#

import sys
import re
import argparse

import EfiPy2.MdePkg.IndustryStandard.Pci as pci
from EfiPy2.Lib.Acpi.AcpiRetrieve   import ExtractTable
from EfiPy2.Lib.Acpi.AcpiMcfgParser import AcpiMcfgParser
from EfiPy2.Lib.PciScanLib          import PrintPciDevice, PCI_ACCESS_MCFG
from EfiPy2.Lib.StructDump          import DumpStruct
from EfiPy2.Lib.HexDump             import HexDump
from EfiPy2.Lib.PciConfigurationSpace import BuildPciHeader

def ParseSbdf (SbdfStr: str):
  """
  Parse SBDF string into (Segment, Bus, Dev, Func).
  Supported formats:
    - [Seg:]Bus:Dev.Func  (e.g. 0000:00:02.0, 00:02.0, 0:2.0)
    - [Seg:]Bus:Dev:Func  (e.g. 0000:00:02:0, 00:02:0)
    - Bus:Dev             (Func defaults to 0)
  """
  Pattern = r'^(?:([0-9a-fA-F]+):)?([0-9a-fA-F]+):([0-9a-fA-F]+)(?:[.:]([0-9a-fA-F]+))?$'
  Match = re.match (Pattern, SbdfStr.strip ())
  if not Match:
    raise ValueError (f"Invalid SBDF format: '{SbdfStr}'. Expected format: [Seg:]Bus:Dev.Func (e.g. 00:02.0 or 0000:00:02.0)")

  SegStr, BusStr, DevStr, FuncStr = Match.groups ()
  Seg  = int (SegStr, 16) if SegStr is not None else 0
  Bus  = int (BusStr, 16)
  Dev  = int (DevStr, 16)
  Func = int (FuncStr, 16) if FuncStr is not None else 0

  return Seg, Bus, Dev, Func

if __name__ == '__main__':

  parser = argparse.ArgumentParser (
    prog        = 'PciConfigDumpSingle.py',
    description = 'Dump detailed PCI/PCIe Configuration Space (HexDump & StructDump) for a specified SBDF device.'
  )
  parser.add_argument (
    'target',
    nargs   = '?',
    default = None,
    help    = 'Target device in [Seg:]Bus:Dev.Func format (e.g. 00:02.0, 0000:00:1f.3)'
  )
  parser.add_argument ('-s', '--segment', type = lambda x: int (x, 0), default = None, help = 'PCI Segment (default: 0)')
  parser.add_argument ('-b', '--bus',     type = lambda x: int (x, 0), default = None, help = 'PCI Bus number (hex or dec)')
  parser.add_argument ('-d', '--device',  type = lambda x: int (x, 0), default = None, help = 'PCI Device number (hex or dec)')
  parser.add_argument ('-f', '--func',    type = lambda x: int (x, 0), default = None, help = 'PCI Function number (hex or dec)')

  args = parser.parse_args ()

  # Resolve Segment, Bus, Dev, Func
  if args.target:
    try:
      Seg, Bus, Dev, Func = ParseSbdf (args.target)
    except ValueError as e:
      print (f"Error: {e}", file = sys.stderr)
      sys.exit (1)
    if args.segment is not None: Seg  = args.segment
    if args.bus     is not None: Bus  = args.bus
    if args.device  is not None: Dev  = args.device
    if args.func    is not None: Func = args.func
  else:
    if args.bus is None or args.device is None:
      parser.print_help ()
      sys.exit (1)
    Seg  = args.segment if args.segment is not None else 0
    Bus  = args.bus
    Dev  = args.device
    Func = args.func if args.func is not None else 0

  # Validate ranges
  if not (0 <= Bus <= pci.PCI_MAX_BUS):
    print (f"Error: Bus {Bus} out of range (0-{pci.PCI_MAX_BUS})", file = sys.stderr)
    sys.exit (1)
  if not (0 <= Dev <= pci.PCI_MAX_DEVICE):
    print (f"Error: Device {Dev} out of range (0-{pci.PCI_MAX_DEVICE})", file = sys.stderr)
    sys.exit (1)
  if not (0 <= Func <= pci.PCI_MAX_FUNC):
    print (f"Error: Function {Func} out of range (0-{pci.PCI_MAX_FUNC})", file = sys.stderr)
    sys.exit (1)

  # Retrieve MCFG Table
  AcpiRaw = ExtractTable (b'MCFG', 0)
  if not AcpiRaw:
    print ("Error: MCFG ACPI table not found!", file = sys.stderr)
    sys.exit (1)

  AcpiObj, AcpiType = AcpiMcfgParser (AcpiRaw)

  McfgDesc = next ((Desc for Desc in AcpiObj.McfgDesc
                   if Desc.PciSegmentGroupNumber == Seg and
                   Desc.StartBusNumber <= Bus <= Desc.EndBusNumber), None)

  if McfgDesc is None:
    print (f"Error: No MCFG entry found for Segment {Seg:04X}, Bus {Bus:02X}", file = sys.stderr)
    sys.exit (1)

  PciCfgOffset = pci.PCI_ECAM_ADDRESS (Bus, Dev, Func, 0)
  MmioAddress  = McfgDesc.BaseAddress + PciCfgOffset

  PciObj, PciType, IsPcieDevice = BuildPciHeader (McfgDesc.BaseAddress, PciCfgOffset)

  if PciObj is None or PciObj.Fields.Hdr.VendorId in (0xFFFF, 0x0000):
    VendorId = PciObj.Fields.Hdr.VendorId if (PciObj and hasattr(PciObj, 'Fields')) else 0xFFFF
    print (f"Device {Seg:04X}:{Bus:02X}:{Dev:02X}.{Func:X} not present (Vendor ID = 0x{VendorId:04X})")
    sys.exit (0)

  # Construct dev dictionary for PrintPciDevice
  dev_info = {
    "mode":    PCI_ACCESS_MCFG,
    "segment": Seg,
    "bus":     Bus,
    "dev":     Dev,
    "func":    Func,
    "vid":     PciObj.Fields.Hdr.VendorId,
    "did":     PciObj.Fields.Hdr.DeviceId,
    "rev":     PciObj.Fields.Hdr.RevisionID,
    "class":   tuple (PciObj.Fields.Hdr.ClassCode[:]),
  }

  print ('\n' + '=' * 100)
  PrintPciDevice (dev_info)
  print (f"Type: {'PCIe (4KB)' if IsPcieDevice else 'PCI (256B)'}, MMIO: 0x{MmioAddress:08X} (Base: 0x{McfgDesc.BaseAddress:08X}, ECAM Offset: 0x{PciCfgOffset:08X})")
  print ('=' * 100)

  print ("\n[1] Configuration Space HexDump:")
  HexDump (PciObj.Raw, MmioAddress)

  print ("\n[2] Configuration Space StructDump:")
  DumpStruct (0, PciObj, PciType, CopyUnit = 4)


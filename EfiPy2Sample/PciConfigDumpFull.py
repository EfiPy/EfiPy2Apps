# PciConfigDumpFull.py
#
# Copyright (C) 2026 MaxWu efipy.core@gmail.com All rights reserved.
#
#   GPL-2.0
#

import EfiPy2.MdePkg.IndustryStandard.Pci as pci
from EfiPy2.Lib.Acpi.AcpiRetrieve   import ExtractTable
from EfiPy2.Lib.Acpi.AcpiMcfgParser import AcpiMcfgParser
from EfiPy2.Lib.PciScanLib          import ScanPciDevices, PrintPciDevice, PCI_ACCESS_MCFG
from EfiPy2.Lib.StructDump          import DumpStruct
from EfiPy2.Lib.HexDump             import HexDump

from EfiPy2.Lib.PciConfigurationSpace import BuildPciHeader

if __name__ == '__main__':

  AcpiRaw = ExtractTable (b'MCFG', 0)
  AcpiObj, AcpiType = AcpiMcfgParser (AcpiRaw)

  devices = ScanPciDevices (AccessMode = PCI_ACCESS_MCFG)

  for dev in devices:
    Segment = dev['segment']
    Bus     = dev['bus']
    Dev     = dev['dev']
    Func    = dev['func']

    McfgDesc = next ((Desc for Desc in AcpiObj.McfgDesc
                     if Desc.PciSegmentGroupNumber == Segment and
                     Desc.StartBusNumber <= Bus <= Desc.EndBusNumber), None)
    if McfgDesc is None:
      continue

    PciCfgOffset = pci.PCI_ECAM_ADDRESS (Bus, Dev, Func, 0)

    PciObj, PciType, IsPcieDevice = BuildPciHeader (McfgDesc.BaseAddress, PciCfgOffset)
    print ('\n' + '=' * 100)
    PrintPciDevice (dev)
    print (f"Type: {'PCIe (4KB)' if IsPcieDevice else 'PCI (256B)'}, MMIO: 0x{McfgDesc.BaseAddress + PciCfgOffset:08X} (Base: 0x{McfgDesc.BaseAddress:08X}, ECAM Offset: 0x{PciCfgOffset:08X})")
    print ('=' * 100)
    HexDump (PciObj.Raw, McfgDesc.BaseAddress + PciCfgOffset)
    DumpStruct (0, PciObj, PciType, CopyUnit = 4)


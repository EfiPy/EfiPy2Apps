# PciScan.py
#
# Copyright (C) 2025 - 2026 MaxWu efipy.core@gmail.com All rights reserved.
#
#   GPL-2.0
#

import EfiPy2 as EfiPy
import EfiPy2.MdePkg.IndustryStandard.Pci as pci
from EfiPy2.Lib.Acpi.AcpiRetrieve   import ExtractTable
from EfiPy2.Lib.Acpi.AcpiMcfgParser import AcpiMcfgParser
import pciids

class PCI_DEVICE_INDEPENDENT_REGION_UNION (pci.EFIPY_INDUSTRY_UNION):

  _fields_ = [
    ('Hdr',     pci.PCI_DEVICE_INDEPENDENT_REGION),
    ('Raw',     EfiPy.UINT32 * (EfiPy.sizeof (pci.PCI_DEVICE_INDEPENDENT_REGION) // (EfiPy.sizeof (EfiPy.UINT32)))),
    ('Raw16',   EfiPy.UINT16 * (EfiPy.sizeof (pci.PCI_DEVICE_INDEPENDENT_REGION) // (EfiPy.sizeof (EfiPy.UINT16)))),
  ]

def ScanMcfgSegment (McfgDesc) -> None:

  PciCfgBase = McfgDesc.BaseAddress
  Segment    = McfgDesc.PciSegmentGroupNumber
  StartBus   = McfgDesc.StartBusNumber
  EndBus     = McfgDesc.EndBusNumber

  for Bus in range (StartBus, EndBus + 1):
    for Dev in range (pci.PCI_MAX_DEVICE + 1):
      for Func in range (pci.PCI_MAX_FUNC + 1):

        PciCfgAddr = PciCfgBase + pci.PCI_ECAM_ADDRESS (Bus, Dev, Func, 0)
        PciCfg     = PCI_DEVICE_INDEPENDENT_REGION_UNION.from_address (PciCfgAddr)

        VendorId, DeviceId = PciCfg.Raw16 [:2]

        if VendorId in (0xFFFF, 0x0000) and Func == 0:
          break

        if VendorId in (0xFFFF, 0x0000):
          continue

        RevisionID                      = PciCfg.Hdr.RevisionID
        Interface, SubClass, BaseClass  = PciCfg.Hdr.ClassCode [:]

        DeviceClass, SubClassDict       = pciids.PciClass.get (BaseClass, (f"Class {BaseClass:02X}", {}))
        SubName, ProgIfDict             =    SubClassDict.get (SubClass, (f"SubClass {SubClass:02X}", {}))
        ProgIfName                      =    ProgIfDict.get (Interface, f"ProgIf {Interface:02X}")
        VendorName, DeviceDict          = pciids.PciIds.get (VendorId, (f"Vendor {VendorId:04X}", {}))
        DeviceName, _                   =    DeviceDict.get (DeviceId, (f"Device {DeviceId:04X}", {}))

        print (f"{Segment:04X}:{Bus:02X}:{Dev:02X}.{Func:X} {SubName}: {ProgIfName} ({BaseClass:X},{SubClass:X},{Interface:X}): {VendorName}: {DeviceName} ({VendorId:04X} {DeviceId:04X} rev: {RevisionID:02X})")

        if Func == 0 and not pci.IS_PCI_MULTI_FUNC (PciCfg):
          break

if __name__ == '__main__':

  AcpiRaw    = ExtractTable (b'MCFG', 0)
  AcpiObj, _ = AcpiMcfgParser (AcpiRaw)

  for McfgDesc in AcpiObj.McfgDesc:
    ScanMcfgSegment (McfgDesc)


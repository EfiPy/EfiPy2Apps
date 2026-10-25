# PciTree.py
#
# Copyright (C) 2025 - 2026 MaxWu efipy.core@gmail.com All rights reserved.
#
# GPL-v2
#
# Modified by Google DeepMind Antigravity (Gemini)
#

import EfiPy2 as EfiPy
from EfiPy2.MdePkg.IndustryStandard import EFIPY_INDUSTRY_STRUCTURE, EFIPY_INDUSTRY_UNION
import EfiPy2.MdePkg.IndustryStandard.Pci as pci
import pciids

from EfiPy2.Lib.Acpi.AcpiRetrieve   import ExtractTable
from EfiPy2.Lib.Acpi.AcpiMcfgParser import AcpiMcfgParser

def BuildPciHeader (EcamBase: int, EcamOffset: int) -> None:

  PciCfgAddress = EcamBase + EcamOffset

  PciCfg = pci.PCI_TYPE00.from_address (PciCfgAddress)

  PciTypeFields = [
      ('Hdr',     pci.PCI_DEVICE_INDEPENDENT_REGION),
    ]

  #
  # Build TYPE 00/01 header
  #
  if pci.IS_PCI_BRIDGE (PciCfg) or pci.IS_CARDBUS_BRIDGE (PciCfg):
    # Type 1
    PciTypeFields.append (('Cfg', pci.PCI_BRIDGE_CONTROL_REGISTER))

  else:
    # Type 0
    PciTypeFields.append (('Cfg', pci.PCI_DEVICE_HEADER_TYPE_REGION))

  class PciStruct (EFIPY_INDUSTRY_STRUCTURE):
    _fields_ = PciTypeFields

  PciCfg = PciStruct.from_address (PciCfgAddress)

  return PciCfg, PciStruct

def IS_PCI_HC(_p):
  return pci.IS_CLASS3 (_p, pci.PCI_CLASS_BRIDGE, pci.PCI_CLASS_BRIDGE_HOST, pci.PCI_IF_BRIDGE_P2P)

def GetDeviceDesc (VendorId: int, DeviceId: int) -> str:
  VendorName, DeviceDict = pciids.PciIds.get (VendorId, (f"Vendor {VendorId:04x}", {}))
  DeviceName, _          = DeviceDict.get (DeviceId, (f"Device {DeviceId:04x}", {}))
  return f"{VendorName} {DeviceName} [{VendorId:04x}:{DeviceId:04x}]"

def CollectBusDevices (PciCfgBase: int, Bus: int, EndBus: int = 0xFF, Visited = None) -> list:
  if Visited is None:
    Visited = set ()
  if Bus > EndBus or Bus in Visited:
    return []
  Visited.add (Bus)
  devices = []

  for Dev in range (pci.PCI_MAX_DEVICE + 1):
    for Func in range (pci.PCI_MAX_FUNC + 1):

      PciCfgOffset = pci.PCI_ECAM_ADDRESS (Bus, Dev, Func, 0)
      PciObj, _    = BuildPciHeader (PciCfgBase, PciCfgOffset)

      VendorId = PciObj.Hdr.VendorId
      if VendorId in (0xFFFF, 0x0000) and Func == 0:
        break

      if VendorId in (0xFFFF, 0x0000):
        continue

      DeviceId = PciObj.Hdr.DeviceId
      IsMulti  = pci.IS_PCI_MULTI_FUNC (PciObj)
      IsBridge = pci.IS_PCI_BRIDGE (PciObj)

      dev_entry = {
        "bus":      Bus,
        "dev":      Dev,
        "func":     Func,
        "vid":      VendorId,
        "did":      DeviceId,
        "desc":     GetDeviceDesc (VendorId, DeviceId),
        "is_bridge": IsBridge,
        "sec_bus":  PciObj.Cfg.SecondaryBus if IsBridge else 0,
        "sub_bus":  PciObj.Cfg.SubordinateBus if IsBridge else 0,
        "children": [],
      }

      if (IsBridge and Bus < dev_entry["sec_bus"] <= dev_entry["sub_bus"] and
          dev_entry["sec_bus"] <= EndBus):
        dev_entry["children"] = CollectBusDevices (
            PciCfgBase, dev_entry["sec_bus"], min (dev_entry["sub_bus"], EndBus), Visited)

      devices.append (dev_entry)

      if Func == 0 and not IsMulti:
        break

  return devices

def PrintBusTree (devices: list, line_prefix: str, cont_prefix: str, is_root: bool = False) -> None:
  if not devices:
    if is_root:
      print (line_prefix)
    return

  total = len (devices)
  for idx, dev in enumerate (devices):
    is_first = (idx == 0)
    is_last  = (idx == total - 1)

    conn = "\\-" if is_last else "+-"

    dev_line_prefix = (line_prefix if (is_first and is_root) else cont_prefix) + conn
    branch_bar      = "  " if is_last else "| "
    dev_cont_prefix = cont_prefix + branch_bar

    bdf_str = f"{dev['bus']:02x}:{dev['dev']:02x}.{dev['func']:x}"

    if dev["is_bridge"]:
      sec = dev["sec_bus"]
      sub = dev["sub_bus"]
      bus_tag = f"-[{sec:02x}-{sub:02x}]--"

      print (f"{dev_line_prefix}{bdf_str}{bus_tag}  {dev['desc']}")

      if dev["children"]:
        child_cont_prefix = dev_cont_prefix + " " * (len (bdf_str) + len (bus_tag))
        PrintBusTree (dev["children"], child_cont_prefix, child_cont_prefix, is_root=False)
    else:
      print (f"{dev_line_prefix}{bdf_str}  {dev['desc']}")

def ScanBus (McfgDesc) -> None:
  PciCfgBase  = McfgDesc.BaseAddress
  Segment     = McfgDesc.PciSegmentGroupNumber
  StartBus    = McfgDesc.StartBusNumber
  EndBus      = McfgDesc.EndBusNumber
  root_prefix = f"-[{Segment:04x}:{StartBus:02x}-{EndBus:02x}]-"
  root_cont   = " " * len (root_prefix)
  devices     = CollectBusDevices (PciCfgBase, StartBus, EndBus)
  PrintBusTree (devices, root_prefix, root_cont, is_root=True)

if __name__ == '__main__':

  AcpiRaw    = ExtractTable (b'MCFG', 0)
  AcpiObj, _ = AcpiMcfgParser (AcpiRaw)
  for McfgDesc in AcpiObj.McfgDesc:
    ScanBus (McfgDesc)

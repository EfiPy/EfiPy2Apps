# PciConfigurationSpace.py
#
# Copyright (C) 2025 MaxWu efipy.core@gmail.com All rights reserved.
#   GPL-2.0
#
# Reference from
#   1. https://github.com/torvalds/linux/blob/master/include/uapi/linux/pci_regs.h
#   2. https://github.com/reactos/reactos/blob/master/sdk/include/xdk/iotypes.h
#   3. https://github.com/zephyrproject-rtos/zephyr/blob/main/include/zephyr/drivers/pcie/cap.h
#

import copy
import EfiPy2 as EfiPy
from EfiPy2.MdePkg.IndustryStandard import EFIPY_INDUSTRY_STRUCTURE, EFIPY_INDUSTRY_UNION
import EfiPy2.MdePkg.IndustryStandard.Pci as pci

from EfiPy2.Lib.Acpi.AcpiRetrieve   import ExtractTable
from EfiPy2.Lib.Acpi.AcpiMcfgParser import AcpiMcfgParser

class EFIPY_PCI_CAPABILITY_MSI32_MASK (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Hdr",                 pci.EFI_PCI_CAPABILITY_HDR),
    ("MsgCtrlReg",          EfiPy.UINT16),
    ("MsgAddrReg",          EfiPy.UINT32),
    ("MsgDataReg",          EfiPy.UINT16),
    ("Reserved",            EfiPy.UINT16),
    ("MaskBits",            EfiPy.UINT32),
    ("PendingBits",         EfiPy.UINT32),
    ]

class EFIPY_PCI_CAPABILITY_MSI64_MASK (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Hdr",                 pci.EFI_PCI_CAPABILITY_HDR),
    ("MsgCtrlReg",          EfiPy.UINT16),
    ("MsgAddrRegLsdw",      EfiPy.UINT32),
    ("MsgAddrRegMsdw",      EfiPy.UINT32),
    ("MsgDataReg",          EfiPy.UINT16),
    ("Reserved",            EfiPy.UINT16),
    ("MaskBits",            EfiPy.UINT32),
    ("PendingBits",         EfiPy.UINT32),
    ]

class EFIPY_PCI_CAPABILITY_HOTPLUG (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Hdr",                 pci.EFI_PCI_CAPABILITY_HDR),
    ("ControlStatus",       EfiPy.UINT8),
    ("Reserved",            EfiPy.UINT8),
    ]

EFIPY_PCI_CAPABILITY_HT         = 0x08    # HyperTransport

class EFIPY_PCI_CAPABILITY_HT_PRI (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Hdr",                 pci.EFI_PCI_CAPABILITY_HDR),
    ("Command",             EfiPy.UINT16),
    ("LinkControl0",        EfiPy.UINT16),
    ("LinkConfig0",         EfiPy.UINT16),
    ("LinkControl1",        EfiPy.UINT16),
    ("LinkConfig1",         EfiPy.UINT16),
    ("RevisionId",          EfiPy.UINT8),
    ("LinkFreq0",           EfiPy.UINT8),
    ("LinkError0",          EfiPy.UINT8),
    ("LinkFreqCap0",        EfiPy.UINT8),
    ("Feature",             EfiPy.UINT8),
    ("LinkFreq1",           EfiPy.UINT8),
    ("LinkError1",          EfiPy.UINT8),
    ("LinkFreqCap1",        EfiPy.UINT8),
    ("EnumerationScratchpad", EfiPy.UINT16),
    ("ErrorHandling",       EfiPy.UINT16),
    ("MemBaseUpper",        EfiPy.UINT8),
    ("MemLimitUpper",       EfiPy.UINT8),
    ("BusNumber",           EfiPy.UINT8),
    ("Reserved",            EfiPy.UINT8),
    ]

class EFIPY_PCI_CAPABILITY_HT_SEC (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Hdr",                 pci.EFI_PCI_CAPABILITY_HDR),
    ("Command",             EfiPy.UINT16),
    ("LinkControl",         EfiPy.UINT16),
    ("LinkConfig",          EfiPy.UINT16),
    ("RevisionId",          EfiPy.UINT8),
    ("LinkFreq",            EfiPy.UINT8),
    ("LinkError",           EfiPy.UINT8),
    ("LinkFreqCap",         EfiPy.UINT8),
    ("Feature",             EfiPy.UINT16),
    ("EnumerationScratchpad", EfiPy.UINT16),
    ("ErrorHandling",       EfiPy.UINT16),
    ("MemBaseUpper",        EfiPy.UINT8),
    ("MemLimitUpper",       EfiPy.UINT8),
    ("ExtendedControl",     EfiPy.UINT16),
    ("Reserved",            EfiPy.UINT16),
    ]

class EFIPY_PCI_CAPABILITY_HT_MSI (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Hdr",                 pci.EFI_PCI_CAPABILITY_HDR),
    ("Command",             EfiPy.UINT16),
    ("AddressLo",           EfiPy.UINT32),
    ("AddressHi",           EfiPy.UINT32),
    ]

class EFIPY_PCI_CAPABILITY_HT_HDR (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Hdr",                 pci.EFI_PCI_CAPABILITY_HDR),
    ("Command",             EfiPy.UINT16),
    ]

EFIPY_PCI_CAPABILITY_DEBUG      = 0x0A    # Debug port

class EFIPY_PCI_CAPABILITY_DEBUG_PORT (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Hdr",                 pci.EFI_PCI_CAPABILITY_HDR),
    ("Offset",              EfiPy.UINT16, 13),
    ("BarNumber",           EfiPy.UINT16, 3),
    ]

EFIPY_PCI_CAPABILITY_CCRC       = 0x0B    # CompactPCI Central Resource Control

class EFIPY_PCI_CAPABILITY_CCRC_STRUCT (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Hdr",                 pci.EFI_PCI_CAPABILITY_HDR),
    ("ControlStatus",       EfiPy.UINT16),
    ]

EFIPY_PCI_CAPABILITY_ID_SHPC    = 0x0C    # PCI Standard Hot-Plug Controller

class EFIPY_PCI_CAPABILITY_SHPC (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Hdr",                 pci.EFI_PCI_CAPABILITY_HDR),
    ("DwordSelect",         EfiPy.UINT8),
    ("Pending",             EfiPy.UINT8),
    ("Data",                EfiPy.UINT32),
    ]

EFIPY_PCI_CAPABILITY_ID_SSVID   = 0x0D

class EFIPY_PCI_CAPABILITY_SSVID (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Hdr",                 pci.EFI_PCI_CAPABILITY_HDR),
    ("Reserved",            EfiPy.UINT16),
    ("VendorId",            EfiPy.UINT16),
    ("DeviceID",            EfiPy.UINT16),
    ]

EFIPY_PCI_CAPABILITY_AGP        = 0x0E    # AGP 8X
EFIPY_PCI_CAPABILITY_SECURE     = 0x0F    # Secure Device

class EFIPY_PCI_CAPABILITY_SECURE_DEV (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Hdr",                 pci.EFI_PCI_CAPABILITY_HDR),
    ("Capabilities",        EfiPy.UINT16),
    ("BaseAddressLow",      EfiPy.UINT32),
    ("BaseAddressHigh",     EfiPy.UINT32),
    ("MsiRange",            EfiPy.UINT32),
    ("Control",             EfiPy.UINT32),
    ("Misc",                EfiPy.UINT32),
    ]

class EFIPY_PCI_CAPABILITY_PCIEXP_V1 (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Hdr",                 pci.EFI_PCI_CAPABILITY_HDR),
    ("Capability",          pci.PCI_REG_PCIE_CAPABILITY),
    ("DeviceCapability",    pci.PCI_REG_PCIE_DEVICE_CAPABILITY),
    ("DeviceControl",       pci.PCI_REG_PCIE_DEVICE_CONTROL),
    ("DeviceStatus",        pci.PCI_REG_PCIE_DEVICE_STATUS),
    ("LinkCapability",      pci.PCI_REG_PCIE_LINK_CAPABILITY),
    ("LinkControl",         pci.PCI_REG_PCIE_LINK_CONTROL),
    ("LinkStatus",          pci.PCI_REG_PCIE_LINK_STATUS),
    ("SlotCapability",      pci.PCI_REG_PCIE_SLOT_CAPABILITY),
    ("SlotControl",         pci.PCI_REG_PCIE_SLOT_CONTROL),
    ("SlotStatus",          pci.PCI_REG_PCIE_SLOT_STATUS),
    ("RootControl",         pci.PCI_REG_PCIE_ROOT_CONTROL),
    ("RootCapability",      pci.PCI_REG_PCIE_ROOT_CAPABILITY),
    ("RootStatus",          pci.PCI_REG_PCIE_ROOT_STATUS),
    ]

EFIPY_PCI_CAPABILITY_ID_MSI_X   = 0x11

class EFIPY_PCI_CAPABILITY_MSI_X (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Hdr",                 pci.EFI_PCI_CAPABILITY_HDR),
    ("MessageControl",      EfiPy.UINT16),
    ("TableOffset",         EfiPy.UINT32),
    ("PbaOffset",           EfiPy.UINT32),
    ]

EFIPY_PCI_CAPABILITY_ID_SATA    = 0x12

class EFIPY_PCI_CAPABILITY_SATA (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Hdr",                 pci.EFI_PCI_CAPABILITY_HDR),

    ("MinorVersion",        EfiPy.UINT8, 4),
    ("MajorVersion",        EfiPy.UINT8, 4),
    ("Reserved1",           EfiPy.UINT8),

    ("BarLoc",              EfiPy.UINT32, 4),
    ("BarOfst",             EfiPy.UINT32, 20),
    ("Reserved2",           EfiPy.UINT32, 8),
    ]

EFIPY_PCI_CAPABILITY_ID_AF      = 0x13    # Advanced Features (AF)

class EFIPY_PCI_CAPABILITY_AF (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Hdr",                 pci.EFI_PCI_CAPABILITY_HDR),
    ("Length",              EfiPy.UINT8),
    ("AfCapabilities",      EfiPy.UINT8),
    ("AfControl",           EfiPy.UINT8),
    ("AfStatus",            EfiPy.UINT8),
    ]

EFIPY_PCI_CAPABILITY_ID_EA      = 0x14    # Enhanced Allocation

class EFIPY_PCI_CAPABILITY_EA_HDR (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Hdr",                 pci.EFI_PCI_CAPABILITY_HDR),
    ("NumEntries",          EfiPy.UINT8, 6),
    ("Reserved",            EfiPy.UINT8, 2),
    ("FirstEntry",          EfiPy.UINT8),
    ]

EFIPY_PCI_CAPABILITY_ID_FPB     = 0x15    # Flattening Portal Bridge

class EFIPY_PCI_CAPABILITY_FPB (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Hdr",                 pci.EFI_PCI_CAPABILITY_HDR),
    ("Capabilities",        EfiPy.UINT16),
    ("RidVectorControl1",   EfiPy.UINT32),
    ("RidVectorControl2",   EfiPy.UINT32),
    ("MemLowVectorControl", EfiPy.UINT32),
    ("MemHighVectorControl1", EfiPy.UINT32),
    ("MemHighVectorControl2", EfiPy.UINT32),
    ("VectorAccessControl", EfiPy.UINT32),
    ("VectorAccessData",    EfiPy.UINT32),
    ]

# ------------------------------------------------------------
# PCIe Extended Capability Additional Structures (0x100 ~ 0xFFF)
# ------------------------------------------------------------
EFIPY_PCIE_EXT_CAPABILITY_ID_CAC       = 0x000C
EFIPY_PCIE_EXT_CAPABILITY_ID_ATS       = pci.EFI_PCIE_CAPABILITY_ID_ATS      # 0x000F
EFIPY_PCIE_EXT_CAPABILITY_ID_PRI       = 0x0013
EFIPY_PCIE_EXT_CAPABILITY_ID_PASID     = 0x001B
EFIPY_PCIE_EXT_CAPABILITY_ID_LNR       = 0x001C
EFIPY_PCIE_EXT_CAPABILITY_ID_DPC       = 0x001D
EFIPY_PCIE_EXT_CAPABILITY_ID_PTM       = 0x001F
EFIPY_PCIE_EXT_CAPABILITY_ID_DVSEC     = 0x0023
EFIPY_PCIE_EXT_CAPABILITY_ID_DLF       = 0x0025
EFIPY_PCIE_EXT_CAPABILITY_ID_MARGINING = 0x0027

class EFIPY_PCIE_EXT_CAPABILITY_ATS (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Header",              pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_HEADER),
    ("AtsCapability",       EfiPy.UINT16),
    ("AtsControl",          EfiPy.UINT16),
    ]

class EFIPY_PCIE_EXT_CAPABILITY_PRI (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Header",                          pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_HEADER),
    ("Control",                         EfiPy.UINT16),
    ("Status",                          EfiPy.UINT16),
    ("OutstandingPageRequestCapacity",  EfiPy.UINT32),
    ("OutstandingPageRequestAllocation", EfiPy.UINT32),
    ]

class EFIPY_PCIE_EXT_CAPABILITY_PASID (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Header",              pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_HEADER),
    ("PasidCapability",     EfiPy.UINT16),
    ("PasidControl",        EfiPy.UINT16),
    ]

class EFIPY_PCIE_EXT_CAPABILITY_LNR (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Header",              pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_HEADER),
    ("LnrCapability",       EfiPy.UINT16),
    ("LnrControl",          EfiPy.UINT16),
    ]

class EFIPY_PCIE_EXT_CAPABILITY_DPC (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Header",              pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_HEADER),
    ("DpcCapability",       EfiPy.UINT16),
    ("DpcControl",          EfiPy.UINT16),
    ("DpcStatus",           EfiPy.UINT16),
    ("DpcErrorSourceId",    EfiPy.UINT16),
    ]

class EFIPY_PCIE_EXT_CAPABILITY_PTM (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Header",              pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_HEADER),
    ("PtmCapability",       EfiPy.UINT32),
    ("PtmControl",          EfiPy.UINT32),
    ]

class EFIPY_PCIE_EXT_CAPABILITY_DLF (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Header",              pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_HEADER),
    ("DlfCapabilities",     EfiPy.UINT32),
    ("DlfStatus",           EfiPy.UINT32),
    ]

class EFIPY_PCIE_EXT_CAPABILITY_MARGINING (EFIPY_INDUSTRY_STRUCTURE):
  _fields_ = [
    ("Header",              pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_HEADER),
    ("PortCapabilities",    EfiPy.UINT16),
    ("PortStatus",          EfiPy.UINT16),
    ]

class PCI_DEVICE_INDEPENDENT_REGION_UNION (pci.EFIPY_INDUSTRY_UNION):

  _fields_ = [
    ('Hdr',     pci.PCI_DEVICE_INDEPENDENT_REGION),
    ('Raw',     EfiPy.UINT32 * (EfiPy.sizeof (pci.PCI_DEVICE_INDEPENDENT_REGION) // (EfiPy.sizeof (EfiPy.UINT32))))
  ]

def PciCapGetMsiStruct (CapId, PciRaw, CapPtr):
  MsiObj = pci.EFI_PCI_CAPABILITY_MSI32.from_buffer (PciRaw, CapPtr)
  Is64Bit = bool (MsiObj.MsgCtrlReg & 0x0080)
  IsMask  = bool (MsiObj.MsgCtrlReg & 0x0100)
  if Is64Bit and IsMask:
    return EFIPY_PCI_CAPABILITY_MSI64_MASK
  elif Is64Bit:
    return pci.EFI_PCI_CAPABILITY_MSI64
  elif IsMask:
    return EFIPY_PCI_CAPABILITY_MSI32_MASK
  return pci.EFI_PCI_CAPABILITY_MSI32

def PciCapGetPcixStruct (CapId, PciRaw, CapPtr):
  HdrType = PciRaw [pci.PCI_HEADER_TYPE_OFFSET] & pci.HEADER_LAYOUT_CODE
  if HdrType == pci.HEADER_TYPE_PCI_TO_PCI_BRIDGE:
    return pci.EFI_PCI_CAPABILITY_PCIX_BRDG
  return pci.EFI_PCI_CAPABILITY_PCIX

def PciCapGetHtStruct (CapId, PciRaw, CapPtr):
  HtHdr = EFIPY_PCI_CAPABILITY_HT_HDR.from_buffer (PciRaw, CapPtr)
  CapType = (HtHdr.Command >> 13) & 0x07
  if CapType == 0x00:
    return EFIPY_PCI_CAPABILITY_HT_PRI
  elif CapType == 0x01:
    return EFIPY_PCI_CAPABILITY_HT_SEC
  elif ((HtHdr.Command >> 11) & 0x1F) == 0x15:
    return EFIPY_PCI_CAPABILITY_HT_MSI
  return EFIPY_PCI_CAPABILITY_HT_HDR

def PciCapGetVendorStruct (CapId, PciRaw, CapPtr):
  StructLength = PciRaw [CapPtr + 2]
  if StructLength < 3:
    raise ValueError ('Vendor capability length is less than 3')
  class EFIPY_PCI_CAPABILITY_VENDOR (EFIPY_INDUSTRY_STRUCTURE):
    _fields_ = [
    ("CapabilityID",  EfiPy.UINT8),
    ("NextItemPtr",   EfiPy.UINT8),
    ("Length",        EfiPy.UINT8),
    ("VendorRaw",     EfiPy.UINT8 * (StructLength - 3)),
    ]
  return EFIPY_PCI_CAPABILITY_VENDOR

def PciCapGetPcieStruct (CapId, PciRaw, CapPtr):
  PcieCapVer = PciRaw [CapPtr + 2] & 0x0F
  if PcieCapVer <= 1:
    return EFIPY_PCI_CAPABILITY_PCIEXP_V1
  return pci.PCI_CAPABILITY_PCIEXP

def PciCapGetEaStruct (CapId, PciRaw, CapPtr):
  NumEntries = PciRaw [CapPtr + 2] & 0x3F
  HdrType    = PciRaw [pci.PCI_HEADER_TYPE_OFFSET] & pci.HEADER_LAYOUT_CODE
  Offset     = CapPtr + (8 if HdrType == pci.HEADER_TYPE_PCI_TO_PCI_BRIDGE else 4)
  for _ in range (NumEntries):
    if Offset + 4 > len (PciRaw):
      raise ValueError ('Truncated Enhanced Allocation entry')
    EntrySizeDwords = PciRaw [Offset] & 0x07
    Offset += (EntrySizeDwords + 1) * 4
  TotalLen = max (Offset - CapPtr, 4)
  class EFIPY_PCI_CAPABILITY_EA (EFIPY_INDUSTRY_STRUCTURE):
    _fields_ = [
      ("Hdr",         pci.EFI_PCI_CAPABILITY_HDR),
      ("NumEntries",  EfiPy.UINT8, 6),
      ("Reserved",    EfiPy.UINT8, 2),
      ("EaRaw",       EfiPy.UINT8 * (TotalLen - 3)),
    ]
  return EFIPY_PCI_CAPABILITY_EA

def PciCapGetDefault (CapId, PciRaw, CapPtr):
  return pci.EFI_PCI_CAPABILITY_HDR

PciCapDict2 = {
  pci.EFI_PCI_CAPABILITY_ID_PMI:      lambda CapId, PciRaw, CapPtr: pci.EFI_PCI_CAPABILITY_PMI,         # 0x01
  pci.EFI_PCI_CAPABILITY_ID_AGP:      lambda CapId, PciRaw, CapPtr: pci.EFI_PCI_CAPABILITY_AGP,         # 0x02
  pci.EFI_PCI_CAPABILITY_ID_VPD:      lambda CapId, PciRaw, CapPtr: pci.EFI_PCI_CAPABILITY_VPD,         # 0x03
  pci.EFI_PCI_CAPABILITY_ID_SLOTID:   lambda CapId, PciRaw, CapPtr: pci.EFI_PCI_CAPABILITY_SLOTID,      # 0x04
  pci.EFI_PCI_CAPABILITY_ID_MSI:      PciCapGetMsiStruct,                                               # 0x05
  pci.EFI_PCI_CAPABILITY_ID_HOTPLUG:  lambda CapId, PciRaw, CapPtr: EFIPY_PCI_CAPABILITY_HOTPLUG,       # 0x06
  pci.EFI_PCI_CAPABILITY_ID_PCIX:     PciCapGetPcixStruct,                                              # 0x07
  EFIPY_PCI_CAPABILITY_HT:            PciCapGetHtStruct,                                                # 0x08
  pci.EFI_PCI_CAPABILITY_ID_VENDOR:   PciCapGetVendorStruct,                                            # 0x09
  EFIPY_PCI_CAPABILITY_DEBUG:         lambda CapId, PciRaw, CapPtr: EFIPY_PCI_CAPABILITY_DEBUG_PORT,    # 0x0A
  EFIPY_PCI_CAPABILITY_CCRC:          lambda CapId, PciRaw, CapPtr: EFIPY_PCI_CAPABILITY_CCRC_STRUCT,   # 0x0B
  EFIPY_PCI_CAPABILITY_ID_SHPC:       lambda CapId, PciRaw, CapPtr: EFIPY_PCI_CAPABILITY_SHPC,          # 0x0C
  EFIPY_PCI_CAPABILITY_ID_SSVID:      lambda CapId, PciRaw, CapPtr: EFIPY_PCI_CAPABILITY_SSVID,         # 0x0D
  EFIPY_PCI_CAPABILITY_AGP:           lambda CapId, PciRaw, CapPtr: pci.EFI_PCI_CAPABILITY_AGP,         # 0x0E
  EFIPY_PCI_CAPABILITY_SECURE:        lambda CapId, PciRaw, CapPtr: EFIPY_PCI_CAPABILITY_SECURE_DEV,    # 0x0F
  pci.EFI_PCI_CAPABILITY_ID_PCIEXP:   PciCapGetPcieStruct,                                              # 0x10
  EFIPY_PCI_CAPABILITY_ID_MSI_X:      lambda CapId, PciRaw, CapPtr: EFIPY_PCI_CAPABILITY_MSI_X,         # 0x11
  EFIPY_PCI_CAPABILITY_ID_SATA:       lambda CapId, PciRaw, CapPtr: EFIPY_PCI_CAPABILITY_SATA,          # 0x12
  EFIPY_PCI_CAPABILITY_ID_AF:         lambda CapId, PciRaw, CapPtr: EFIPY_PCI_CAPABILITY_AF,            # 0x13
  EFIPY_PCI_CAPABILITY_ID_EA:         PciCapGetEaStruct,                                                # 0x14
  EFIPY_PCI_CAPABILITY_ID_FPB:        lambda CapId, PciRaw, CapPtr: EFIPY_PCI_CAPABILITY_FPB,           # 0x15
}

def PcieExtCapGetVendorSpecificStruct (ExtCapId, PciRaw, ExtCapPtr):
  VsecObj = pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_VENDOR_SPECIFIC.from_buffer (PciRaw, ExtCapPtr)
  VsecLen = (VsecObj.VendorSpecificHeader >> 20) & 0xFFF
  if VsecLen < 8:
    raise ValueError ('VSEC length is less than 8')
  class EFIPY_PCIE_EXT_CAPABILITY_VSEC (EFIPY_INDUSTRY_STRUCTURE):
    _fields_ = [
      ("Header",                pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_HEADER),
      ("VendorSpecificHeader",  EfiPy.UINT32),
      ("VendorSpecific",        EfiPy.UINT8 * (VsecLen - 8)),
    ]
  return EFIPY_PCIE_EXT_CAPABILITY_VSEC

def PcieExtCapGetLinkDeclarationStruct (ExtCapId, PciRaw, ExtCapPtr):
  LinkObj   = pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_LINK_DECLARATION.from_buffer (PciRaw, ExtCapPtr)
  LinkCount = max ((LinkObj.ElementSelfDescription >> 8) & 0xFF, 1)
  class EFIPY_PCIE_EXT_CAPABILITY_LINK_DECL (EFIPY_INDUSTRY_STRUCTURE):
    _fields_ = [
      ("Header",                  pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_HEADER),
      ("ElementSelfDescription",  EfiPy.UINT32),
      ("Reserved",                EfiPy.UINT32),
      ("LinkEntry",               EfiPy.UINT32 * LinkCount),
    ]
  return EFIPY_PCIE_EXT_CAPABILITY_LINK_DECL

def PcieExtCapGetResizableBarStruct (ExtCapId, PciRaw, ExtCapPtr):
  RbarObj = pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_RESIZABLE_BAR.from_buffer (PciRaw, ExtCapPtr)
  NumBars = max (RbarObj.Capability[0].ResizableBarControl.Bits.ResizableBarNumber, 1)
  class EFIPY_PCIE_EXT_CAPABILITY_RESIZABLE_BAR (EFIPY_INDUSTRY_STRUCTURE):
    _fields_ = [
      ("Header",      pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_HEADER),
      ("Capability",  pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_RESIZABLE_BAR_ENTRY * NumBars),
    ]
  return EFIPY_PCIE_EXT_CAPABILITY_RESIZABLE_BAR

def PcieExtCapGetDvsecStruct (ExtCapId, PciRaw, ExtCapPtr):
  DvsecObj = pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_DESIGNATED_VENDOR_SPECIFIC.from_buffer (PciRaw, ExtCapPtr)
  DvsecLen = DvsecObj.DesignatedVendorSpecificHeader1.Bits.DvsecLength
  if DvsecLen < 10:
    raise ValueError ('DVSEC length is less than 10')
  class EFIPY_PCIE_EXT_CAPABILITY_DVSEC (EFIPY_INDUSTRY_STRUCTURE):
    _fields_ = [
      ("Header",                          pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_HEADER),
      ("DesignatedVendorSpecificHeader1", pci.PCI_EXPRESS_DESIGNATED_VENDOR_SPECIFIC_HEADER_1),
      ("DesignatedVendorSpecificHeader2", pci.PCI_EXPRESS_DESIGNATED_VENDOR_SPECIFIC_HEADER_2),
      ("DesignatedVendorSpecific",        EfiPy.UINT8 * (DvsecLen - 10)),
    ]
  return EFIPY_PCIE_EXT_CAPABILITY_DVSEC

def PcieExtCapGetDefault (ExtCapId, PciRaw, ExtCapPtr):
  return pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_HEADER

PcieExtCapDict = {
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_ADVANCED_ERROR_REPORTING_ID:                lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_ADVANCED_ERROR_REPORTING,               # 0x0001
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_VIRTUAL_CHANNEL_ID:                         lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_VIRTUAL_CHANNEL_CAPABILITY,             # 0x0002
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_SERIAL_NUMBER_ID:                           lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_SERIAL_NUMBER,                          # 0x0003
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_POWER_BUDGETING_ID:                         lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_POWER_BUDGETING,                        # 0x0004
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_LINK_DECLARATION_ID:                        PcieExtCapGetLinkDeclarationStruct,                                                                         # 0x0005
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_LINK_CONTROL_ID:                            lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_INTERNAL_LINK_CONTROL,                  # 0x0006
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_EVENT_COLLECTOR_ENDPOINT_ASSOCIATION_ID:    lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_EVENT_COLLECTOR_ENDPOINT_ASSOCIATION,   # 0x0007
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_MULTI_FUNCTION_VIRTUAL_CHANNEL_ID:          lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_MULTI_FUNCTION_VIRTUAL_CHANNEL_CAPABILITY, # 0x0008
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_VIRTUAL_CHANNEL_MFVC:                       lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_VIRTUAL_CHANNEL_CAPABILITY,             # 0x0009
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_RCRB_HEADER_ID:                             lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_RCRB_HEADER,                            # 0x000A
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_VENDOR_SPECIFIC_ID:                         PcieExtCapGetVendorSpecificStruct,                                                                          # 0x000B
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_ACS_EXTENDED_ID:                            lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_ACS_EXTENDED,                           # 0x000D
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_ARI_CAPABILITY_ID:                          lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_ARI_CAPABILITY,                         # 0x000E
  EFIPY_PCIE_EXT_CAPABILITY_ID_ATS:                                               lambda CapId, PciRaw, CapPtr: EFIPY_PCIE_EXT_CAPABILITY_ATS,                                                # 0x000F
  pci.EFI_PCIE_CAPABILITY_ID_SRIOV:                                               lambda CapId, PciRaw, CapPtr: pci.SR_IOV_CAPABILITY_REGISTER,                                               # 0x0010
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_MULTICAST_ID:                               lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_MULTICAST,                              # 0x0012
  EFIPY_PCIE_EXT_CAPABILITY_ID_PRI:                                               lambda CapId, PciRaw, CapPtr: EFIPY_PCIE_EXT_CAPABILITY_PRI,                                                # 0x0013
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_RESIZABLE_BAR_ID:                           PcieExtCapGetResizableBarStruct,                                                                            # 0x0015
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_DYNAMIC_POWER_ALLOCATION_ID:                lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_DYNAMIC_POWER_ALLOCATION,               # 0x0016
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_TPH_ID:                                     lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_TPH,                                    # 0x0017
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_LATENCE_TOLERANCE_REPORTING_ID:             lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_LATENCE_TOLERANCE_REPORTING,            # 0x0018
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_SECONDARY_PCIE_ID:                          lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_SECONDARY_PCIE,                         # 0x0019
  EFIPY_PCIE_EXT_CAPABILITY_ID_PASID:                                             lambda CapId, PciRaw, CapPtr: EFIPY_PCIE_EXT_CAPABILITY_PASID,                                              # 0x001B
  EFIPY_PCIE_EXT_CAPABILITY_ID_LNR:                                               lambda CapId, PciRaw, CapPtr: EFIPY_PCIE_EXT_CAPABILITY_LNR,                                                # 0x001C
  EFIPY_PCIE_EXT_CAPABILITY_ID_DPC:                                               lambda CapId, PciRaw, CapPtr: EFIPY_PCIE_EXT_CAPABILITY_DPC,                                                # 0x001D
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_L1_PM_SUBSTATES_ID:                         lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_L1_PM_SUBSTATES,                        # 0x001E
  EFIPY_PCIE_EXT_CAPABILITY_ID_PTM:                                               lambda CapId, PciRaw, CapPtr: EFIPY_PCIE_EXT_CAPABILITY_PTM,                                                # 0x001F
  EFIPY_PCIE_EXT_CAPABILITY_ID_DVSEC:                                             PcieExtCapGetDvsecStruct,                                                                                   # 0x0023
  EFIPY_PCIE_EXT_CAPABILITY_ID_DLF:                                               lambda CapId, PciRaw, CapPtr: EFIPY_PCIE_EXT_CAPABILITY_DLF,                                                # 0x0025
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_PHYSICAL_LAYER_16_0_ID:                     lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_PHYSICAL_LAYER_16_0,                    # 0x0026
  EFIPY_PCIE_EXT_CAPABILITY_ID_MARGINING:                                         lambda CapId, PciRaw, CapPtr: EFIPY_PCIE_EXT_CAPABILITY_MARGINING,                                          # 0x0027
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_PHYSICAL_LAYER_32_0_ID:                     lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_PHYSICAL_LAYER_32_0,                    # 0x002A
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_DEVICE3_ID:                                lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_DEVICE3,                                # 0x002F
  pci.PCI_EXPRESS_EXTENDED_CAPABILITY_PHYSICAL_LAYER_64_0_ID:                     lambda CapId, PciRaw, CapPtr: pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_PHYSICAL_LAYER_64_0,                    # 0x0031
}

def GetPciCapabilityStart (PciRaw):
  HdrType = PciRaw[pci.PCI_HEADER_TYPE_OFFSET] & pci.HEADER_LAYOUT_CODE
  return 0x80 if HdrType == pci.HEADER_TYPE_CARDBUS_BRIDGE else 0x40


def GetPciCapabilityPointer (PciRaw):
  Offset = 0x14 if GetPciCapabilityStart (PciRaw) == 0x80 else pci.PCI_CAPBILITY_POINTER_OFFSET
  return PciRaw[Offset]


def ValidateCapabilityPointer (CapPtr, Start, Stop, HeaderSize, Visited):
  if CapPtr in Visited:
    raise ValueError (f'Capability list cycle at 0x{CapPtr:X}')
  if CapPtr % 4 or CapPtr < Start or CapPtr + HeaderSize > Stop:
    raise ValueError (f'Invalid capability pointer 0x{CapPtr:X} (range 0x{Start:X}..0x{Stop:X})')
  Visited.add (CapPtr)


def BuildPciCapabilitiesList (PciRaw, CapPtr: int) -> list:
  CapList = []
  Visited = set ()
  while CapPtr:
    ValidateCapabilityPointer (CapPtr, GetPciCapabilityStart (PciRaw),
                               min (len (PciRaw), 0x100), 2, Visited)
    CapId, CapNPtr = PciRaw[CapPtr:CapPtr + 2]
    CapList.append ((CapPtr, CapId, CapNPtr))
    CapPtr = CapNPtr
  return CapList


def InsertCapability (Reserved, CapPtr, CapStruct):
  CapStop = CapPtr + EfiPy.sizeof (CapStruct)
  for idx, (r, s) in enumerate (Reserved):
    # Only split unparsed bytes; never overwrite a capability already inserted.
    if CapPtr in r and issubclass (s, EfiPy.Array):
      if CapStop > r.stop:
        raise ValueError (f'Capability at 0x{CapPtr:X} overlaps another region')
      Fields = []
      if r.start < CapPtr:
        Fields.append ((range (r.start, CapPtr), EfiPy.UINT8 * (CapPtr - r.start)))
      Fields.append ((range (CapPtr, CapStop), CapStruct))
      if CapStop < r.stop:
        Fields.append ((range (CapStop, r.stop), EfiPy.UINT8 * (r.stop - CapStop)))
      Reserved[idx:idx + 1] = Fields
      return
  raise ValueError (f'Capability at 0x{CapPtr:X} is outside unparsed space')


def GetBoundedCapabilityStruct (PciRaw, CapPtr, CapId, Stop, HeaderSize, Factory):
  # Preserve absolute offsets while preventing factories from reading the next
  # capability or bytes beyond the configuration space boundary.
  BoundedRaw = bytearray (PciRaw[:Stop])
  try:
    CapStruct = Factory (CapId, BoundedRaw, CapPtr)
  except (IndexError, ValueError) as Error:
    raise ValueError (f'Invalid capability at 0x{CapPtr:X}: {Error}') from Error
  CapSize = EfiPy.sizeof (CapStruct)
  if CapSize < HeaderSize or CapPtr + CapSize > Stop:
    raise ValueError (f'Capability at 0x{CapPtr:X} has invalid size 0x{CapSize:X}; boundary 0x{Stop:X}')
  return CapStruct


def BuildPciCapabilitiesFull (PciRaw, PciReserved, CapPtr: int) -> bool:
  CapList = BuildPciCapabilitiesList (PciRaw, CapPtr)
  Offsets = sorted ([Item[0] for Item in CapList] + [min (len (PciRaw), 0x100)])
  IsPcieDevice = False
  for CapPtr, CapId, CapNPtr in CapList:
    print (f'Cap ID: 0x{CapId:02X} (offset: 0x{CapPtr:02X}, next offset: 0x{CapNPtr:02X}), in EfiPy2 database: {CapId in PciCapDict2}')
    Stop = Offsets[Offsets.index (CapPtr) + 1]
    Factory = PciCapDict2.get (CapId, PciCapGetDefault)
    CapStruct = GetBoundedCapabilityStruct (PciRaw, CapPtr, CapId, Stop, 2, Factory)
    InsertCapability (PciReserved, CapPtr, CapStruct)
    IsPcieDevice |= CapId == pci.EFI_PCI_CAPABILITY_ID_PCIEXP
  return IsPcieDevice


def BuildPcieExtCapabilitiesList (PciExtRaw, ExtCapPtr: int = pci.EFI_PCIE_CAPABILITY_BASE_OFFSET) -> list:
  ExtCapList = []
  Visited = set ()
  while ExtCapPtr:
    ValidateCapabilityPointer (ExtCapPtr, pci.EFI_PCIE_CAPABILITY_BASE_OFFSET,
                               min (len (PciExtRaw), pci.PCI_EXP_MAX_CONFIG_OFFSET), 4, Visited)
    ExtHdr = pci.PCI_EXPRESS_EXTENDED_CAPABILITIES_HEADER.from_buffer (PciExtRaw, ExtCapPtr)
    if ExtHdr.CapabilityId in (0x0000, 0xFFFF):
      break
    ExtCapList.append ((ExtCapPtr, ExtHdr.CapabilityId, ExtHdr.CapabilityVersion, ExtHdr.NextCapabilityOffset))
    ExtCapPtr = ExtHdr.NextCapabilityOffset
  return ExtCapList


def BuildPcieExtCapabilitiesFull (PciExtRaw, PcieExtReserved, ExtCapPtr: int = pci.EFI_PCIE_CAPABILITY_BASE_OFFSET) -> None:
  ExtCapList = BuildPcieExtCapabilitiesList (PciExtRaw, ExtCapPtr)
  Offsets = sorted ([Item[0] for Item in ExtCapList] + [min (len (PciExtRaw), pci.PCI_EXP_MAX_CONFIG_OFFSET)])
  for ExtCapPtr, ExtCapId, ExtCapVer, ExtCapNPtr in ExtCapList:
    print (f'ExtCap ID: 0x{ExtCapId:04X} (ver: 0x{ExtCapVer:X}, offset: 0x{ExtCapPtr:03X}, next offset: 0x{ExtCapNPtr:03X}), in EfiPy2 database: {ExtCapId in PcieExtCapDict}')
    Stop = Offsets[Offsets.index (ExtCapPtr) + 1]
    Factory = PcieExtCapDict.get (ExtCapId, PcieExtCapGetDefault)
    CapStruct = GetBoundedCapabilityStruct (PciExtRaw, ExtCapPtr, ExtCapId, Stop, 4, Factory)
    InsertCapability (PcieExtReserved, ExtCapPtr, CapStruct)


def BuildPciHeader (EcamBase: int, EcamOffset: int):

  CapNameDict = {}

  def BuildCapName (CapName, CapNameDict):
    ShowIndex = CapNameDict.get (CapName, -1)
    CapNameDict [CapName] = ShowIndex + 1
    if ShowIndex == -1:
      return CapName
    return f'{CapName}{ShowIndex + 1}'


  PciCfgAddress = EcamBase + EcamOffset

  PciCfg = PCI_DEVICE_INDEPENDENT_REGION_UNION.from_address (PciCfgAddress)

  PciTypeFields = [
      ('Hdr',     pci.PCI_DEVICE_INDEPENDENT_REGION),
    ]

  #
  # Build TYPE 00/01/02 header
  #
  if pci.IS_PCI_BRIDGE (PciCfg):
    # Type 1
    PciTypeFields.append (('Cfg', pci.PCI_BRIDGE_CONTROL_REGISTER))

  elif pci.IS_CARDBUS_BRIDGE (PciCfg):
    # Type 2 includes the subsystem IDs, legacy base and reserved bytes.
    PciTypeFields.extend ([
      ('Cfg', pci.PCI_CARDBUS_CONTROL_REGISTER),
      ('SubsystemVendorID', EfiPy.UINT16),
      ('SubsystemID', EfiPy.UINT16),
      ('LegacyModeBase', EfiPy.UINT32),
      ('CardBusReserved', EfiPy.UINT8 * 0x38),
    ])

  else:
    # Type 0
    PciTypeFields.append (('Cfg', pci.PCI_DEVICE_HEADER_TYPE_REGION))

  class PciStruct (EFIPY_INDUSTRY_STRUCTURE):
    _fields_ = PciTypeFields

  class PciUnion (EFIPY_INDUSTRY_UNION):
    _fields_ = [
        ('Fields',  PciStruct),
        ('Raw',     EfiPy.UINT8 * 0x100),
    ]

  PciCfg = PciUnion.from_address (PciCfgAddress)

  IsPcieDevice = False
  if PciCfg.Fields.Hdr.Status & pci.EFI_PCI_STATUS_CAPABILITY == pci.EFI_PCI_STATUS_CAPABILITY:

    PciRaw = (EfiPy.UINT8 * 0x100).from_address (PciCfgAddress)
    HeaderSize = EfiPy.sizeof (PciStruct)
    PciReserved = [(range (HeaderSize, 0x100), EfiPy.UINT8 * (0x100 - HeaderSize))]

    IsPcieDevice = BuildPciCapabilitiesFull (PciRaw, PciReserved, GetPciCapabilityPointer (PciRaw))

    for idx, (r, s) in enumerate (PciReserved):

      if issubclass (s, EfiPy.Structure):
        ShowName = BuildCapName (s.__name__, CapNameDict)
        PciTypeFields.append ((ShowName, s))
      else:
        ShowName = BuildCapName ('Reserved', CapNameDict)
        PciTypeFields.append ((ShowName, EfiPy.UINT8 * len(r)))

    if IsPcieDevice:
      PciExtRaw = (EfiPy.UINT8 * pci.PCI_EXP_MAX_CONFIG_OFFSET).from_address (PciCfgAddress)
      PcieExtReserved = [(range (pci.EFI_PCIE_CAPABILITY_BASE_OFFSET, pci.PCI_EXP_MAX_CONFIG_OFFSET),
                          EfiPy.UINT8 * (pci.PCI_EXP_MAX_CONFIG_OFFSET - pci.EFI_PCIE_CAPABILITY_BASE_OFFSET))]

      BuildPcieExtCapabilitiesFull (PciExtRaw, PcieExtReserved, pci.EFI_PCIE_CAPABILITY_BASE_OFFSET)

      for idx, (r, s) in enumerate (PcieExtReserved):
        if issubclass (s, EfiPy.Structure):
          ShowName = BuildCapName (s.__name__, CapNameDict)
          PciTypeFields.append ((ShowName, s))
        else:
          ShowName = BuildCapName ('Reserved', CapNameDict)
          PciTypeFields.append ((ShowName, EfiPy.UINT8 * len(r)))

    class PciStruct (EFIPY_INDUSTRY_STRUCTURE):
      _fields_ = PciTypeFields

  else:
    PciTypeFields.append (('Reserved', EfiPy.UINT8 * (0x100 - EfiPy.sizeof (PciStruct))))

    class PciStruct (EFIPY_INDUSTRY_STRUCTURE):
      _fields_ = PciTypeFields

  CfgSpaceSize = pci.PCI_EXP_MAX_CONFIG_OFFSET if IsPcieDevice else pci.PCI_MAX_CONFIG_OFFSET

  class PciUnion (EFIPY_INDUSTRY_UNION):
    _fields_ = [
        ('Fields',  PciStruct),
        ('Raw',     EfiPy.UINT8 * CfgSpaceSize),
    ]

  PciCfg = PciUnion.from_address (PciCfgAddress)

  return PciCfg, PciUnion, IsPcieDevice

if __name__ == '__main__':

  import argparse

  parser = argparse.ArgumentParser (prog = 'PciConfigurationSpace.py')
  ArgCommand = parser.add_subparsers (help = 'Dump PCI configuration space registers via MMIO.')
  parser.add_argument ('-v', '--verbose', action = 'store_true', help = 'Verbose output by Read/Dump MSR')
  args = parser.parse_args ()

  # if args.verbose == True:
  if True:
    from EfiPy2.Lib.StructDump import DumpStruct
    from EfiPy2.Lib.HexDump import HexDump

  AcpiRaw = ExtractTable (b'MCFG', 0)
  AcpiObj, AcpiType = AcpiMcfgParser (AcpiRaw)

  Bus   = 0x01
  Dev   = 0x00
  Func  = 0x00

  PciCfgOffset  = pci.PCI_ECAM_ADDRESS (Bus, Dev, Func, 0)
  PciCfgAddress = AcpiObj.McfgDesc.BaseAddress + PciCfgOffset

  PciObj, PciType, IsPcieDevice = BuildPciHeader (AcpiObj.McfgDesc.BaseAddress, PciCfgOffset)
  print (f"PCI{'e' if IsPcieDevice else ''} Base: 0x{AcpiObj.McfgDesc.BaseAddress:08X}, Device {Bus:02X}:{Dev:02X}.{Func:X} ECAM: 0x{PciCfgOffset:08X}")
  DumpStruct (0, PciObj, PciType)

  PciRaw = (EfiPy.UINT8 * 0x100).from_address (PciCfgAddress)
  if PciRaw [pci.PCI_PRIMARY_STATUS_OFFSET] & pci.EFI_PCI_STATUS_CAPABILITY == pci.EFI_PCI_STATUS_CAPABILITY:
    CapList = BuildPciCapabilitiesList (PciRaw, GetPciCapabilityPointer (PciRaw))
    print ('\nPCI capabilities list...')
    for CapPtr, CapId, CapNPtr in CapList:
      print (f'0x{CapPtr:X} 0x{CapId:X} 0x{CapNPtr:X}')
      if CapId == EFIPY_PCI_CAPABILITY_ID_MSI_X:
        MsiX = EFIPY_PCI_CAPABILITY_MSI_X.from_buffer (PciRaw, CapPtr)
        print (f'  MSI-X: entries={(MsiX.MessageControl & 0x07FF) + 1}, enabled={bool (MsiX.MessageControl & 0x8000)}, function mask={bool (MsiX.MessageControl & 0x4000)}')
        print (f'  Table: BAR{MsiX.TableOffset & 7} + 0x{MsiX.TableOffset & 0xFFFFFFF8:X}')
        print (f'  PBA: BAR{MsiX.PbaOffset & 7} + 0x{MsiX.PbaOffset & 0xFFFFFFF8:X}')
      elif CapId == pci.EFI_PCI_CAPABILITY_ID_PCIEXP:
        Flags = PciRaw[CapPtr + 2] | (PciRaw[CapPtr + 3] << 8)
        PortType = (Flags >> 4) & 0x0F
        HasSlot = bool (Flags & 0x0100) and PortType in (4, 6)
        HasRoot = PortType in (4, 10)
        print (f'  Register applicability: Slot={"applicable" if HasSlot else "N/A"}, Root={"applicable" if HasRoot else "N/A"}')

    if IsPcieDevice:
      PciExtRaw  = (EfiPy.UINT8 * pci.PCI_EXP_MAX_CONFIG_OFFSET).from_address (PciCfgAddress)
      ExtCapList = BuildPcieExtCapabilitiesList (PciExtRaw, pci.EFI_PCIE_CAPABILITY_BASE_OFFSET)
      if ExtCapList:
        print ('\nPCIe extended capabilities list...')
        for ExtCapPtr, ExtCapId, ExtCapVer, ExtCapNPtr in ExtCapList:
          print (f'0x{ExtCapPtr:03X} 0x{ExtCapId:04X} (v{ExtCapVer:X}) 0x{ExtCapNPtr:03X}')

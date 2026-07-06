# X86ApicIdDump.py
#
#   part of EfiPy2
#
# Copyright (C) 2025 - 2026 MaxWu efipy.core@gmail.com
#   GPL-2.0
#

import EfiPy2 as EfiPy
from EfiPy2.Lib.X86Processor import X86Processors, X86ProcessorArray
from EfiPy2.Lib.CpuIdIntel import CPUID_GENERIC_REGISTERs
from EfiPy2.Lib.Msr import MSR_GENERIC_REGISTER
from EfiPy2.MdePkg.Register.Intel.ArchitecturalMsr import MSR_IA32_APIC_BASE_REGISTER

print (f'APIC base address: 0x{X86Processors.LocalApicAddress:08X}')
print (f'Processor IDs from EFI_MP_SERVICES_PROTOCOL: {X86Processors.ProcessorIds}')
print (f'WhoAmI: {X86Processors.WhoAmI}, Processor numbers: {len (X86Processors)}, {len (X86ProcessorArray)}')

for Index, Processor in enumerate (X86ProcessorArray):

  print (f'\nCPU {Index} infromation....')

  CpuIndex = 0x0B

  CpuIdReg = CPUID_GENERIC_REGISTERs()
  Processor.CpuId (CpuIndex, 0x00, CpuIdReg)
  print (f'  From CPUID 0x{CpuIndex:02X}: 0x{CpuIdReg.EDX:08X}')

  MsrIndex = 0x1B
  MsrApicReg = MSR_IA32_APIC_BASE_REGISTER ()
  Processor.RdMsr (MsrIndex, MsrApicReg)
  print (f'  MsrApicReg.Uint64:     0x{MsrApicReg.Uint64:016X}')
  print (f'  MsrApicReg.Bits.BSP:   0x{MsrApicReg.Bits.BSP:02X}')
  print (f'  MsrApicReg.Bits.EXTD:  0x{MsrApicReg.Bits.EXTD:02X}')
  print (f'  MsrApicReg.Bits.EN:    0x{MsrApicReg.Bits.EN:02X}')
  MmioAddress = (MsrApicReg.Bits.ApicBaseHi << 32) | (MsrApicReg.Bits.ApicBase << 12)
  print (f'  Local Apic MMIO:       0x{MmioAddress:016X}')
  MmioAddress += 0x20
  print (f'  From MMIO 0x{MmioAddress:08X}: 0x{Processor.MemGet32(MmioAddress):08X}')


  ApicExtd = MsrApicReg.Bits.EXTD
  if MsrApicReg.Bits.EXTD != 0x01:
    MsrApicReg.Bits.EXTD = 1
    Processor.WrMsr (MsrIndex, MsrApicReg)

  MsrIndex = 0x802
  MsrReg = MSR_GENERIC_REGISTER ()
  Processor.RdMsr (MsrIndex, MsrReg)
  print (f'  From MSR 0x{MsrIndex:X}: 0x{MsrReg.Uint64:016X}')
# X86CpuInfo.py
#
#   part of EfiPy2
#
# Copyright (C) 2025 - 2026 MaxWu efipy.core@gmail.com
#   GPL-2.0
#

import EfiPy2 as EfiPy
from EfiPy2.Lib import CpuIdIntel as CpuId
from EfiPy2.Lib.X86Processor import Me, X86ProcessorArray

import argparse
parser = argparse.ArgumentParser (prog = 'X86CouInfo.py')
parser.add_argument ('-v', '--verbose', action = 'store_true', help = 'Dump more CPU flags from CPUID.')
parser.add_argument ('-a', '--all', action = 'store_true', help = 'Dump all cores information.')
parser.add_argument ('-c', '--core', type = int, default = 0, help = 'Dump specified cores information.')
args = parser.parse_args ()

def DumpX86CpuInfo (Proc):
  CpuIdSignature  = CpuId.CPUID_SIGNATURE_REGISTERs ()
  Proc.CpuId (CpuId.CPUID_SIGNATURE, 0x00, CpuIdSignature)

  VendorId = bytes((CpuIdSignature.EBX[:] + CpuIdSignature.EDX[:] + CpuIdSignature.ECX[:] )).decode('utf-8')

  VersionInfo = CpuId.CPUID_VERSION_INFO_REGISTERs ()
  Proc.CpuId (CpuId.CPUID_VERSION_INFO, 0x00, VersionInfo)

  BrandString1 = CpuId.CPUID_BRAND_STRING_REGISTERs ()
  Proc.CpuId (CpuId.CPUID_BRAND_STRING1, 0x00, BrandString1)
  BrandString2 = CpuId.CPUID_BRAND_STRING_REGISTERs ()
  Proc.CpuId (CpuId.CPUID_BRAND_STRING2, 0x00, BrandString2)
  BrandString3 = CpuId.CPUID_BRAND_STRING_REGISTERs ()
  Proc.CpuId (CpuId.CPUID_BRAND_STRING3, 0x00, BrandString3)

  ProcessorFreq = CpuId.CPUID_PROCESSOR_FREQUENCY_REGISTERs ()
  Proc.CpuId (CpuId.CPUID_PROCESSOR_FREQUENCY, 0x00, ProcessorFreq)

  BrandString = bytes (BrandString1.EAX.BrandString[:] +
                       BrandString1.EBX.BrandString[:] +
                       BrandString1.ECX.BrandString[:] +
                       BrandString1.EDX.BrandString[:] +
                       BrandString2.EAX.BrandString[:] +
                       BrandString2.EBX.BrandString[:] +
                       BrandString2.ECX.BrandString[:] +
                       BrandString2.EDX.BrandString[:] +
                       BrandString3.EAX.BrandString[:] +
                       BrandString3.EBX.BrandString[:] +
                       BrandString3.ECX.BrandString[:] +
                       BrandString3.EDX.BrandString[:]
                       ).decode('utf-8')

  print (f'== Apic ID: {VersionInfo.EBX.Bits.InitialLocalApicId}')
  print (f'Vendor ID: "{VendorId}"')
  print (f'Brand String: "{BrandString}"')
  print (f'''CPUID: 0x{VersionInfo.EAX.Uint32:05X}
    CPU Type: {VersionInfo.EAX.Bits.ProcessorType:02X}
    CPU Famaly: {(VersionInfo.EAX.Bits.FamilyId + (VersionInfo.EAX.Bits.ExtendedFamilyId << 4)):02X}
    CPU Model: {(VersionInfo.EAX.Bits.Model + (VersionInfo.EAX.Bits.ExtendedModelId << 4)):02X}
    CPU Stepping: {VersionInfo.EAX.Bits.SteppingId:02X}

Base Frequence: {ProcessorFreq.EAX.Bits.ProcessorBaseFrequency} MHz
Maximun Frequence: {ProcessorFreq.EBX.Bits.MaximumFrequency} MHz
Bus Frequences: {ProcessorFreq.ECX.Bits.BusFrequency} MHz
''')

  if args.verbose == False:
    return

  from EfiPy2.Lib.StructDump import DumpStruct

  print ("CPU Version Info...")
  DumpStruct (2, VersionInfo, CpuId.CPUID_VERSION_INFO_REGISTERs)

  print ("Extend Feature 0...")
  ExtendedFeature = CpuId.CPUID_STRUCTURED_EXTENDED_FEATURE_FLAGS_REGISTERs ()
  Proc.CpuId (CpuId.CPUID_STRUCTURED_EXTENDED_FEATURE_FLAGS, 0x00, ExtendedFeature)
  DumpStruct (2, ExtendedFeature, CpuId.CPUID_STRUCTURED_EXTENDED_FEATURE_FLAGS_REGISTERs)

  ExtenedLeafNumber = ExtendedFeature.EAX

  if ExtenedLeafNumber >= 1:
    print ("Extend Feature 1...")
    ExtendedFeature = CpuId.CPUID_STRUCTURED_EXTENDED_FEATURE_FLAGS_SUB_LEAF_1_INFO_REGISTERs ()
    Proc.CpuId (CpuId.CPUID_STRUCTURED_EXTENDED_FEATURE_FLAGS, 0x01, ExtendedFeature)
    DumpStruct (2, ExtendedFeature, CpuId.CPUID_STRUCTURED_EXTENDED_FEATURE_FLAGS_SUB_LEAF_1_INFO_REGISTERs)

  if ExtenedLeafNumber >= 2:
    print ("Extend Feature 2...")
    ExtendedFeature = CpuId.CPUID_STRUCTURED_EXTENDED_FEATURE_FLAGS_SUB_LEAF_2_INFO_REGISTERs ()
    Proc.CpuId (CpuId.CPUID_STRUCTURED_EXTENDED_FEATURE_FLAGS, 0x02, ExtendedFeature)
    DumpStruct (2, ExtendedFeature, CpuId.CPUID_STRUCTURED_EXTENDED_FEATURE_FLAGS_SUB_LEAF_2_INFO_REGISTERs)

  print ()

if __name__ == '__main__':
  print (f'Total {len (X86ProcessorArray)} cores in system.')
  if args.all:
    for Processor in X86ProcessorArray:
      DumpX86CpuInfo (Processor)
  else:
    DumpX86CpuInfo (X86ProcessorArray[args.core])
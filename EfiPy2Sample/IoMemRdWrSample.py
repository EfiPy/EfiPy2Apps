# IoMemRdWrSample.py
#
# Copyright (C) 2026 MaxWu efipy.core@gmail.com All rights reserved.
#
#   GPL-2.0
# 

import EfiPy2 as EfiPy
import EfiPy2.MdePkg.IndustryStandard.Pci as pci
from EfiPy2.Lib.X86Processor import Me
from EfiPy2.Lib.EfiPyPci import GetPciEcam

Me.Iow8 (0x80, 0x22)

Bus  = 0
Dev  = 0
Func = 0
Reg  = 0

BaseReg = GetPciEcam (Bus, Dev, Func)
IoReg   = pci.PCI_CONFIG_ACCESS_CF8((Reg & 0xFC, Func, Dev, Bus, 0, 1))

Me.Iow32 (0xCF8, IoReg.Uint32)

IoRet   = Me.Ior8 (0xCFC)
IdxRet  = Me.IndexDatar8  (0xCF8, 0xCFC, IoReg.Uint32)
BaseRet = Me.MemGet8 (BaseReg)
print (f'0x{IoRet:02X} == 0x{IdxRet:02X}, result: {IoRet == IdxRet}')
print (f'0x{IoRet:02X} == 0x{BaseRet:02X}, result: {IoRet == BaseRet}')

IoRet   = Me.Ior16 (0xCFC)
IdxRet  = Me.IndexDatar16  (0xCF8, 0xCFC, IoReg.Uint32)
BaseRet = Me.MemGet16 (BaseReg)
print (f'0x{IoRet:04X} == 0x{IdxRet:04X}, result: {IoRet == IdxRet}')
print (f'0x{IoRet:04X} == 0x{BaseRet:04X}, result: {IoRet == BaseRet}')

IoRet   = Me.Ior32 (0xCFC)
IdxRet  = Me.IndexDatar32  (0xCF8, 0xCFC, IoReg.Uint32)
BaseRet = Me.MemGet32 (BaseReg)
print (f'0x{IoRet:08X} == 0x{IdxRet:08X}, result: {IoRet == IdxRet}')
print (f'0x{IoRet:08X} == 0x{BaseRet:08X}, result: {IoRet == BaseRet}')

TestValue = EfiPy.UINT32 (0x12345678)
BaseRet = Me.MemGet32 (EfiPy.addressof (TestValue))
print (f'0x{TestValue.value:08X} == 0x{BaseRet:08X}, result: {TestValue.value == BaseRet}')

Me.MemSet32 (EfiPy.addressof (TestValue), 0x87654321)
BaseRet = Me.MemGet32 (EfiPy.addressof (TestValue))
print (f'0x{TestValue.value:08X} == 0x{BaseRet:08X}, result: {TestValue.value == BaseRet}')

Me.MemSet16 (EfiPy.addressof (TestValue), 0xABCD)
BaseRet = Me.MemGet32 (EfiPy.addressof (TestValue))
print (f'0x{TestValue.value:08X} == 0x{BaseRet:08X}, result: {TestValue.value == BaseRet}')

Me.MemSet8 (EfiPy.addressof (TestValue), 0xEF)
BaseRet = Me.MemGet32 (EfiPy.addressof (TestValue))
print (f'0x{TestValue.value:08X} == 0x{BaseRet:08X}, result: {TestValue.value == BaseRet}')
